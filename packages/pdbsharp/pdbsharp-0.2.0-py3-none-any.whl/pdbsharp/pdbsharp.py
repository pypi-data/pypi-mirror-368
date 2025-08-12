# Imports are separated into those needed specifically for attach()
# For easier decoupling if that ever can be removed/simplified
import argparse
from ast import ExceptHandler
import asyncio
from contextlib import ExitStack, closing
import enum
import pdb
import typing

## attach() imports
import os
import sys
import json
import stat
import atexit
import socket
import tempfile
import textwrap
import _colorize

from textual import log
from textual.app import App
from textual.reactive import reactive
from textual.widgets import Input, Log
from textual.worker import Worker, get_current_worker

from .attachedscreen import AttachedScreen
from .detachedscreen import DetachedScreen
from .messages import PdbState, PdbMessageType, MessageFromRepl, MessageToRepl
from .debuginputarea import DebugInputWidget
from .debugresponsearea import DebugResponseArea
from .wrappedclient import WrappedClient


class Pdbsharp(App):
    MODES = {"detached": DetachedScreen, "attached": AttachedScreen}
    DEFAULT_MODE = "detached"

    pdbmode = reactive(PdbState.Unattached)

    def __init__(self, *args, attach_to=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = "pdb#"
        self._client: WrappedClient | None = None
        self._server_pid: int | None = None
        self._exitstack = ExitStack()
        self.command_list: list[str] | None = None

        atexit.register(self._exitstack.close)

        def _close_client():
            if self._client and self._client.server_socket:
                return self._client.server_socket.close
            else:
                return lambda *args, **kwargs: 0

        atexit.register(_close_client)

        self._attach_to = attach_to

        self._current_worker: Worker | None = None
        self._quitting = False
        atexit.register(self.quit)

    def on_message_to_repl(self, message: MessageToRepl) -> None:
        if self._client:
            match message.type:
                case PdbMessageType.COMMAND:
                    self._client._send(reply=message.content)
                case PdbMessageType.INT:
                    self._client.send_interrupt()
                case _:
                    raise ValueError(f"Unknown message type {message.type.name}")

    def on_mount(self):
        if self._attach_to:
            self.attach(self._attach_to)

    def attach(self, pid, commands=()):
        if self.pdbmode in (PdbState.Attached, PdbState.Attaching):
            raise ValueError(f"Already in state {self.pdbmode} and trying to attach()")
        """Attach to a running process with the given PID."""
        """Based on original PdbClient's attach method"""
        self.pdbmode = PdbState.Attaching
        server = self._exitstack.enter_context(
            closing(socket.create_server(("localhost", 0)))
        )

        port = server.getsockname()[1]

        connect_script = self._exitstack.enter_context(
            tempfile.NamedTemporaryFile("w", delete_on_close=False)
        )

        use_signal_thread = sys.platform == "win32"
        colorize = _colorize.can_colorize()

        connect_script.write(
            textwrap.dedent(
                f"""
                import pdb, sys
                pdb._connect(
                    host="localhost",
                    port={port},
                    frame=sys._getframe(1),
                    commands={json.dumps("\n".join(commands))},
                    version={pdb._PdbServer.protocol_version()},
                    signal_raising_thread={use_signal_thread!r},
                    colorize={colorize!r},
                )
                """
            )
        )
        connect_script.close()
        orig_mode = os.stat(connect_script.name).st_mode
        os.chmod(connect_script.name, orig_mode | stat.S_IROTH | stat.S_IRGRP)
        try:
            sys.remote_exec(pid, connect_script.name)
        except RuntimeError:
            # showwarning("Pid does not match python process")
            self.query_one(Input).value = ""
            self.query_one(
                Input
            ).placeholder = "PID does not match a valid python process"
            self._exitstack.close()
            self.pdbmode = PdbState.Unattached
            return

        self.query_one(Input).placeholder = "Remote Process PID"

        # TODO Add a timeout? Or don't bother since the user can ^C?
        client_sock, _ = server.accept()
        self._exitstack.enter_context(closing(client_sock))

        if use_signal_thread:
            interrupt_sock, _ = server.accept()
            self._exitstack.enter_context(closing(interrupt_sock))
            interrupt_sock.setblocking(False)
        else:
            interrupt_sock = None

        # Dropped the call to cmdloop() at the end of this
        self._client = WrappedClient(self, pid, client_sock, interrupt_sock)

        self._server_pid = pid
        self.pdbmode = PdbState.Attached
        self.switch_mode("attached")
        self._current_worker = self.run_worker(self.update_buffer, thread=True)

        self._exitstack.push(self._detach_and_close)

    def _detach_and_close(self, *args):
        if not self.pdbmode in (PdbState.Attached,):
            raise ValueError(f"Tried to detach while in state {self.pdbmode}")
        if self._client:
            self._client._send(signal="INT")
        self._exitstack.close()

    def detach(self, *args):
        self._detach_and_close()
        if self._screen_stack:
            self.screen.query_one(DebugResponseArea).clear()
        self._client = None
        self.pdbmode = PdbState.Unattached
        self.switch_mode("detached")

    async def update_buffer(self, prewait=0.25):
        if self._quitting:
            return

        while not self._client:
            if self._quitting:
                return
            await asyncio.sleep(0.25)

        await asyncio.sleep(prewait)
        log("About to _readline")
        while not get_current_worker().is_cancelled and not self._quitting:
            res = self._client._readline()
            if res:
                self.screen.post_message(MessageFromRepl(res.decode("utf-8")))

    def quit(self):
        self._quitting = True
        if self._client:
            self._client._send(signal="INT")
        if self._current_worker:
            self._current_worker.cancel()
        # if self._loop: self._loop.shutdown_default_executor(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--pid", type=int, help="The PID of a Python process to connect to"
    )

    args = parser.parse_args()

    app = Pdbsharp(attach_to=args.pid)
    app.run()


if __name__ == "__main__":
    main()

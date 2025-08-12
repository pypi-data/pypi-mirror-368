from os import getpid
from textwrap import shorten
from typing import TYPE_CHECKING, TypedDict, cast

import psutil
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, OptionList, TextArea
from textual.widgets.option_list import Option

from .messages import PdbState

if TYPE_CHECKING:
    from .pdbsharp import Pdbsharp


class ProcessInfo(TypedDict):
    name: str
    pid: str
    cmdline: list[str] | None


class DetachedScreen(Screen):
    CSS_PATH = "detachedscreen.tcss"

    def compose(self) -> ComposeResult:
        self.app: Pdbsharp
        self.sub_title = f"{self.app.pdbmode.name}"
        yield Header()
        with Vertical(id="content"):
            yield Label(
                "Enter the PID of a running Python process to debug:",
                id="intro",
            )
            yield Input(
                "", placeholder="Remote Process PID", type="integer", id="remote-pid"
            )
            info = self.get_python_processes()
            options = [
                Option(
                    f"{p['pid']: <10}{shorten(p['name'], 10): <11}{shorten(p['cmdline'][-1] if p['cmdline'] else '', self.app.size.width - 30)}"
                )
                for p in info
            ]
            yield Label(
                "Or select an existing process:\n[grey][showing processes matching 'python3'][/grey]"
            )
            yield ProcessOptionList(
                *options, id="processes", compact=(len(options) > 10)
            )
        yield Footer()

    def user_attach(self, pid, commands=()):
        # When the PID is provided by the user or another input, pass it through the validation here instead of calling app.attach directly
        match self.app.pdbmode:
            case PdbState.Unattached:
                pid = int(pid)
                self.app.attach(pid)
            case _:
                ...
                # showwarning "Invalid mode for input commands

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.log(f"Input submitted in mode {self.app.pdbmode.name}")
        if event.input.value:
            self.user_attach(event.input.value)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        prompt = cast(str, event.option.prompt)
        pid, _, _ = prompt.partition(" ")
        self.user_attach(int(pid))

    def get_python_processes(self) -> list[ProcessInfo]:
        process_info: list[ProcessInfo] = []
        wanted = ("pid", "name", "cmdline")
        ignored_command_strings = (
            ".vscode/extensions",  # If developing in VS code, Pylance and the language server create a bunch of processes
            "pylance",
        )
        for p in psutil.process_iter():
            data: ProcessInfo = p.as_dict(attrs=wanted)
            # Heuristics for which processes to show are in this conditional
            if (
                (
                    data["cmdline"] and any("python" in cmd for cmd in data["cmdline"])
                )  # 'python' in the command line invocation
                and not int(data["pid"]) == getpid()  # Don't list our own process
                and not any(
                    s in cmd for cmd in data["cmdline"] for s in ignored_command_strings
                )  # Anything with a forbidden string is ignored
            ):
                process_info.append(data)
        return process_info


class ProcessOptionList(OptionList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.highlighted = None

    def on_focus(self, event):
        self.highlighted = 0

import enum

from textual.message import Message


class PdbState(enum.Enum):
    Unattached = enum.auto()
    Attached = enum.auto()
    Attaching = enum.auto()


class PdbMessageType(enum.Enum):
    COMMAND = enum.auto()
    EOF = enum.auto()
    INT = enum.auto()


class MessageToRepl(Message):
    def __init__(self, type: PdbMessageType, content: str | None = None) -> None:
        self.type = type
        self.content = content
        super().__init__()


class MessageFromRepl(Message):
    def __init__(self, text):
        self.text = text
        super().__init__()

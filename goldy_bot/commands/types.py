from enum import Enum

__all__ = (
    "CommandType",
)

class CommandType(Enum):
    def __init__(self, value: int) -> None:
        ...

    SLASH = 1
    """The typical slash commands we all know and love... or maybe not..."""
    USER = 2
    """A UI-based command that shows up when you right click or tap on a user."""
    MESSAGE = 3
    """A UI-based command that shows up when you right click or tap on a message."""
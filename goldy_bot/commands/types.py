from enum import Enum

__all__ = (
    "CommandType",
)

class CommandType(Enum):
    def __init__(self, value: int) -> None:
        ...

    SLASH = 2
    """The typical slash commands we all know and love... or maybe not..."""
    MESSAGE = 3
    AUTO_COMPLETE = 4
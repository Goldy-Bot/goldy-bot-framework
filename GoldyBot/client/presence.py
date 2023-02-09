from enum import Enum

class Status(Enum):
    """Goldy Bot enum class of nextcore status."""
    ONLINE = "online"
    IDLE = "idle"
    DND = "dnd"
    INVISIBLE = "invisible"
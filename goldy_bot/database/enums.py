from enum import Enum

__all__ = (
    "DatabaseEnums",
)

class DatabaseEnums(Enum):
    """Enum class that holds the names for all goldy bot mongo databases and collection types."""
    GOLDY_MAIN = "goldy_main"
    GOLDY_MEMBER_DATA = "goldy_member_data"

    def __init__(self, database_name: str):
        ...
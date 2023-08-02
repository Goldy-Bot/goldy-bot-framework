from enum import Enum

class Perms(Enum):
    """Goldy Bot's built-in permissions."""
    BOT_DEV = 0
    BOT_ADMIN = 1

    GUILD_OWNER = 2
    GUILD_ADMIN = 3
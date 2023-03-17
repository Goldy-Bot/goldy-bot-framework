from enum import Enum

class Perms(Enum):
    """Goldy Bot's built-in perms."""
    BOT_DEV = "bot_dev"
    BOT_ADMIN = "bot_admin"

    def __str__(self) -> str:
        return str(self.value)
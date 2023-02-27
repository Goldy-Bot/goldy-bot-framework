from .. import Goldy
from ...errors import GoldyBotError

# TODO: Finish this and import it in goldy/__init__.py.

class Guilds():
    def __init__(self, goldy:Goldy) -> None:
        self.allowed_guilds = goldy.config.allowed_guilds

        if self.allowed_guilds == []:
            raise AllowedGuildsNotSpecified()

    def setup(self):
        """Adds guilds specified in goldy.json to the database if not already added."""
        ...


# Exceptions
# ------------
class AllowedGuildsNotSpecified(GoldyBotError):
    def __init__(self):
        super().__init__(
            "Please add your guild id to the allowed_guilds in goldy.json"
        )
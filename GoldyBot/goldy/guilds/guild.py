from __future__ import annotations

from typing import TYPE_CHECKING
from discord_typings import GuildData

from devgoldyutils import DictClass, LoggerAdapter, Colours

from ... import goldy_bot_logger
from ..database.wrappers.guild import GuildDBWrapper

if TYPE_CHECKING:
    from .. import Goldy
    from ... import Extension

class Guild(DictClass):
    """A goldy bot guild class."""
    def __init__(self, id: str, code_name:str, data: GuildData, goldy: Goldy) -> None:
        self.id = id
        """The guild's discord id"""
        self.code_name = code_name
        """The goldy bot code name of the guild."""
        self.data = data
        self.goldy = goldy

        self.logger = LoggerAdapter(
            LoggerAdapter(goldy_bot_logger, prefix = "Guild"), 
            prefix = Colours.PINK_GREY.apply(data["name"])
        )

        self.config_wrapper = GuildDBWrapper(self)

        super().__init__(self.logger)

    @property
    async def config(self) -> GuildDBWrapper:
        """Returns the guild's database wrapper for it's configuration."""
        if self.config_wrapper.data == {}:
            await self.config_wrapper.update()

        return self.config_wrapper

    async def is_extension_allowed(self, extension: Extension) -> bool:
        """Returns True/False if this extension is allowed to function in this guild."""
        guild_config = await self.config
        disallowed_extensions = [ext.lower() for ext in guild_config.disallowed_extensions]

        if extension.name.lower() in [x.lower() for x in ["Goldy", "GuildAdmin"]]: # These extensions are always allowed.
            return True

        if extension.name.lower() in disallowed_extensions:
            return False

        if len(disallowed_extensions) > 0:

            if disallowed_extensions[0] == "." and extension.name.lower() not in [ext.lower() for ext in guild_config.allowed_extensions]:
                return False

        return True
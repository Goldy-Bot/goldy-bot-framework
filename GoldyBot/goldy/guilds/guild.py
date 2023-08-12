from __future__ import annotations

from typing import TYPE_CHECKING
from discord_typings import GuildData

from devgoldyutils import DictClass, LoggerAdapter, Colours

from ... import goldy_bot_logger
from ..database.wrappers.guild import GuildDBWrapper

if TYPE_CHECKING:
    from ... import Extension
    from .. import Goldy, objects

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

        if extension.name.lower() in ["goldy", "guildadmin"]: # These extensions are always allowed.
            return True

        if extension.name.lower() in disallowed_extensions:
            return False

        if len(disallowed_extensions) > 0:

            if disallowed_extensions[0] == "." and extension.name.lower() not in [ext.lower() for ext in guild_config.allowed_extensions]:
                return False

        return True

    async def do_extension_restrictions_pass(self, extension: Extension, platter: objects.GoldPlatter) -> bool:
        """Checks if extension's restrictions pass."""
        guild_config = await self.config
        extension_restriction = guild_config.get("extensions", "restrictions", extension.name)

        if extension_restriction is not None:
            role = guild_config.roles.get(extension_restriction)
            channel = guild_config.channels.get(extension_restriction)

            if channel is not None and channel == str(platter.data["channel_id"]):
                return True

            if role is not None:
                member_data = await platter.author.member_data

                for role_id in member_data["roles"]:
                    if role == str(role_id):
                        return True

            return False

        return True
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from goldy_bot.goldy import Goldy

import asyncio
from devgoldyutils import Colours, LoggerAdapter

import GoldyBot
from GoldyBot.goldy.token import Token
from GoldyBot.goldy import (
    Goldy as LegacyGoldy, 
    cache as legacy_cache, 
    GoldyConfig as LegacyGoldyConfig,
    Database as LegacyDatabase, 
    Presence as LegacyPresence, 
    System as LegacySystem, 
    CommandLoader as LegacyCommandLoader, 
    CommandListener as LegacyCommandListener, 
    ExtensionLoader as LegacyExtensionLoader, 
    GuildManager as LegacyGuildManager, 
    PermissionSystem as LegacyPermissionSystem
)
from GoldyBot.logging import goldy_bot_logger as legacy_gbot_logger

import goldy_bot
from .wrapper import Wrapper
from ...logger import goldy_bot_logger

__all__ = (
    "LegacyWrapper",
)

# NOTE: All the stuff you are seeing here is for pre-pancake legacy support. DO NOT TOUCH ANY OF THIS from the pancake API!

class GoldyConfigTranslationLayer(LegacyGoldyConfig):
    def __init__(self, goldy: Goldy):
        self.logger = LoggerAdapter(goldy_bot_logger, prefix = "GoldyConfigTranslationLayer")

        pancake_config = goldy.config

        self.json_data: dict = {
            "goldy": {
                "branding": {
                    "name": pancake_config.branding_name
                },
                "extensions": {
                    "repos": pancake_config.repos,
                    "include": pancake_config.included_extensions,
                    "ignored_extensions": pancake_config.ignored_extensions,
                    "late_load_extensions": [],
                    "raise_on_load_error": pancake_config.extensions_raise_on_load_error,
                    "folder_location": pancake_config.extensions_directory
                },
                "bot_dev": pancake_config.developer_id
            }
        }

        test_guild_id = pancake_config.test_guild_id

        if test_guild_id is not None:
            self.json_data["goldy"]["allowed_guilds"] = {
                f"{test_guild_id}": "test_server"
            }

class LegacyWrapper(Wrapper):
    """Wraps some attributes from the legacy goldy class for the new 🥞 pancake one."""
    def __init__(self, goldy: Goldy) -> None:
        self.__goldy = goldy

        # Hijack old logger to present it self as the legacy goldy bot api.
        legacy_gbot_logger.name = Colours.GREY.apply("Legacy API")
        GoldyBot.info.VERSION = goldy_bot.__version__
        super().__init__(goldy)

    async def _legacy_setup(self) -> None:
        """Legacy support method. Do not use!"""

        def __legacy_init_interceptor(goldy_self: LegacyGoldy):
            bot_authentication = self.__goldy.shard_manager.authentication
            database_url = self.__goldy.database.url

            goldy_self.token = Token(bot_authentication.token, database_url)
            goldy_self.logger = LoggerAdapter(legacy_gbot_logger, Colours.ORANGE.apply_to_string("Goldy"))
            goldy_self.async_loop = asyncio.get_event_loop()

            goldy_self.nc_authentication = bot_authentication
            goldy_self.intents = 1 << 9 | 1 << 15 | 1 << 7 | 1 << 0

            goldy_self.http_client = self.__goldy.http_client
            goldy_self.shard_manager = self.__goldy.shard_manager

            goldy_self.start_up_time = self.__goldy.boot_datetime

            goldy_self.pre_invokables = set()
            goldy_self.invokables = set()

            goldy_self.bot_user = None
            goldy_self.application_data = None

            legacy_cache["goldy_core_instance"] = goldy_self

            def __legacy_database_interceptor(db_self: LegacyDatabase):
                db_self.goldy = goldy_self
                db_self.logger = LoggerAdapter(legacy_gbot_logger, prefix = "Database")
                db_self.client = self.__goldy.database._client

            LegacyDatabase.__init__ = __legacy_database_interceptor

            goldy_self.config = GoldyConfigTranslationLayer(self)
            goldy_self.database = LegacyDatabase()
            goldy_self.presence = LegacyPresence(goldy_self)
            goldy_self.system = LegacySystem(goldy_self)
            goldy_self.command_loader = LegacyCommandLoader(goldy_self)
            goldy_self.command_listener = LegacyCommandListener(goldy_self)
            goldy_self.extension_loader = LegacyExtensionLoader(goldy_self)
            goldy_self.guild_manager = LegacyGuildManager(goldy_self)
            goldy_self.permission_system = LegacyPermissionSystem(goldy_self)

        LegacyGoldy.__init__ = __legacy_init_interceptor

        legacy_goldy = LegacyGoldy()

        await legacy_goldy.pre_setup()
        await legacy_goldy.setup()


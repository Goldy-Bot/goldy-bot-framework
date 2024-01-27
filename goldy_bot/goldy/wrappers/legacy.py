from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List, Tuple
    from typing_extensions import Self
    from discord_typings import ApplicationCommandPayload, ApplicationCommandData

    from ..goldy import Goldy
    from ...typings import GoldySelfT

    from GoldyBot.goldy.commands import slash_command

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
    PermissionSystem as LegacyPermissionSystem,
    Member as LegacyMember
)
from GoldyBot.logging import goldy_bot_logger as legacy_gbot_logger

import goldy_bot
from ...logger import goldy_bot_logger

__all__ = (
    "Legacy",
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

class Legacy():
    """Wraps some attributes from the legacy goldy class for the new 🥞 pancake one."""
    def __init__(self) -> None:
        legacy_gbot_logger.setLevel(goldy_bot_logger.level)
        GoldyBot.info.VERSION = goldy_bot.__version__

        self.__legacy_goldy: Optional[LegacyGoldy] = None

        super().__init__()

    def _initialize_legacy_goldy(self: GoldySelfT[Self]):
        """Do not use this method! Initializes legacy API goldy class."""

        def __legacy_init_interceptor(goldy_self: LegacyGoldy):
            bot_authentication = self.shard_manager.authentication
            database_url = self.database.url

            goldy_self.token = Token(bot_authentication.token, database_url)
            goldy_self.logger = LoggerAdapter(legacy_gbot_logger, Colours.ORANGE.apply_to_string("Goldy"))
            goldy_self.async_loop = asyncio.get_event_loop()

            goldy_self.nc_authentication = bot_authentication
            goldy_self.intents = 1 << 9 | 1 << 15 | 1 << 7 | 1 << 0

            goldy_self.http_client = self.client
            goldy_self.shard_manager = self.shard_manager

            goldy_self.start_up_time = self.boot_datetime

            goldy_self.pre_invokables = set()
            goldy_self.invokables = set()

            goldy_self.bot_user = None
            goldy_self.application_data = None

            legacy_cache["goldy_core_instance"] = goldy_self

            def __legacy_database_interceptor(db_self: LegacyDatabase):
                db_self.goldy = goldy_self
                db_self.logger = LoggerAdapter(legacy_gbot_logger, prefix = "Database")
                db_self.client = self.database._client

            LegacyDatabase.__init__ = __legacy_database_interceptor

            async def __batch_create_interactions(
                cmd_loader_self: LegacyCommandLoader, 
                slash_commands_to_register: List[slash_command.SlashCommand], 
                slash_command_payloads: List[ApplicationCommandPayload], 
                testing_server: Tuple[str, str] | None
            ) -> None:
                created_interaction_cmds: List[ApplicationCommandData] = []

                # Creating global commands.
                # --------------------------
                if testing_server is None:
                    created_interaction_cmds += await self.low_level.create_application_commands(
                        slash_command_payloads
                    )

                    cmd_loader_self.logger.debug("Created global commands.")

                # Creating guild commands for testing server.
                # --------------------------------------------
                else:
                    # Adding test warning to all slash commands for the test server.
                    for payload in slash_command_payloads:
                        test_description = "⚒️ THIS IS A TEST COMMAND REGISTERED JUST FOR THIS GUILD"
                        
                        # Setting test description to all first layer sub commands.
                        for option in payload["options"]:
                            if not option["type"] == 1:
                                continue

                            option["description"] = test_description

                        payload["description"] = test_description

                    created_interaction_cmds += await self.low_level.create_application_commands(
                        slash_command_payloads, guild_id = testing_server[0]
                    )

                    cmd_loader_self.logger.debug("Created guild commands for test server.")

                # Registering slash commands with the id given by discord.
                # ----------------------------------------------------------
                for interaction_cmd in created_interaction_cmds:

                    for command in slash_commands_to_register:

                        if command.name == interaction_cmd["name"]:

                            if interaction_cmd.get("guild_id") is not None:
                                command.register(f"{interaction_cmd.get('guild_id')}:{interaction_cmd['id']}")
                            else:
                                command.register(f"{interaction_cmd['id']}")

                            break

                return None

            LegacyCommandLoader._CommandLoader__batch_create_interactions = __batch_create_interactions

            # Emptying the load and pull method as it should no longer be used.
            LegacyExtensionLoader.load = lambda x: None
            LegacyExtensionLoader.pull = lambda x: None

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

        self.__legacy_goldy = LegacyGoldy()

    async def _legacy_setup(self: GoldySelfT[Self]) -> None:
        """Do not use this method! Runs legacy API setup routine."""
        if self.__legacy_goldy is not None:
            bot_user_data = await self.low_level.get_bot_user_data(bucket_priority = 1)

            self.__legacy_goldy.application_data = await self.low_level.get_application_data()
            self.__legacy_goldy.bot_user = LegacyMember(bot_user_data, None, self.__legacy_goldy)

            await self.__legacy_goldy.setup()
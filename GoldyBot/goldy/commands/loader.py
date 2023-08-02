from __future__ import annotations
from typing import List, overload, Tuple
from discord_typings import ApplicationCommandPayload, ApplicationCommandData

from nextcore.http import Route

from .. import Goldy
from . import slash_command
from .command import Command
from ... import goldy_bot_logger, LoggerAdapter

class CommandLoader():
    """Class that handles command loading."""
    def __init__(self, goldy:Goldy) -> None:
        self.goldy = goldy

        self.logger = LoggerAdapter(goldy_bot_logger, prefix="CommandLoader")

    @overload
    async def load(self) -> None:
        """Loads all commands that have been initialized in goldy bot."""
        ...

    @overload
    async def load(self, commands:List[Command]) -> None:
        """Loads each command in this list."""
        ...

    async def load(self, commands: List[Command] = None) -> None:
        """Loads/creates all commands that have been initialized in goldy bot."""
        self.logger.info("Loading and registering commands...")
        if commands is None:
            commands = [x for x in self.goldy.pre_invokables if isinstance(x, Command)]

        slash_command_payloads: List[ApplicationCommandPayload] = []

        for command in commands:

            if command.extension is None: # If the extension doesn't exist don't load this command.
                self.logger.warn(
                    f"Not loading command '{command.name}' because the extension '{command.extension_name}' is being ignored or has failed to load!"
                )
                continue

            command.extension.commands.append(command)

            if isinstance(command, slash_command.SlashCommand):
                slash_command_payloads.append(dict(command))
                self.logger.debug(f"Slash command '{command.name}' payload grabbed.")
            else:
                command.register(command.name) # Registering prefix commands with their command name.

            command._is_loaded = True

            command.logger.debug("Command loaded.")

        slash_commands_to_register = [x for x in self.goldy.pre_invokables if isinstance(x, slash_command.SlashCommand)]


        # Grab testing server.
        testing_server = None
        for guild in self.goldy.guild_manager.allowed_guilds:
            if not guild[1] == "test_server":
                continue

            testing_server = guild
            break

        await self.__batch_create_interactions(
            slash_commands_to_register = slash_commands_to_register,
            slash_command_payloads = slash_command_payloads,
            testing_server = testing_server
        )

        self.logger.info("All commands loaded!")

        return None
    
    async def __batch_create_interactions(
        self, 
        slash_commands_to_register: List[slash_command.SlashCommand], 
        slash_command_payloads: List[ApplicationCommandPayload], 
        testing_server: Tuple[str, str] | None
    ) -> None:
        created_interactions: List[ApplicationCommandData] = []

        # Creating global commands.
        # --------------------------
        global_route = Route(
            "PUT",
            "/applications/{application_id}/commands",
            application_id = self.goldy.application_data["id"]
        )
        
        r = await self.goldy.http_client.request(
            global_route,
            rate_limit_key = self.goldy.nc_authentication.rate_limit_key,
            headers = self.goldy.nc_authentication.headers,
            json = slash_command_payloads
        )

        created_interactions += await r.json()
        self.logger.debug("Created global commands.")


        # Creating guild commands for testing server.
        # --------------------------------------------
        if testing_server is not None:
            testing_guild_route = Route(
                "PUT",
                "/applications/{application_id}/guilds/{guild_id}/commands",
                application_id = self.goldy.application_data["id"],
                guild_id = testing_server[0],
            )

            # Adding test warning to all slash commands for the test server.
            for payload in slash_command_payloads:
                test_description = "⚒️ THIS IS A TEST COMMAND REGISTERED JUST FOR THIS GUILD"
                
                # Setting test description to all first layer sub commands.
                for option in payload["options"]:
                    if not option["type"] == 1:
                        continue

                    option["description"] = test_description

                payload["description"] = test_description

            # Creating guild commands for testing server.
            r = await self.goldy.http_client.request(
                testing_guild_route,
                rate_limit_key = self.goldy.nc_authentication.rate_limit_key,
                headers = self.goldy.nc_authentication.headers,
                json = slash_command_payloads
            )

            created_interactions += await r.json()

            self.logger.debug("Created guild commands for test server.")


        # Registering slash commands with the id given by discord.
        # ----------------------------------------------------------
        for interaction in created_interactions:

            for command in slash_commands_to_register:

                if command.name == interaction["name"]:

                    if interaction.get("guild_id") is not None:
                        command.register(f"{interaction.get('guild_id')}:{interaction['id']}")
                    else:
                        command.register(f"{interaction['id']}")

                    break

        return None
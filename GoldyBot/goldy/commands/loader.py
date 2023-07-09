from __future__ import annotations
from typing import List, overload
from discord_typings import ApplicationCommandPayload

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

        # Create slash commands for each allowed guild.
        # ----------------------------------------------
        for guild in self.goldy.guild_manager.allowed_guilds:

            r = await self.goldy.http_client.request(
                Route(
                    "PUT",
                    "/applications/{application_id}/guilds/{guild_id}/commands",
                    application_id = self.goldy.application_data["id"],
                    guild_id = guild[0],
                ),
                rate_limit_key = self.goldy.nc_authentication.rate_limit_key,
                headers = self.goldy.nc_authentication.headers,
                json = slash_command_payloads
            )

            registered_interactions = await r.json()

            # Registering slash commands with the id given by discord.
            for interaction in registered_interactions:

                for command in slash_commands_to_register:

                    if command.name == interaction["name"]:
                        command.register(f"{guild[0]}:{interaction['id']}")
                        break

            self.logger.debug(f"Created slash cmds for guild '{guild[1]}'.")

        self.logger.info("All commands loaded!")

        return None
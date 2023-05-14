from __future__ import annotations
from typing import List, overload, TYPE_CHECKING
from discord_typings import ApplicationCommandPayload

from nextcore.http import Route

from .. import Goldy
from ... import goldy_bot_logger, LoggerAdapter
from . import commands_cache

if TYPE_CHECKING:
    from . import Command

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

    async def load(self, commands:List[Command] = None) -> None:
        """Loads/creates all commands that have been initialized in goldy bot."""
        if commands is None:
            commands = [x[1] for x in commands_cache]

        slash_command_payloads: List[ApplicationCommandPayload] = []

        for command in commands:

            if command.extension is None: # If the extension doesn't exist don't load this command.
                self.logger.warn(
                    f"Not loading command '{command.name}' because the extension '{command.extension_name}' is being ignored or has failed to load!"
                )
                continue

            command.extension.commands.append(command)

            if command.allow_slash_cmd:
                slash_command_payloads.append(command.slash_cmd_payload)

            command.__loaded = True

            self.logger.debug(
                f"Command '{command.name}' loaded and slash cmd payload grabbed."
            )


        # Create slash commands for each allowed guild.
        # ----------------------------------------------
        for guild in self.goldy.guild_manager.allowed_guilds:

            # TODO: Get the application objects from this response and save it in the guild. Also add a method in command object to retrieve it.
            await self.goldy.http_client.request(
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

            self.logger.debug(f"Created slash cmds for guild '{guild[1]}'.")

        self.logger.info("All commands loaded!")

        return None
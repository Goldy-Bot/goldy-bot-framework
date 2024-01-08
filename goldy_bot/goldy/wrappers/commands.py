from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

    from ...commands import Command

    from ...typings import GoldySelfT

from devgoldyutils import LoggerAdapter, Colours

from ...logger import goldy_bot_logger

__all__ = (
    "Commands",
)

logger = LoggerAdapter(
    goldy_bot_logger, prefix = "Commands"
)

class Commands():
    """Brings valuable methods to the goldy class for managing loading and syncing of commands."""
    def __init__(self) -> None:
        super().__init__()

    async def _sync_commands(self: GoldySelfT) -> None:
        """
        Registers all the commands from each extension in goldy bot's internal state with discord if not registered already.
        Also removes commands from discord that are no longer registered within the framework.
        """
        commands_to_register: List[Command] = []

        for extension in self.extensions:

            for commands in extension._commands.values():
                commands_to_register.extend(commands)

        test_guild_id = self.config.test_guild_id

        registered_commands = await self.create_application_commands(
            payload = [command.payload for command in commands_to_register], 
            guild_id = test_guild_id
        )

        logger.info(
            Colours.GREEN.apply(str(len(registered_commands))) + " command(s) have been registered with discord!"
        )
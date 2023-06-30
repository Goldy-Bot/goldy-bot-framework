from __future__ import annotations
from typing import Any, Callable, Dict, List, TYPE_CHECKING
from discord_typings import ApplicationCommandOptionData, InteractionData

from devgoldyutils import Colours

from .. import objects

if TYPE_CHECKING:
    from .. import Goldy, objects
    from ... import Extension

import params_utils
from .command import Command

class SlashCommand(Command):
    def __init__(
        self, 
        goldy: Goldy, 
        func: Callable[[Extension, objects.GoldPlatter], Any], 
        name: str, 
        description: str, 
        required_roles: List[str], 
        slash_options: Dict[str, ApplicationCommandOptionData], 
        hidden: bool
    ):
        super().__init__(
            goldy, 
            func, 
            name, 
            description, 
            required_roles, 
            slash_options, 
            hidden
        )

    async def invoke(self, platter: objects.GoldPlatter) -> None:
        """Runs and triggers a slash command. This method is usually ran internally."""
        data: InteractionData = platter.data

        self.logger.info(
            Colours.CLAY.apply(
                f"Slash command invoked by '{platter.author.username}#{platter.author.discriminator}'."
            )
        )

        params = params_utils.invoke_data_to_params(data, platter)
        if not params == []: self.logger.debug(f"Got args --> {params}")

        super().invoke(
            platter, lambda: await self.func(platter.command.extension, platter, **params)
        )

        # TODO: When exceptions raise in commands wrap them in a goldy bot command exception.
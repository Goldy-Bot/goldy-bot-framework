from __future__ import annotations
from typing import Any, Callable, Dict, List, TYPE_CHECKING
from discord_typings import ApplicationCommandOptionData, InteractionData

from devgoldyutils import Colours

from .. import objects
from ..nextcore_utils import front_end_errors

if TYPE_CHECKING:
    from .. import Goldy, objects

import params_utils
from .command import Command

class SlashCommand(Command):
    def __init__(
        self, 
        goldy: Goldy, 
        func: Callable[[objects.GoldPlatter], Any], 
        name: str, 
        description: str, 
        required_roles: List[str], 
        slash_options: Dict[str, ApplicationCommandOptionData], 
        allow_prefix_cmd: bool, 
        hidden: bool
    ):
        super().__init__(
            goldy, 
            func, 
            name, 
            description, 
            required_roles, 
            slash_options, 
            allow_prefix_cmd, 
            hidden
        )

    async def invoke(self, platter: objects.GoldPlatter) -> None:
        """Runs and triggers a slash command. This method is usually ran internally."""

        data: InteractionData = platter.data

        self.logger.info(
            Colours.CLAY.apply(
                f"Slash command invoked by '{data['member']['user']['username']}#{data['member']['user']['discriminator']}'."
            )
        )

        params = params_utils.invoke_data_to_params(data, platter)
        if not params == []: self.logger.debug(f"Got args --> {params}")

        # Run callback.
        # --------------
        return_value = await self.func(self.extension, gold_platter, **params)

        # Invoke sub command if there is one in invoke data.
        if return_value is not False and self.is_parent is True:
            await self.__invoke_sub_cmd(data, gold_platter)

        return True

        # If member has no perms raise MissingPerms exception.
        raise front_end_errors.MissingPerms(gold_platter, self.logger)
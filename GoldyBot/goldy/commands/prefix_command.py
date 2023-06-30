from __future__ import annotations
from typing import Any, Callable, Dict, List, TYPE_CHECKING
from discord_typings import ApplicationCommandOptionData, InteractionData

from devgoldyutils import Colours

from .. import objects
from ..nextcore_utils import front_end_errors

if TYPE_CHECKING:
    from .. import Goldy, objects
    from ... import Extension

import params_utils
from .command import Command

class PrefixCommand(Command):
    def __init__(
        self, 
        goldy: Goldy, 
        func: Callable[[Extension, objects.GoldPlatter], Any], 
        name: str, 
        description: str, 
        required_roles: List[str], 
        hidden: bool
    ):
        super().__init__(
            goldy, 
            func, 
            name, 
            description, 
            required_roles, 
            [],
            hidden
        )

    @property
    def command_usage(self) -> str:
        command_args_string = " "
        for param in self.params:
            command_args_string += f"{{{param}}} "

        command_sub_cmds_string = "<"
        for sub_cmd in self.sub_commands:
            command_sub_cmds_string += f"{sub_cmd[0]}|"

        if len(command_sub_cmds_string) >= 2:
            command_sub_cmds_string = command_sub_cmds_string[:-1] + "> "

        return f"{self.parent_cmd.name + ' ' if self.is_child else ''}{self.name} {command_args_string[:-1]}{command_sub_cmds_string[:-1]}"

    async def invoke(self, platter: objects.GoldPlatter) -> None:
        """Runs and triggers a slash command. This method is usually ran internally."""
        data: InteractionData = platter.data

        self.logger.info(
            Colours.BLUE.apply(
                f"Prefix command invoked by '{platter.author.username}#{platter.author.discriminator}'."
            )
        )

        params = params_utils.invoke_data_to_params(data, platter)
        if not params == []: self.logger.debug(f"Got args --> {params}")

        try:
            super().invoke(
                platter, lambda: await self.func(platter.command.extension, platter, **params)
            )

        except TypeError as e:
            # This could mean the args are missing or it could very well be a normal type error so let's check and handle it respectively.
            if f"{self.func.__name__}() missing" in e.args[0]:
                # If params are missing raise MissingArgument exception.
                raise front_end_errors.MissingArgument(
                    missing_args = self.params[len(params):], 
                    platter = platter, 
                    logger = self.logger
                )

            # The or condition is here because of newer python versions.
            if f"{self.func.__name__}() takes" in e.args[0] or f"{self.extension_name}.{self.func.__name__}() takes" in e.args[0]:
                raise front_end_errors.TooManyArguments(
                    platter = platter, 
                    logger = self.logger
                )
            
            # TODO: When exceptions raise in commands wrap them in a goldy bot command exception.
            raise e
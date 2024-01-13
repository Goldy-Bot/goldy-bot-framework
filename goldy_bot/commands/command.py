from __future__ import annotations
from typing import TYPE_CHECKING

from discord_typings import ApplicationCommandPayload

if TYPE_CHECKING:
    from typing import Optional, Dict, List
    from discord_typings import ApplicationCommandOptionData

    from .slash_option import SlashOption
    from ..typings import CommandFuncT

import regex
from devgoldyutils import LoggerAdapter

from .types import CommandType
from ..helpers.helper import DictHelper
from ..errors import GoldyBotError
from ..logger import goldy_bot_logger

__all__ = (
    "Command",
)

class Command(DictHelper[ApplicationCommandPayload]):
    def __init__(
        self,
        function: CommandFuncT,
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        slash_options: Optional[Dict[str, SlashOption]] = None, 
        wait: bool = False
    ) -> None:
        self.function = function

        name = name or function.__name__
        # Even though discord docs say no, description is a required field.
        description = description or "🪹 Oopsie daisy, looks like no description was set for this command." 

        data = {}
        data["type"] = CommandType.SLASH.value
        data["name"] = name
        data["description"] = description

        if slash_options is not None:
            data["options"] = self.__options_parser(function, slash_options)

        self.wait = wait

        self._slash_options = slash_options
        self._subcommands: List[Command] = []

        self.logger = LoggerAdapter(
            LoggerAdapter(goldy_bot_logger, prefix = "Command"), prefix = name
        )

        super().__init__(data)

    @property
    def name(self) -> str:
        """The command's name."""
        return self.data["name"]

    @property
    def description(self) -> str:
        """The command's description."""
        return self.data["description"]

    def add_subcommand(self, command: Command) -> None:
        self._subcommands.append(command)

        self.data["options"].append(
            {
                "name": command.name,
                "description": command.description,
                "options": [] if command._slash_options is None else self.__options_parser(command.function, command._slash_options),
                "type": 1
            }
        )

        self.logger.info(f"Added subcommand '{command.name}' to '{self.name}'.")

    def __options_parser(
        self, 
        function: CommandFuncT, 
        slash_options: Dict[str, SlashOption]
    ) -> List[ApplicationCommandOptionData]:
        """A function that converts slash command parameters to slash command payload options."""
        options: List[ApplicationCommandOptionData] = []

        # Discord chat input regex as of 
        # https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-naming
        chat_input_patten = regex.compile(r"^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$", regex.UNICODE)

        func_params = list(function.__code__.co_varnames)

        # Filters out 'self' and 'platter' arguments.
        func_params = func_params[2:]

        # Get command function parameters.
        # --------------------------------------
        for param in func_params:
            # Uppercase parameters are not allowed in the discord API.
            if param.isupper() or bool(chat_input_patten.match(param)) is False:
                raise GoldyBotError(
                    f"The parameter used in the command '{self.name}' is NOT allowed >> {param}"
                )

            slash_option = slash_options.get(param)

            if slash_option is not None:
                option_name = slash_option.data["name"]
                slash_option.data["name"] = param if option_name is None else option_name

                options.append(slash_option.data)

            else:
                options.append({
                    "name": param,
                    "description": "🪹 Oopsie daisy, looks like no description was set for this option.",
                    "type": 3,
                    "required": True,
                })

        return options
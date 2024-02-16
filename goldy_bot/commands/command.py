from __future__ import annotations
from typing import TYPE_CHECKING

from discord_typings import ApplicationCommandPayload

if TYPE_CHECKING:
    from typing import Optional, Dict, List
    from discord_typings import ApplicationCommandOptionData

    from ..typings import CommandFuncT, SlashOptionsT

import regex
from devgoldyutils import LoggerAdapter

from ..helpers.dict_helper import DictHelper
from ..errors import GoldyBotError
from ..logger import goldy_bot_logger

__all__ = (
    "Command",
)

logger = LoggerAdapter(goldy_bot_logger, prefix = "Command")

class Command(DictHelper[ApplicationCommandPayload]):
    def __init__(
        self,
        function: CommandFuncT,
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        slash_options: Optional[Dict[str, SlashOptionsT]] = None, 
        wait: bool = False
    ) -> None:
        self.function = function

        name = name or function.__name__
        # Even though discord docs say no, description is a required field.
        description = description or "🪹 Oopsie daisy, looks like no description was set for this command." 
        slash_options = slash_options or {}

        data = {}
        data["type"] = 1
        data["name"] = name
        data["description"] = description
        data["options"] = self.__options_parser(self.params, slash_options)

        self.wait = wait

        self._slash_options = slash_options
        self._subcommands: Dict[str, Command] = {}

        super().__init__(data)

    @property
    def name(self) -> str:
        """The command's name."""
        return self.data["name"]

    @property
    def class_name(self) -> str:
        """The name of class this command is housed in."""
        return self.function.__qualname__.split(".")[0]

    @property
    def description(self) -> str:
        """The command's description."""
        return self.data["description"]

    @property
    def params(self) -> List[str]:
        """The commands's function parameters."""
        func_params = list(self.function.__code__.co_varnames)

        # Filters out 'self' and 'platter' arguments.
        return func_params[:self.function.__code__.co_argcount][2:]

    def add_subcommand(self, command: Command) -> None:
        subcommand_data = {
            "name": command.name, 
            "description": command.description, 
            "options": self.__options_parser(command.params, command._slash_options), 
            "type": 1
        }

        self.data["options"].append(subcommand_data)

        self._subcommands[command.name] = command
        logger.debug(f"Added subcommand '{command.name}' --> '{self.name}'.")

    def __options_parser( # TODO: Maybe more logging in here.
        self, 
        params: List[str], 
        slash_options: Dict[str, SlashOptionsT]
    ) -> List[ApplicationCommandOptionData]:
        """A function that converts slash command parameters to slash command payload options."""
        options: List[ApplicationCommandOptionData] = []

        # Discord chat input regex as of 
        # https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-naming
        chat_input_patten = regex.compile(r"^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$", regex.UNICODE)

        for param in params:
            # Uppercase parameters are not allowed in the discord API.
            if param.isupper() or bool(chat_input_patten.match(param)) is False:
                raise GoldyBotError(
                    f"The parameter used in the command '{self.name}' is NOT allowed >> {param}"
                )

            slash_option = slash_options.get(param)

            if slash_option is not None:
                option_name = slash_option.data.get("name")
                slash_option.data["name"] = option_name if option_name is not None else param # get's real slash option name

                options.append(slash_option.data)

            else:
                options.append({
                    "name": param, 
                    "description": "🪹 Oopsie daisy, looks like no description was set for this option.", 
                    "type": 3, 
                    "required": True
                })

        return options
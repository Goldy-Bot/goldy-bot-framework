from __future__ import annotations
from typing import TYPE_CHECKING, cast
from discord_typings import ApplicationCommandPayload

if TYPE_CHECKING:
    from typing import Callable, Any, Optional, Dict, List
    from discord_typings import ApplicationCommandOptionData

    from GoldyBot import SlashOption

    from ..platter import Platter

import regex
from devgoldyutils import LoggerAdapter

from .. import errors, logger

__all__ = (
    "Command",
)

class Command():
    def __init__(
        self,
        function: Callable[[object, Platter], Any],
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        slash_options: Optional[Dict[str, SlashOption]] = None, 
        wait: bool = False
    ) -> None:
        self.function = function

        name = name or function.__name__
        description = description or "🪹 Oopsie daisy, looks like no description was set for this command."

        self.payload = cast(ApplicationCommandPayload, {})
        self.payload["name"] = name
        self.payload["description"] = description
        self.payload["options"] = self.__options_parser(function, slash_options)

        self.wait = wait

        self._slash_options = slash_options
        self._subcommands: List[Command] = []

        self.logger = LoggerAdapter(
            LoggerAdapter(logger.goldy_bot_logger, prefix = "Command"), prefix = name
        )

    @property
    def name(self) -> str:
        """The command's name."""
        return self.payload["name"]

    @property
    def description(self) -> str:
        """The command's description."""
        return self.payload["description"]

    def add_subcommand(self, command: Command) -> None:
        self._subcommands.append(command)

        self.payload["options"].append(
            {
                "name": command.name,
                "description": command.description,
                "options": self.__options_parser(command.function, command._slash_options),
                "type": 1
            }
        )

        self.logger.info(f"Registered '{command.name}' as subcommand for '{self.name}'.")

    # Honestly this was all just stolen from pre-pancake (legacy).
    def __options_parser(
        self, 
        function: Callable[[object, Platter], Any], 
        slash_options: Optional[Dict[str, SlashOption]]
    ) -> List[ApplicationCommandOptionData]:
        """A function that converts slash command parameters to slash command payload options."""

        options: List[ApplicationCommandOptionData] = []
        slash_options: Dict[str, SlashOption] = slash_options or {}

        # Discord chat input regex as of 
        # https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-naming
        chat_input_patten = regex.compile(r"^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$", regex.UNICODE)

        # Get command function parameters.
        # -----------------------------------
        params = list(function.__code__.co_varnames)

        # Removes 'self' and 'platter' argument and filters out 
        # other variables resulting in just function parameters.
        params = params[1:self.function.__code__.co_argcount - 2]

        # Get command function parameters.
        # --------------------------------------
        for param in params:
            # Uppercase parameters are not allowed in the discord API.
            if param.isupper() or bool(chat_input_patten.match(param)) is False:
                raise errors.InvalidParameter(self, param)

            if param in params:
                option_data = slash_options[param]
                
                if option_data.get("name") is None:
                    option_data["name"] = param

                options.append(
                    option_data
                )

            else:
                options.append({
                    "name": param,
                    "description": "This option has no description. Sorry about that.",
                    "type": 3,
                    "required": True,
                })

        return options
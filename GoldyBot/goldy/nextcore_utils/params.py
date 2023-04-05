from __future__ import annotations

import regex
from typing import List, TYPE_CHECKING, Dict
from discord_typings import ApplicationCommandOptionData, MessageData, InteractionData

from ... import errors
from ..objects import PlatterType

if TYPE_CHECKING:
    from ..commands import Command

def params_to_options(command: Command) -> List[ApplicationCommandOptionData]:
    """A utility function that converts goldy command parameters to slash command options."""
    options:List[ApplicationCommandOptionData] = []

    # Discord chat input regex as of https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-naming
    chat_input_patten = regex.compile(r"^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$", regex.UNICODE)

    for param in command.params:
        if param.isupper() or bool(chat_input_patten.match(param)) is False: # Uppercase parameters are not allowed in the discord API.
            raise errors.InvalidParameter(command, param)

        if param in command.slash_options:
            options.append(
                command.slash_options[param]
            )
        
        else:
            options.append({
                "name": param,
                "description": "This option has no description. Sorry about that.",
                "type": 3,
                "required": True,
            })

    return options


def invoke_data_to_params(data: MessageData | InteractionData, platter_type: PlatterType) -> List[str] | Dict[str, str]:
    """A utility function that grabs command arguments from invoke data and converts it to appropriate params."""

    if platter_type.value == PlatterType.PREFIX_CMD.value:
        return data["content"].split(" ")[1:]
    
    if platter_type.value == PlatterType.SLASH_CMD.value:
        params = {}
        for option in data["data"]["options"]:
            params[option["name"]] = option["value"]

        return params
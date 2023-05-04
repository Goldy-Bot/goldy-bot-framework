from __future__ import annotations

import regex
from typing import List, TYPE_CHECKING, Dict
from discord_typings import ApplicationCommandOptionData, MessageData, InteractionData

from ... import errors
from ..objects import PlatterType, GoldPlatter

if TYPE_CHECKING:
    from ..commands import Command

def params_to_options(command: Command) -> List[ApplicationCommandOptionData]:
    """A utility function that converts goldy command parameters to slash command options."""
    options: List[ApplicationCommandOptionData] = []

    # Discord chat input regex as of https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-naming
    chat_input_patten = regex.compile(r"^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$", regex.UNICODE)

    for param in command.params:
        if param.isupper() or bool(chat_input_patten.match(param)) is False: # Uppercase parameters are not allowed in the discord API.
            raise errors.InvalidParameter(command, param)

        if param in command.slash_options:
            option_data = command.slash_options[param]
            
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


def invoke_data_to_params(data: MessageData | InteractionData, platter: GoldPlatter) -> List[str] | Dict[str, str]: 
    """A utility function that grabs command arguments from invoke data and converts it to appropriate params."""
    
    # Where all the fucking magic happens.
    if platter.type.value == PlatterType.PREFIX_CMD.value:
        params = []
        for arg in data["content"].split(" ")[1:]:
            # If the argument is a user, a channel or a role strip the id from the mention.
            if arg[:2] in ["<@", "<#"]:
                params.append(arg[2:-1])

        return params

    if platter.type.value == PlatterType.SLASH_CMD.value:
        params = {}
        for option in data["data"].get("options", []):
            param_key_name = option["name"]

            # If command is slash command make sure to set dictionary key to the true parameter name.
            if platter.type.value == 1:
                for slash_option in platter.command.slash_options:
                    if platter.command.slash_options[slash_option]["name"] == option["name"]:
                        param_key_name = slash_option
                        break

            params[param_key_name] = option["value"]

        return params
    

def get_function_parameters(command: Command) -> List[str]:
    """Returns the function parameters of a command respectively."""
    
    # Get list of function params.
    func_params = list(command.func.__code__.co_varnames)
    
    # Removes 'self' argument.
    func_params.pop(0)

    # Removes 'platter' argument.
    func_params.pop(0)

    # Filters out other variables resulting in just function parameters. It's weird I know.
    params = func_params[:command.func.__code__.co_argcount - 2]

    return params
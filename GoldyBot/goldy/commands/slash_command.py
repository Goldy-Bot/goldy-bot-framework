from __future__ import annotations
from typing import Any, Callable, Dict, List, TYPE_CHECKING
from discord_typings import ApplicationCommandOptionData, InteractionData

if TYPE_CHECKING:
    from .. import Goldy, objects
    from ... import Extension

from .command import Command
from ..objects import GoldPlatter

class SlashCommand(Command):
    def __init__(
        self, 
        goldy: Goldy, 
        func: Callable[[Extension, objects.GoldPlatter], Any], 
        name: str = None, 
        description: str = None, 
        required_roles: List[str] = None, 
        slash_options: Dict[str, ApplicationCommandOptionData] = None, 
        hidden: bool = False,
        pre_register: bool = True
    ):
        self.__sub_commands: List[SlashCommand] = []

        super().__init__(
            goldy = goldy, 
            func = func, 
            name = name, 
            description = description, 
            required_roles = required_roles, 
            slash_options = slash_options, 
            hidden = hidden,
            pre_register = pre_register
        )

        self.logger.debug("Slash command has been initialized!")

    def register_sub_command(self, command: Command) -> None:
        """Method to register slash sub command."""
        self.__sub_commands.append(command)

        dict(self)["options"].append(
            {
                "name": command.name,
                "description": command.description,
                "options": command.params_to_options(),
                "default_member_permissions": str(1 << 3) if command.hidden else None,
                "type": 1
            }
        )

        self.logger.info(f"Registered '{command.name}' -> '{self.name}' as sub command.")

    async def invoke(self, platter: objects.GoldPlatter) -> None:
        """Runs and triggers a slash command. This method is usually ran internally."""
        data: InteractionData = platter.data

        params = self.__invoke_data_to_params(data)
        if not params == {}: self.logger.debug(f"Got args --> {params}")

        return_value = await super().invoke(
            platter, lambda: self.func(platter.command.extension, platter, **params)
        )

        # Handle sub commands.
        # ----------------------
        # Invoke sub command if there is one in invoke data.
        if return_value is not False:
            await self.__invoke_sub_command(data, platter)

        # TODO: When exceptions raise in commands wrap them in a goldy bot command exception.


    async def __invoke_sub_command(self, data: InteractionData, platter: objects.GoldPlatter) -> None:
        for option in data["data"].get("options", []):
            if option["type"] == 1:
                for command in self.__sub_commands:
                    if command.name == option["name"]:
                        self.logger.debug("Calling sub command...")

                        interaction_responded = platter._interaction_responded

                        # Migrating some things from sub command.
                        data["data"]["options"] = option["options"]

                        platter = GoldPlatter(
                            data = data, 
                            author = platter.author,
                            command = command,
                        )
                        platter._interaction_responded = interaction_responded

                        await command.invoke(platter)
                        break

    def __invoke_data_to_params(self, data: InteractionData) -> Dict[str, str]:
        """A method that grabs slash command arguments from invoke data and converts it to appropriate params."""
        self.logger.debug("Attempting to phrase invoke data into parameters...")

        params = {}
        for option in data["data"].get("options", []):
            param_key_name = option["name"]

            if option["type"] == 1 or option["type"] == 2: # Ignore sub commands and sub groups.
                continue

            # Make sure to set dictionary key to the true parameter name.
            for slash_option in self.slash_options:
                if self.slash_options[slash_option]["name"] == option["name"]:
                    param_key_name = slash_option
                    break

            params[param_key_name] = option["value"]
            self.logger.debug(f"Found arg '{params[param_key_name]}'.")

        return params
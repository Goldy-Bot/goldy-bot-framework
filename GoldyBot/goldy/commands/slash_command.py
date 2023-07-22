from __future__ import annotations
from typing import Any, Callable, Dict, List, TYPE_CHECKING
from discord_typings import ApplicationCommandOptionData, InteractionData, AutocompleteInteractionData

from ..nextcore_utils import front_end_errors

if TYPE_CHECKING:
    from .. import Goldy, objects
    from ... import Extension
    from ..nextcore_utils.slash_options.auto_complete import SlashOptionAutoComplete

from .command import Command
from ..objects import GoldPlatter

class SlashCommand(Command):
    def __init__(
        self, 
        goldy: Goldy, 
        func: Callable[[Extension, objects.GoldPlatter], Any], 
        name: str = None, 
        description: str = None, 
        required_perms: List[str] = None, 
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
            required_perms = required_perms, 
            slash_options = slash_options, 
            hidden = hidden,
            pre_register = pre_register
        )

        self.logger.debug("Slash command has been initialized!")

    @property
    def is_parent(self):
        """Returns whether this slash command is a parent command or not."""
        if len(self.__sub_commands) > 0:
            return True

        return False


    def register_sub_command(self, command: SlashCommand) -> None:
        """Method to register slash sub command."""
        command._parent_command = self
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

        try:
            return_value = await super().invoke(
                platter, lambda: self.func(platter.invokable.extension, platter, **params)
            )

            # Handle sub commands.
            # ----------------------
            # Invoke sub command if there is one in invoke data.
            if return_value is not False:
                await self.__invoke_sub_command(data, platter)

        except Exception as e:
            raise front_end_errors.UnknownError(platter, e, self.logger)


    async def invoke_auto_complete(self, data: AutocompleteInteractionData):
        command: SlashCommand = self
        current_typing_value: str = None
        auto_complete_option: SlashOptionAutoComplete = None
        options = data["data"]["options"]

        # We are just handling sub commands here, nothing too important.
        if self.is_parent:
            for option in options:
                if not option["type"] == 1:
                    continue

                for sub_command in self.__sub_commands:

                    if option["name"] == sub_command.name:
                        options = option["options"]
                        command = sub_command
                        break

        for option in options:
            if option.get("focused"):
                current_typing_option = option
                current_typing_value = option["value"]

                for param in command.slash_options:
                    option = command.slash_options[param]

                    if option["name"] == current_typing_option["name"]:
                        auto_complete_option = option
                        break

                break

        await auto_complete_option.send_auto_complete(
            data, current_typing_value, self, self.goldy, 
        )


    async def __invoke_sub_command(self, data: InteractionData, platter: objects.GoldPlatter) -> None:
        for option in data["data"].get("options", []):
            if not option["type"] == 1:
                continue

            for command in self.__sub_commands:
                if command.name == option["name"]:
                    self.logger.debug("Calling sub command...")

                    interaction_responded = platter._interaction_responded

                    # Migrating some things from sub command.
                    data["data"]["options"] = option["options"]

                    platter = GoldPlatter(
                        data = data, 
                        author = platter.author,
                        invokable = command,
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
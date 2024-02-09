from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
    from typing import List, Dict, Optional, Tuple
    from discord_typings import InteractionData, ApplicationCommandPayload, ApplicationCommandData, ApplicationCommandOptionInteractionData

    from ...commands import Command
    from ...typings import GoldySelfT

from devgoldyutils import LoggerAdapter, Colours

from ...logger import goldy_bot_logger
from ...commands import CommandType
from ...errors import FrontEndError
from ...objects.platter import Platter
from ...helpers import Embed

__all__ = (
    "Commands",
)

logger = LoggerAdapter(
    goldy_bot_logger, prefix = "Commands"
)

class Commands():
    """Brings valuable methods to the goldy class for managing loading and syncing of commands."""
    def __init__(self) -> None:
        super().__init__()

    async def invoke_command(self: GoldySelfT[Self], name: str, type: CommandType, data: InteractionData) -> bool: 
        """Invokes a goldy bot command. Returns False if command is not found."""
        for extension in self.extensions:

            for _class in extension._classes:

                for command in extension._commands[_class.__class__.__name__]:

                    if command.name == name and command.data["type"] == type.value:
                        logger.info(
                            f"Invoking the command '{command.name}' in extension class '{_class.__class__.__name__}'..."
                        )

                        options = data["data"].get("options", [])

                        # if this is a subcommand then replace the parent command object with the subcommand.
                        subcommand, subcommand_options = self.__get_subcommand(data, command)

                        if subcommand is not None:
                            command = subcommand
                            options = subcommand_options

                        # create a platter, generate function params from interaction data options.
                        platter = Platter(data, self)
                        params = self.__interaction_options_to_kwargs(options, command)

                        # invoke the command's function
                        try:
                            await command.function(_class, platter, **params)

                        except FrontEndError as e:
                            self.__send_front_end_error(e) # TODO: Complete these.
                            raise e

                        except Exception as e:
                            await self.__send_unknown_error(e, platter, command)
                            raise e

                        return True

        return False

    async def _sync_commands(self: GoldySelfT[Self]) -> None:
        """
        Registers all the commands from each extension in goldy bot's internal state with discord if not registered already.
        Also removes commands from discord that are no longer registered within the framework.
        """
        commands_to_register: List[ApplicationCommandPayload] = []

        for extension in self.extensions:

            for commands in extension._commands.values():
                commands_to_register.extend([command.data for command in commands])

        test_guild_id = self.config.test_guild_id

        registered_application_commands = await self.low_level.get_application_commands(test_guild_id)

        commands_are_same = self.__are_commands_same(commands_to_register, registered_application_commands)

        if not commands_are_same:
            newly_registered_app_commands = await self.low_level.create_application_commands(
                payload = commands_to_register, 
                guild_id = test_guild_id
            )

            logger.debug(f"Commands registered -> {[(cmd['name'], cmd['type']) for cmd in newly_registered_app_commands]}")

            logger.info(
                Colours.GREEN.apply(str(len(newly_registered_app_commands))) + " new command(s) have been registered with discord!"
            )

        else:
            logger.info("No commands have been registered as no changes were detected.")

    def __are_commands_same(
        self, 
        commands_to_register: List[ApplicationCommandPayload], 
        registered_application_commands: List[ApplicationCommandData]
    ) -> bool:

        framework_commands = commands_to_register
        discord_app_commands = registered_application_commands

        if framework_commands == []:
            return False

        for command in framework_commands:
            found = False

            for app_command in discord_app_commands:

                # if this app command doesn't exist in framework NUKE IT.
                if app_command["name"] not in [command["name"] for command in framework_commands]:

                    logger.debug(
                        f"The application command '{app_command['name']}' of type '{CommandType(app_command['type']).name}' " \
                            "isn't registered in the framework, so it will be removed."
                    )

                    return False

                if command["name"] == app_command["name"] and command["type"] == app_command["type"]:

                    for key in ["description", "options"]:

                        if not command.get(key) == app_command.get(key):
                            return False

                    found = True

            if found is False:
                return False

        return True

    def __get_subcommand(self, data: InteractionData, parent_command: Command) -> Tuple[Optional[Command], List[ApplicationCommandOptionInteractionData]]:
        # NOTE: This won't support a third layer of subcommands.
        subcommand: Optional[Command] = None
        subcommand_options: List[ApplicationCommandOptionInteractionData] = []

        for option in data["data"].get("options", []):

            if option["type"] == 1:
                subcommand_options = option.get("options", []) 
                subcommand = parent_command._subcommands[option["name"]]
                break

        return subcommand, subcommand_options

    def __interaction_options_to_kwargs(self, options: List[ApplicationCommandOptionInteractionData], command: Command) -> Dict[str, str]:
        """A method that phrases option parameters from interaction data of a command."""
        logger.debug(
            f"Phrasing interaction data options into function parameters for command '{command.name}'..."
        )

        kwargs = {}

        for option in options:

            # Ignore sub commands and sub groups.
            if option["type"] == 1 or option["type"] == 2: 
                continue

            for param in command.params:
  
                if option["name"] == param:
                    kwargs[param] = option["value"]
                    logger.debug(f"Command argument '{param}' found!")
                    break

        return kwargs

    async def __send_unknown_error(self: GoldySelfT[Self], error: Exception, platter: Platter, command: Command):
        # TODO: Add report button that dms the bot developer the full traceback from the error.
        # Also add a guild and user black listing feature to it to mitigate spam and unwanted reports.
        embed = Embed(
            title = "❤️ An Error Occurred!", 
            description = "Oopsie daisy, an internal unknown error occurred. *Sorry I'm still new to this.* 🥺", 
            colour = Colours.RED, 
            footer = {
                "text": "Report button will be coming soon."
            }
        )

        await platter.send_message(embeds = [embed], hidden = True)

        logger.error(
            f"Error occurred in the command '{command.name}' executed by '{platter.data['member']['user']['username']}'!"
        )
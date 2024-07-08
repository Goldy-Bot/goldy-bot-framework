from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
    from typing import List, Dict, Optional, Tuple, Generator, Any, Union
    from discord_typings import (
        ApplicationCommandPayload, 
        ApplicationCommandData, 
        ApplicationCommandOptionInteractionData, 
        InteractionCreateData
    )
    from discord_typings.interactions.receiving import (
        SubcommandOptionInteractionData, 
        SubcommandGroupOptionInteractionData
    )

    from ...commands import Command
    from ...typings import GoldySelfT
    from ...extensions import Extension

from prettyprinter import pformat
from devgoldyutils import LoggerAdapter, Colours

from ...logger import goldy_bot_logger
from ...commands import CommandType, SlashOptionAutoComplete
from ...errors import FrontEndError
from ...objects.platter import Platter
from ...helpers import Embed, EmbedFooter
from ...colours import Colours as GBotColours

__all__ = (
    "Commands",
)

logger = LoggerAdapter(
    goldy_bot_logger, prefix = "Commands"
)

_type = type

class Commands():
    """Brings valuable methods to the goldy class for managing loading and syncing of commands."""
    def __init__(self) -> None:
        super().__init__()

    def get_commands(self: GoldySelfT[Self]) -> Generator[Tuple[Command, object, Extension], Any, None]:
        """Get framework commands."""

        for extension in self.extensions:

            for _class in extension._classes:

                for command in extension._commands[_class.__class__.__name__]:

                    yield command, _class, extension

    async def invoke_command(self: GoldySelfT[Self], name: str, type: CommandType, data: InteractionCreateData) -> bool: 
        """Invokes a goldy bot command. Returns False if command is not found."""
        for command, _class, _ in self.get_commands():

            if command.name == name and type == CommandType.AUTO_COMPLETE:
                options = data["data"]["options"]

                subcommand, subcommand_options = self.__get_subcommand(data, command)

                if subcommand is not None:
                    command = subcommand
                    options = subcommand_options

                auto_complete_option = options[0]
                params = self.__interaction_options_to_kwargs(options, command)

                for slash_option in command._slash_options.values():

                    if isinstance(slash_option, SlashOptionAutoComplete):

                        if slash_option.data["name"] == auto_complete_option["name"]:
                            await slash_option.send_auto_complete(
                                data, auto_complete_option["value"], params, _class, self
                            )

                            break # I don't think you can even get two auto complete slash options at the 
                            # same time, if we do welp... this shit is blowing up!

                return True

            elif command.name == name and type == CommandType.SLASH:
                logger.info(
                    f"Invoking the command '{command.name}' in extension class '{_class.__class__.__name__}'..."
                )

                logger.debug(f"Interaction data = {pformat(data)}")

                options = data["data"].get("options", [])

                # if this is a subcommand then replace the parent command object with the subcommand.
                subcommand, subcommand_options = self.__get_subcommand(data["data"].get("options", []), command)

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
                    await self.__send_front_end_error(e, platter, command) # TODO: Complete these.
                    # if it's a front end error it's anticipated so we don't need to raise it.

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
                        f"The application command '{app_command['name']}' of type '{app_command['type']}' " \
                            "isn't registered in the framework, so it will be removed and re-synced alongside others."
                    )

                    return False

                if command["name"] == app_command["name"] and command["type"] == app_command["type"]:

                    for key in ["description", "options"]:
                        value = command.get(key)
                        app_value = app_command.get(key)

                        if value == []:
                            value = None

                        if not value == app_value:
                            logger.debug(
                                f"The application command '{app_command['name']}' of type '{app_command['type']}' " \
                                    "was not identical to it's clone in the framework, so it will be removed and re-synced alongside others." \
                                        f"\nKey: '{key}' \nValues (fw | app): \n{pformat(value)} | \n{pformat(app_value)}"
                            )
                            return False

                    found = True

            if found is False:
                return False

        return True

    def __get_subcommand(
        self, 
        options: Union[SubcommandOptionInteractionData, SubcommandGroupOptionInteractionData, ApplicationCommandOptionInteractionData], 
        parent_command: Command
    ) -> Tuple[Optional[Command], List[ApplicationCommandOptionInteractionData]]:
        # NOTE: This won't support a third layer of subcommands.
        # TODO: Add support for more layers of subcommands.
        subcommand: Optional[Command] = None
        subcommand_options: List[ApplicationCommandOptionInteractionData] = []

        logger.debug(f"Finding subcommand in '{parent_command.name}' parent command...")

        for option in options:

            if option["type"] == 2: # we got to handle sub command groups differently
                subgroup_command_options = option.get("options", [])
                subgroup_master_command = parent_command._subcommands[option["name"]]

                return self.__get_subcommand(subgroup_command_options, subgroup_master_command)

            if option["type"] == 1:
                subcommand_options = option.get("options", [])
                subcommand = parent_command._subcommands[option["name"]]

                inner_subcommand, inner_subcommand_options = self.__get_subcommand(subcommand_options, subcommand)

                if inner_subcommand is not None:
                    return inner_subcommand, inner_subcommand_options

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

    async def __send_front_end_error(self: GoldySelfT[Self], error: FrontEndError, platter: Platter, command: Command):
        # TODO: Add report button that dms the bot developer the full traceback from the error.
        # Also add a guild and user black listing feature to it to mitigate spam and unwanted reports.

        await platter.send_message(embeds = [error.embed], hidden = True)

        logger.info(
            f"Front end error raised for command '{command.name}' executed by '{platter.data['member']['user']['username']}'." \
                f" Cause: {error.embed.data['description']}"
        )

    async def __send_unknown_error(self: GoldySelfT[Self], error: Exception, platter: Platter, command: Command):
        # TODO: Add report button that dms the bot developer the full traceback from the error.
        # Also add a guild and user black listing feature to it to mitigate spam and unwanted reports.
        embed = Embed(
            title = "❤️ An Error Occurred!", 
            description = "Oopsie daisy, an internal unknown error occurred. *Sorry I'm still new to this.* 🥺", 
            colour = GBotColours.RED, 
            footer = EmbedFooter(text = "Report button will be coming soon.")
        )

        await platter.send_message(embeds = [embed], hidden = True)

        logger.error(
            f"Error occurred in the command '{command.name}' executed by '{platter.data['member']['user']['username']}'!"
        )
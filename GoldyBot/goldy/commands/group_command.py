from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING, Tuple, overload
from discord_typings import ApplicationCommandOptionData, InteractionData

from devgoldyutils import Colours, LoggerAdapter

if TYPE_CHECKING:
    from .. import Goldy, objects
    from ... import Extension
    from ..nextcore_utils.slash_options.slash_option import SlashOption

from . import params_utils
from .slash_command import SlashCommand
from .prefix_command import PrefixCommand
from ... import get_goldy_instance, goldy_bot_logger

class GroupCommand():
    @overload
    def __init__(
        self, 
        name: str, 
        description: str = None, 
        required_roles: List[str] = None, 
        slash_options: Dict[str, ApplicationCommandOptionData] = None, 
        slash_cmd_only: bool = False, 
        hidden: bool = False,
    ):
        ...
        
    @overload
    def __init__(
        self, 
        base_commands: Tuple[SlashCommand, PrefixCommand] = None
    ):
        ...

    def __init__(
        self, 
        name: str = None, 
        description: str = None, 
        required_roles: List[str] = None, 
        slash_cmd_only: bool = False, 
        hidden: bool = False,
        base_commands: Tuple[SlashCommand, PrefixCommand] = None
    ):
        self.goldy = get_goldy_instance()
        self.logger = LoggerAdapter(goldy_bot_logger, prefix="GroupCommand")

        self.commands: Tuple[SlashCommand, PrefixCommand] = None

        if base_commands is None:
            self.commands = (
                SlashCommand(
                    self.goldy, 
                    func = lambda x, y: None,
                    name = name,
                    description = description,
                    required_roles = required_roles,
                    hidden = hidden
                ),
                PrefixCommand(
                    self.goldy, 
                    func = lambda x, y: None,
                    name = name,
                    description = description,
                    required_roles = required_roles,
                    hidden = hidden
                ) if slash_cmd_only is False else None
            )
        else:
            self.commands = base_commands

        self.logger.debug("Group command has been initialized!")

    def master_command(self):
        def decorate(func):
            def inner(func) -> None:
                for command in self.commands:

                    if command is not None:
                        command.func = func

            return inner(func)

        return decorate

    def sub_command(
        self,
        name: str = None, 
        description: str = None, 
        required_roles: List[str]=None, 
        slash_options: Dict[str, SlashOption] = None
    ):
        """
        Create a sub command in this group command with this decorator.
        
        ---------------
        
        ⭐ Example:
        -------------
        This is how you can create a sub command in GoldyBot::

            @GoldyBot.command(group=True)
            async def game(self, platter: GoldyBot.GoldPlatter):
                if platter.author.id == "332592361307897856":
                    return True

                # You are able to perform checks with sub commands like this.
                # Returning False will stop the execution of the sub command. 
                # Returning True or nothing (None) will allow the sub command to execute.

                await platter.send_message("You are not the game master! So you may not start the game.", reply=True)
                return False

            @game.sub_command()
            async def start(self, platter: GoldyBot.GoldPlatter):
                await platter.send_message("✅ Game has started!", reply=True)

        .. note::

            Read the code comments for more detail.

        .. warning::

            To create a sub command from a command, you first must make that command a group command by passing the ``group=True`` parameter.

        """
        def decorate(func):
            def inner(func) -> None:
                for command in self.commands:

                    if command is not None:
                        ...

            return inner(func)

        return decorate
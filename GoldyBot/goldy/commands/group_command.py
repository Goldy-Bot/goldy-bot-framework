from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING, Tuple, overload, Callable, Any

from devgoldyutils import LoggerAdapter

if TYPE_CHECKING:
    from ..nextcore_utils.slash_options.slash_option import SlashOption
    from ..objects.platter.golden_platter import GoldPlatter

from .slash_command import SlashCommand
from .prefix_command import PrefixCommand
from ... import get_goldy_instance, goldy_bot_logger

class GroupCommand():
    """
    The group command allows for the grouping of commands together like sub commands and ect.
    
    ---------------
    
    ⭐ Example:
    -------------
    You can group commands like so::

        group = GoldyBot.GroupCommand("game")

        @group.sub_command()
        async def start(self, platter: GoldyBot.GoldPlatter):
            await platter.send_message("✅ Game has started!", reply=True)

    If you would like a parent command you can do this::
    
        group = GoldyBot.GroupCommand("game")

        @group.master_command()
        async def game(self, platter: GoldyBot.GoldPlatter):
            if platter.author.id == "332592361307897856":
                return True

            # You are able to perform checks with sub commands like this.
            # Returning False will stop the execution of the sub command. 
            # Returning True or nothing (None) will allow the sub command to execute.

            await platter.send_message("You are not the game master! So you may not start the game.", reply=True)
            return False

        @group.sub_command()
        async def start(self, platter: GoldyBot.GoldPlatter):
            await platter.send_message("✅ Game has started!", reply=True)

    """
    @overload
    def __init__(
        self, 
        name: str, 
        description: str = None, 
        required_perms: List[str] = None, 
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
        required_perms: List[str] = None, 
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
                    func = lambda x, y: self.__dummy__(),
                    name = name,
                    description = description,
                    required_perms = required_perms,
                    hidden = hidden
                ),
                PrefixCommand(
                    self.goldy, 
                    func = lambda x, y: self.__dummy__(),
                    name = name,
                    description = description,
                    required_perms = required_perms,
                    hidden = hidden
                ) if slash_cmd_only is False else None
            )
        else:
            self.commands = base_commands

        self.logger.debug("Group command has been initialized!")

    def master_command(self):
        def decorate(func):
            def inner(func: Callable) -> None:
                slash_cmd, prefix_cmd = self.commands

                if slash_cmd is not None:
                    slash_cmd.func = func

                if prefix_cmd is not None:
                    prefix_cmd.func = func

                self.logger.debug(f"Master command initialized to '{func.__name__}' function.")

            return inner(func)

        return decorate

    def sub_command(
        self,
        name: str = None, 
        description: str = None, 
        required_perms: List[str]=None, 
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

        However there is also another way to create sub commands that allows you to completely skip registering the parent command::

            group = GoldyBot.GroupCommand("game")

            @group.sub_command()
            async def start(self, platter: GoldyBot.GoldPlatter):
                await platter.send_message("✅ Game has started!", reply=True)

        This makes things a little more cleaner.

        If you would like the parent command back you can also have that::
        
            group = GoldyBot.GroupCommand("game")

            @group.master_command()
            async def game(self, platter: GoldyBot.GoldPlatter):
                if platter.author.id == "332592361307897856":
                    return True

                # You are able to perform checks with sub commands like this.
                # Returning False will stop the execution of the sub command. 
                # Returning True or nothing (None) will allow the sub command to execute.

                await platter.send_message("You are not the game master! So you may not start the game.", reply=True)
                return False

            @group.sub_command()
            async def start(self, platter: GoldyBot.GoldPlatter):
                await platter.send_message("✅ Game has started!", reply=True)

        Although this now sort of defeats the purpose, so it's up to you to pick which one is best. 😉

        """
        def decorate(func):
            def inner(func: Callable) -> Callable[[GoldPlatter], Any]:
                slash_cmd, prefix_cmd = self.commands

                if slash_cmd is not None:
                    slash_cmd.extension_name = str(func).split(" ")[1].split(".")[0] # I do this incase the master command is not set.
                    slash_cmd.register_sub_command(
                        SlashCommand(
                            self.goldy,
                            func,
                            name,
                            description,
                            required_perms,
                            slash_options,
                            pre_register = False
                        )
                    )

                if prefix_cmd is not None:
                    prefix_cmd.extension_name = str(func).split(" ")[1].split(".")[0]  # I do this incase the master command is not set.
                    prefix_cmd.register_sub_command(
                        PrefixCommand(
                            self.goldy,
                            func,
                            name,
                            description,
                            required_perms,
                            pre_register = False
                        )
                    )

                return func

            return inner(func)

        return decorate

    async def __dummy__(self):
        ...
from __future__ import annotations
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from typing import Optional, Callable, Any, Dict

    from GoldyBot import SlashOption

    from ..platter import Platter

from devgoldyutils import LoggerAdapter

from .command import Command
from ..logger import goldy_bot_logger

__all__ = (
    "GroupCommand",
)

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
        description: str = None
    ):
        ...

    @overload
    def __init__(
        self, 
        command: Optional[Command] = None
    ):
        ...

    def __init__(
        self, 
        name: str = None, 
        description: str = None, 
        command: Optional[Command] = None
    ):
        self._master_command = command

        if self._master_command is None:
            self._master_command = Command( 
                function = lambda x, y: self.__dummy__(),
                name = name,
                description = description
            )

        self.logger = LoggerAdapter(goldy_bot_logger, prefix = "GroupCommand")

    def master_command(self):
        def decorate(func):
            def inner(func: Callable) -> None:
                self._master_command.function = func

                self.logger.debug(f"The function '{func.__name__}' was made a master command.")

            return inner(func)

        return decorate

    def subcommand(
        self,
        name: str = None, 
        description: str = None, 
        slash_options: Dict[str, SlashOption] = None,
        wait: bool = False
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
            def inner(func: Callable) -> Callable[[Platter], Any]:
                self._master_command.add_subcommand(
                    Command(
                        function = func,
                        name = name,
                        description = description,
                        slash_options = slash_options,
                        wait = wait
                    )
                )

                return func

            return inner(func)

        return decorate

    async def __dummy__(self):
        ...
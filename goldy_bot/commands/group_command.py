from __future__ import annotations
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from typing import Optional, Callable, Dict

    from GoldyBot import SlashOption

    from ..objects.platter import Platter

from devgoldyutils import LoggerAdapter

from .command import Command
from ..logger import goldy_bot_logger

__all__ = (
    "GroupCommand",
)

logger = LoggerAdapter(goldy_bot_logger, prefix = "GroupCommand")

class GroupCommand():
    """
    A group command allows you to group commands together to make sub commands.

    ---------------

    ⭐ Example:
    -------------
    You can group commands like so::

        group = goldy_bot.GroupCommand("game")

        @group.subcommand()
        async def start(self, platter: GoldyBot.GoldPlatter):
            await platter.send_message("✅ Game has started!", reply=True)

    If you would like a parent command you can do this::

        group = goldy_bot.GroupCommand("game")

        @group.master_command()
        async def game(self, platter: goldy_bot.Platter):
            if platter.author.id == "332592361307897856":
                return True

            # You are able to perform checks with sub commands like this.
            # Returning False will stop the execution of the sub command. 
            # Returning True or nothing (None) will allow the sub command to execute.

            await platter.send_message("You are not the game master! So you may not start the game.", reply=True)
            return False

        @group.subcommand()
        async def start(self, platter: goldy_bot.Platter):
            await platter.send_message("✅ Game has started!", reply=True)

    """
    @overload
    def __init__(
        self, 
        name: str, 
        description: Optional[str] = None, 
        parent_group: Optional[GroupCommand] = None
    ):
        ...

    @overload
    def __init__(
        self, 
        command: Optional[Command] = None, 
        parent_group: Optional[GroupCommand] = None
    ):
        ...

    def __init__(
        self, 
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        command: Optional[Command] = None, 
        parent_group: Optional[GroupCommand] = None
    ):
        self._master_command: Command = command
        self._parent_group = parent_group

        if self._master_command is None and name is None:
            raise ValueError("You must give the group command a name if you're not passing a command object!")

        if self._master_command is None:
            self._master_command = Command( 
                function = None, 
                name = name, 
                description = description
            )

        if parent_group is not None:
            self._master_command.data["type"] = 2 # we must do this so it's a group command by discord's standards.

    def master_command(self):
        def decorate(func):
            def inner(func: Callable) -> None:
                self._master_command.function = func

                logger.debug(f"The function '{func.__name__}' was made a master command.")

            return inner(func)

        return decorate

    def subcommand(
        self, 
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        slash_options: Optional[Dict[str, SlashOption]] = None, 
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
            def inner(func: Callable) -> Callable[[Platter], Callable]:
                self._master_command.add_subcommand(
                    Command(
                        function = func,
                        name = name,
                        description = description,
                        slash_options = slash_options,
                        wait = wait
                    )
                )

                # If we don't update the master command in the parent group with 
                # our master command sub-commands will fail to be set as an option.
                # self.__sync_with_parent_master_command() # NOTE: Do we even need this now?

                return func

            return inner(func)

        return decorate

    def group_command(
        self, 
        name: str, 
        description: Optional[str] = None
    ) -> GroupCommand:
        group = GroupCommand(
            name = name, 
            description = description, 
            parent_group = self
        )

        self._master_command.add_subcommand(group._master_command)

        return group

    def __sync_with_parent_master_command(self) -> None:

        if self._parent_group is not None:
            master_command = self._master_command
            parent_master_command = self._parent_group._master_command

            for subcommand in parent_master_command._subcommands:

                if subcommand == master_command.name:
                    del parent_master_command._subcommands[master_command.name]
                    break

            for index, option in enumerate(parent_master_command.data["options"]):

                if option["name"] == master_command.name:
                    parent_master_command.data["options"].pop(index)
                    break

            parent_master_command.add_subcommand(master_command)

            logger.debug(
                f"Synced group master command '{master_command.name}' with parent group master command '{parent_master_command.name}'."
            )
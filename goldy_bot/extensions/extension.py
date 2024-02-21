from __future__ import annotations
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from typing import List, Dict, Optional, Literal, Callable

    from ..typings import SlashOptionsT

    from ..goldy import Goldy

    ExtensionClassT = Callable[[Goldy], object]

from devgoldyutils import LoggerAdapter

from ..commands import Command
from ..logger import goldy_bot_logger
from ..commands.group_command import GroupCommand

__all__ = (
    "Extension",
)

logger = LoggerAdapter(goldy_bot_logger, prefix = "Extension")

class Extension():
    """Class to create an extension in 🥞 pancake."""
    def __init__(self, name: str) -> None:
        self.name = name

        self._classes: List[object] = []
        self._commands: Dict[str, List[Command]] = {}

    def mount(self, goldy: Goldy, *cls: ExtensionClassT) -> None:
        """Method to mount any classes you are using in your extension."""
        for _class in cls:
            self._classes.append(_class(goldy))

            logger.debug(
                f"Mounted class '{_class.__name__}' to extension '{self.name}'."
            )

    @overload
    def command(
        self,
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        slash_options: Dict[str, SlashOptionsT] = None,
        group: Literal[False] = False,
        wait: bool = False
    ) -> Callable[..., Callable]:
        ...

    @overload
    def command(
        self,
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        group: Literal[True] = False,
        wait: bool = False
    ) -> Callable[..., GroupCommand]:
        ...

    def command(
        self,
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        slash_options: Dict[str, SlashOptionsT] = None,
        group: bool = False,
        wait: bool = False
    ) -> Callable[..., GroupCommand] | Callable[..., Callable]:
        """
        Add a command to a Goldy Bot extension with this decorator.

        ---------------

        ⭐ Example:
        -------------
        This is how you create a command in GoldyBot::

            @extension.command()
            async def hello(self, platter: GoldyBot.GoldPlatter):
                await platter.send_message("👋hello", reply=True)

        .. note::

            Visit `here`_ to find out how to create extensions.

        .. _here: https://goldybot.devgoldy.xyz/goldy.extensions.html#how-to-create-an-extension
        """
        def decorate(func):
            def inner(func):
                command = Command(
                    function = func, 
                    name = name, 
                    description = description, 
                    slash_options = slash_options,
                    wait = wait
                )

                class_name = command.function.__qualname__.split(".")[0]

                self._add_command(command, class_name)

                return GroupCommand(command = command) if group else func

            return inner(func)

        return decorate

    def group_command(
        self, 
        class_name: str, 
        name: str, 
        description: Optional[str] = None
    ) -> GroupCommand:
        """
        Add a group command to a Goldy Bot extension with this decorator.
        A group command allows you to group commands together to make sub commands.

        ---------------

        ⭐ Example:
        -------------
        You can group commands in extensions like so::

            group = extension.group_command(__qualname__, "game")

            @group.subcommand()
            async def start(self, platter: goldy_bot.Platter):
                await platter.send_message("✅ Game has started!", reply=True)

        If you would like a parent command you can do this::

            group = extension.group_command(__qualname__, "game")

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

        .. note::

            Visit `here`_ to find out how to create extensions.

        .. _here: https://goldybot.devgoldy.xyz/goldy.extensions.html#how-to-create-an-extension
        """
        group_command = GroupCommand(name, description)

        self._add_command(group_command._master_command, class_name)

        return group_command

    def _add_command(self, command: Command, class_name: str):
        if class_name not in self._commands:
            self._commands[class_name] = []

        self._commands[class_name].append(command)
        logger.debug(f"Added command '{command.name}' --> '{self.name}'.")
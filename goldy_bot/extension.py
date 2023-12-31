from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict, Optional

    from GoldyBot.goldy.nextcore_utils.slash_options.slash_option import SlashOption

from devgoldyutils import LoggerAdapter

from .logger import goldy_bot_logger
from .commands import GroupCommand, Command

class Extension():
    """🥞 Pancake extension to create an extension."""
    def __init__(self, name: str) -> None:
        self.name = name

        self.__classes: List[object] = []
        self.__commands: Dict[object, List[object]] = [] # TODO: Change 'object' in List[] to 'command' when that is available.

        self.logger = LoggerAdapter(goldy_bot_logger, prefix = "Extension")

    def mount(self, _class: object):
        self.__classes.append(_class)
        self.logger.debug(f"Mounted class '{_class.__name__}' to extension '{self.name}'.")

    def command(
        self,
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        slash_options: Dict[str, SlashOption] = None,
        group: bool = False,
        wait: bool = False
    ):
        """
        Add a command to Goldy Bot with this decorator.

        ---------------

        ⭐ Example:
        -------------
        This is how you create a command in GoldyBot::

            @GoldyBot.command()
            async def hello(self, platter: GoldyBot.GoldPlatter):
                await platter.send_message("👋hello", reply=True)

        .. warning::

            Do note that standalone commands are no longer a thing in goldy bot v5 so you WILL need to register this command inside an Extension. Visit `here`_ to find out how to create extensions.

        .. _here: https://goldybot.devgoldy.xyz/goldy.extensions.html#how-to-create-an-extension
        """
        def decorate(func):
            def inner(func):
                command = Command(
                    func = func, 
                    name = name, 
                    description = description, 
                    slash_options = slash_options,
                    wait = wait
                )

                return GroupCommand(command = command) if group else func

            return inner(func)

        return decorate
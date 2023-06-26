from __future__ import annotations
from typing import Callable, Any, List, Dict, TYPE_CHECKING
from discord_typings import ApplicationCommandOptionData

import logging
from devgoldyutils import LoggerAdapter, Colours

from GoldyBot.goldy.objects.invokable import InvokableType
from ... import goldy_bot_logger

from .. import objects

if TYPE_CHECKING:
    from ... import Goldy

class Command(objects.Invokable):
    """Class that all commands in goldy bot inherit from."""
    def __init__(
        self, 
        goldy: Goldy, 
        func: Callable[[objects.GoldPlatter], Any], 
        name: str, 
        description: str, 
        required_roles: List[str], 
        slash_options: Dict[str, ApplicationCommandOptionData], 
        allow_prefix_cmd: bool, 
        hidden: bool, 
    ):
        self.__func = func
        self.__required_roles = required_roles
        self.__slash_options = slash_options
        self.__allow_prefix_cmd = allow_prefix_cmd
        self.__hidden = hidden

        super().__init__(
            name, 
            {
                "name": name,
                "description": description,
                "default_member_permissions": str(1 << 3) if hidden else None,
                "type": 1
            }, 
            goldy, 
            LoggerAdapter(LoggerAdapter(goldy_bot_logger, prefix=f"Command"), prefix=Colours.PINK_GREY.apply(name))
        )

    @property
    def func(self) -> Callable[[objects.GoldPlatter], Any]:
        """The command's callback function."""
        return self.__func
    
    @property
    def name(self) -> str:
        """The command's code name."""
        return self.get("name")
    
    @property
    def description(self) -> str:
        """The command's set description. None if there is no description set."""
        return self.get("description")

    @property
    def required_roles(self):
        """The code names for the roles needed to access this command."""
        return self.__required_roles
    
    @property
    def slash_options(self):
        """Allows you to customize slash command arguments and make them beautiful 🥰."""
        return self.__slash_options
    
    @property
    def allow_prefix_cmd(self):
        """If the creation of a prefix command is allowed. Slash commands are now ALWAYS created since v5.0dev5."""
        return self.__allow_prefix_cmd
    
    @property
    def hidden(self):
        """Should this command be hidden? For slash commands the command is just set to admins only."""
        return self.__hidden
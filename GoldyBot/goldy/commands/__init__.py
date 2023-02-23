from __future__ import annotations

from typing import List

from .. import utils
from ... import LoggerAdapter, goldy_bot_logger
from ..extensions import Extension, extensions_cache

class Command():
    def __init__(
        self, 
        func, 
        cmd_name:str = None,
        description:str = None,
        required_roles:List[str] = None,
        parent_cmd:Command = None
    ):
        """A class representing a GoldyBot command."""
        self.func:function = func
        """The command's callback function."""
        self.cmd_name = cmd_name
        """The command's code name."""
        self.description = description
        """The command's set description. None if there is no description set."""
        self.required_roles = required_roles
        """The code names for the roles needed to access this command."""
        self.parent_cmd = parent_cmd
        """Command object of the parent command if this command is a subcommand."""

        self.logger = LoggerAdapter(goldy_bot_logger, prefix="Command")

        if self.cmd_name is None:
            self.cmd_name = self.func.__name__
        
        self.params = list(self.func.__code__.co_varnames)
        self.__params_amount = self.func.__code__.co_argcount
        
        self.__in_extension = False

        if self.params[0] == "self":
            self.__in_extension = True
            self.__params_amount -= 1
            self.params.pop(0)

    @property
    def in_extension(self) -> bool:
        """Returns true if the command is in an extension."""
        if self.__in_extension:
            return True
        return False

    @property
    def extension_name(self) -> str | None:
        """Returns extension's code name."""
        if self.in_extension:
            return str(self.func).split(" ")[1].split(".")[0]

        return None

    @property
    def extension(self) -> Extension | None:
        """Finds and returns the object of the command's extension. Returns None if command is not in any extension."""
        if self.in_extension:
            return utils.cache_lookup(self.extension_name, extensions_cache)
        
        return None

    @property
    def is_child(self):
        """Returns if command is child or not. Basically is it a subcommand or not essentially."""
        if self.parent_cmd is None:
            return False
        else:
            return True

    def create_slash(self) -> nextcord.BaseApplicationCommand:
        """Creates slash command."""
        self.logger.info(f"Creating slash command for '{self.cmd_name}'...")
        ...
    
    # Where I left off.
    # TODO: Use code from goldy bot v4 to fill the rest.

    def any_args_missing(self, command_executers_args:tuple) -> bool:
        """Checks if the args given by the command executer matches what parameters the command needs."""
        if len(command_executers_args) == len(self.params[1:]):
            return True
        else:
            return False

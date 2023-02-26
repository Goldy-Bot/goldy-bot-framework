from __future__ import annotations

from typing import List
from discord_typings import ApplicationCommandData

from .. import utils
from ... import LoggerAdapter, goldy_bot_logger, Goldy
from ..extensions import Extension, extensions_cache


class Command():
    def __init__(
        self, 
        goldy:Goldy, 
        func, 
        name:str = None, 
        description:str = None, 
        required_roles:List[str] = None, 
        parent_cmd:Command = None
    ):
        """A class representing a GoldyBot command."""
        self.func:function = func
        """The command's callback function."""
        self.name = name
        """The command's code name."""
        self.description = description
        """The command's set description. None if there is no description set."""
        self.required_roles = required_roles
        """The code names for the roles needed to access this command."""
        self.parent_cmd = parent_cmd
        """Command object of the parent command if this command is a subcommand."""

        self.goldy = goldy
        self.logger = LoggerAdapter(
            LoggerAdapter(goldy_bot_logger, prefix="Command"), 
            prefix=(lambda x: self.func.__name__ if x is None else x)(self.name)
        )

        # If cmd_name is null, set it to function name.
        if self.name is None:
            self.name = self.func.__name__
        
        if self.description is None:
            self.description = "This command has no description. Sorry about that."
        
        # Get list of function params.
        self.params = list(self.func.__code__.co_varnames)
        self.__params_amount = self.func.__code__.co_argcount
        
        # Check if command is inside extension by checking if self is first parameter.
        self.__in_extension = False

        if self.params[0] == "self":
            self.__in_extension = True
            self.__params_amount -= 1
            self.params.pop(0)

        self.list_of_application_command_data:List[ApplicationCommandData] = None

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
            return utils.cache_lookup(self.extension_name, extensions_cache)[1]
        
        return None

    @property
    def is_child(self):
        """Returns if command is child or not. Basically is it a subcommand or not essentially."""
        if self.parent_cmd is None:
            return False
        else:
            return True

    async def create_slash(self) -> List[ApplicationCommandData]:
        """Creates and registers a slash command in goldy bot. E.g.``/goldy``"""
        self.logger.info(f"Creating slash command for '{self.name}'...")

        list_of_application_command_data = []

        # Add slash command for each allowed guild.
        # -------------------------------------------
        for guild in self.goldy.guilds.allowed_guilds:

            list_of_application_command_data.append(
                await self.goldy.http_client.create_guild_application_command(
                    authentication = self.goldy.nc_authentication,
                    application_id = self.goldy.application_data["id"],
                    guild_id = guild[0],

                    name = self.name,
                    description = self.description,
                )
            )

            self.logger.debug(f"Created slash for guild '{guild[1]}'.")

        self.list_of_application_command_data = list_of_application_command_data
        return list_of_application_command_data
    
    async def create_normal(self) -> None:
        """Creates and registers a normal on-msg command in goldy bot. Also know as a prefix command. E.g.``!goldy``"""
        ...
    
    # Where I left off.
    # TODO: Use code from goldy bot v4 to fill the rest.

    def any_args_missing(self, command_executers_args:tuple) -> bool:
        """Checks if the args given by the command executer matches what parameters the command needs."""
        if len(command_executers_args) == len(self.params[1:]):
            return True
        else:
            return False

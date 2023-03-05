from __future__ import annotations

from typing import List, Callable, Tuple, TYPE_CHECKING
from discord_typings import ApplicationCommandData, MessageData, InteractionData

from .. import utils
from ..objects import GoldPlatter, PlatterType
from ... import LoggerAdapter, goldy_bot_logger
from ..extensions import Extension, extensions_cache

if TYPE_CHECKING:
    from ... import Goldy

commands_cache:List[Tuple[str, object]] = []
"""
This cache contains all the commands that have been registered and it's memory location to the class.
"""

class Command():
    def __init__(
        self, 
        goldy:Goldy, 
        func, 
        name:str = None, 
        description:str = None, 
        required_roles:List[str] = None, 
        allow_prefix_cmd:bool = True, 
        allow_slash_cmd:bool = True, 
        parent_cmd:Command = None
    ):
        """A class representing a GoldyBot command."""
        self.func:Callable = func
        """The command's callback function."""
        self.name = name
        """The command's code name."""
        self.description = description
        """The command's set description. None if there is no description set."""
        self.required_roles = required_roles
        """The code names for the roles needed to access this command."""
        self.allow_prefix_cmd = allow_prefix_cmd
        """If the creation of a prefix command is allowed."""
        self.allow_slash_cmd = allow_slash_cmd
        """If the creation of a slash command is allowed."""
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

        commands_cache.append(
            (self.name, self)
        )

        self.logger.debug("Command initialized!")

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
        
    
    async def __invoke(self, data:MessageData|InteractionData, type:PlatterType|int) -> bool:
        """Runs/triggers this command. This method is mostly supposed to be used internally."""
        # If not from guild in allowed guilds don't invoke.
        if data["guild_id"] in [x[0] for x in self.goldy.config.allowed_guilds]:
        
            gold_plater = GoldPlatter(data, type)
            guild = self.goldy.guilds.get_guild(data["guild_id"])

            # TODO: Add all permission and argument management stuff here...

            # Prefix/normal command.
            # ------------------------
            if gold_plater.type.value == PlatterType.PREFIX_CMD.value:
                data:MessageData = data
                prefix = guild.prefix

                if data["content"] == f"{prefix}{self.name}":
                    self.logger.info(f"Command invoked by '{data['author']['username']}#{data['author']['discriminator']}'.")

                    if self.in_extension:
                        await self.func(self.extension, gold_plater)
                    else:
                        await self.func(gold_plater)


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
        """Creates and registers a normal on-msg/prefix command in goldy bot. Also know as a prefix command. E.g.``!goldy``"""
        self.logger.info(f"Creating normal/prefix command for '{self.name}'...")

        self.goldy.shard_manager.event_dispatcher.add_listener(
            lambda x: self.goldy.async_loop.create_task(self.__invoke(x, type=PlatterType.PREFIX_CMD)),
            event_name="MESSAGE_CREATE"
        )


    def load(self) -> None:
        """Loads and creates the command."""

        if self.allow_slash_cmd:
            self.goldy.async_loop.create_task(
                self.create_slash()
            )

        if self.allow_prefix_cmd:
            self.goldy.async_loop.create_task(
                self.create_normal()
            )

        if self.extension is not None:
            self.extension.add_command(self)

        return None
    
    
    # Where I left off.
    # TODO: Use code from goldy bot v4 to fill the rest.

    def any_args_missing(self, command_executers_args:tuple) -> bool:
        """Checks if the args given by the command executer matches what parameters the command needs."""
        if len(command_executers_args) == len(self.params[1:]):
            return True
        else:
            return False

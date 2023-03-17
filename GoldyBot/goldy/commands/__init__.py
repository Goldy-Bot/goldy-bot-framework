from __future__ import annotations

from typing import List, Callable, Tuple, TYPE_CHECKING
from discord_typings import ApplicationCommandData, MessageData, InteractionData, ApplicationCommandPayload

from nextcore.http import Route

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
    """Class that represents all commands in goldy bot."""
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

        self.list_of_application_command_data:List[Tuple[str, ApplicationCommandData]] | None = None

        self.__loaded = False

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
    
    @property
    def loaded(self) -> bool:
        """Returns whether this command has been loaded."""
        return self.__loaded


    async def __invoke_prefix(self, data:MessageData):
        guild = self.goldy.guilds.get_guild(data["guild_id"])

        if guild is not None: # Ignore invoke if guild is None as None could mean the guild is not in the allowed guilds list.

            if data["content"] == f"{guild.prefix}{self.name}":
                self.goldy.async_loop.create_task(self.__invoke(data, type=PlatterType.PREFIX_CMD))

    async def __invoke_slash(self, data:InteractionData):
        guild = self.goldy.guilds.get_guild(data["guild_id"])

        if guild is not None: # Ignore invoke if guild is None as None could mean the guild is not in the allowed guilds list.

            if self.name == data["data"]["name"]:
                self.goldy.async_loop.create_task(self.__invoke(data, type=PlatterType.SLASH_CMD))


    async def __invoke(self, data:MessageData|InteractionData, type:PlatterType|int) -> bool:
        """Runs/triggers this command. This method is mostly supposed to be used internally."""
        self.logger.debug(f"Attempting to invoke '{type.name}'...")
        
        gold_plater = GoldPlatter(data, type, goldy=self.goldy, command=self)

        if self.__got_perms(gold_plater):

            # Prefix/normal command.
            # ------------------------
            if gold_plater.type.value == PlatterType.PREFIX_CMD.value:
                data:MessageData = data

                self.logger.info(f"Prefix command invoked by '{data['author']['username']}#{data['author']['discriminator']}'.")

                if self.in_extension:
                    await self.func(self.extension, gold_plater)
                else:
                    await self.func(gold_plater)


            # Slash command.
            # ----------------
            if gold_plater.type.value == PlatterType.SLASH_CMD.value:
                data:InteractionData = data

                self.logger.info(f"Slash command invoked by '{data['member']['user']['username']}#{data['member']['user']['discriminator']}'.")

                if self.in_extension:
                    await self.func(self.extension, gold_plater)
                else:
                    await self.func(gold_plater)

            return True
    
        # Member has no perms.
        # TODO: Add no perms discord message.

        return False
    
    def __got_perms(self, gold_plater:GoldPlatter) -> bool:
        """Internal method that checks if the command author has the perms to run this command."""

        if not self.required_roles == []:

            # If the required roles contain 'bot_dev' and the bot dev is running the command allow the command to execute.
            # --------------------------------------------------------------------------------------------------------------
            if "bot_dev" in self.required_roles:
                if gold_plater.author.id == self.goldy.config.bot_dev:
                    return True

            # Check if member has any of the required roles.
            #----------------------------------------------------
            for role_code_name in self.required_roles:

                if not role_code_name in ["bot_dev", "bot_admin"]:
                    
                    # TODO: Check if member has this role.
                    # Might have to create a role object and add a .has_role() method to Member object.
                    ...

            return False
        
        return True


    async def create_slash(self) -> List[ApplicationCommandData]:
        """Creates and registers a slash command in goldy bot. E.g.``/goldy``"""
        self.logger.debug(f"Creating slash command for '{self.name}'...")

        list_of_application_command_data = []

        # Add slash command for each allowed guild.
        # -------------------------------------------
        for guild in self.goldy.guilds.allowed_guilds:

            payload = ApplicationCommandPayload(
                name = self.name,
                description = self.description,
                type = 1
            )

            r = await self.goldy.http_client._request(
                Route(
                    "POST",
                    "/applications/{application_id}/guilds/{guild_id}/commands",
                    application_id = self.goldy.application_data["id"],
                    guild_id = guild[0],
                ),
                rate_limit_key = self.goldy.nc_authentication.rate_limit_key,
                headers = {"Authorization": str(self.goldy.nc_authentication)},
                json = payload
            )

            list_of_application_command_data.append(
                (
                    guild[0],
                    await r.json()
                )
            )

            self.logger.debug(f"Created slash for guild '{guild[1]}'.")

        # Set event listener for slash command.
        # --------------------------------------
        self.goldy.shard_manager.event_dispatcher.add_listener(
            self.__invoke_slash,
            event_name="INTERACTION_CREATE"
        )

        self.list_of_application_command_data = list_of_application_command_data
        return list_of_application_command_data
    

    async def remove_slash(self) -> None:
        """Un-registers the slash command."""
        self.logger.debug(f"Removing slash command for '{self.name}'...")

        for slash_command in self.list_of_application_command_data:

            await self.goldy.http_client._request(
                Route(
                    "GET",
                    "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                    application_id = self.goldy.application_data["id"],
                    guild_id = slash_command[0],
                    command_id = slash_command[1]["id"],
                ),
                rate_limit_key = self.goldy.nc_authentication.rate_limit_key,
                headers = {"Authorization": str(self.goldy.nc_authentication)}
            )

            self.logger.debug(f"Deleted slash for guild with id '{slash_command[0]}'.")

        # Remove event listener for slash command.
        # --------------------------------------
        self.goldy.shard_manager.event_dispatcher.remove_listener(
            self.__invoke_slash,
            event_name="INTERACTION_CREATE"
        )

        return None
    

    def create_normal(self) -> None:
        """Creates and registers a normal on-msg/prefix command in goldy bot. Also know as a prefix command. E.g.``!goldy``"""
        self.logger.debug(f"Creating normal/prefix command for '{self.name}'...")

        self.goldy.shard_manager.event_dispatcher.add_listener(
            self.__invoke_prefix,
            event_name="MESSAGE_CREATE"
        )

        return None
    

    def remove_normal(self) -> None:
        """Un-registers the prefix command."""
        self.logger.debug(f"Removing normal/prefix command for '{self.name}'...")

        self.goldy.shard_manager.event_dispatcher.remove_listener(
            self.__invoke_prefix,
            event_name="MESSAGE_CREATE"
        )

        return None


    async def load(self) -> None:
        """Loads and creates the command."""
        if self.allow_slash_cmd:
            await self.create_slash()

        if self.allow_prefix_cmd:
            self.create_normal()

        if self.extension is not None:
            self.extension.add_command(self)

        self.__loaded = True

        self.logger.info(
            f"Command '{self.name}' has been loaded!"
        )

        return None
    

    async def unload(self) -> None:
        """Unloads and removes the command."""

        if self.allow_slash_cmd:
            await self.remove_slash()

        if self.allow_prefix_cmd:
            self.remove_normal()

        self.__loaded = False

        self.logger.debug(
            f"Command '{self.name}' has been unloaded!"
        )

        return None
    
    async def delete(self) -> None:
        """Completely deletes this command. Unloads it and removes it from cache."""
        await self.unload()

        commands_cache.remove((self.name, self))

        self.logger.info(
            f"Command '{self.name}' has been deleted!"
        )
    
    # Where I left off.
    # TODO: Use code from goldy bot v4 to fill the rest.
    # Like argument missing detection for prefix commands.

    def any_args_missing(self, command_executers_args:tuple) -> bool:
        """Checks if the args given by the command executer matches what parameters the command needs."""
        if len(command_executers_args) == len(self.params[1:]):
            return True
        else:
            return False

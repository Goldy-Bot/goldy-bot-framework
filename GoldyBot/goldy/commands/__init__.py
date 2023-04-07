from __future__ import annotations

from devgoldyutils import Colours
from typing import List, Callable, Tuple, TYPE_CHECKING, Dict
from discord_typings import ApplicationCommandData, MessageData, InteractionData, ApplicationCommandPayload, ApplicationCommandOptionData, ApplicationCommandOptionInteractionData
from discord_typings.interactions.commands import ChoicesStringOptionData

from nextcore.http import Route

from .. import utils, nextcore_utils
from ..nextcore_utils import front_end_errors
from ..objects import GoldenPlatter, PlatterType
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
        goldy: Goldy, 
        func, 
        name: str = None, 
        description: str = None, 
        required_roles: List[str] = None, 
        slash_options: Dict[str, ApplicationCommandOptionData] = None,
        allow_prefix_cmd: bool = True, 
        allow_slash_cmd: bool = True, 
        parent_cmd: Command = None
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
        self.slash_options = slash_options
        """Allows you to customize slash command arguments and make them beautiful 🥰."""
        self.allow_prefix_cmd = allow_prefix_cmd
        """If the creation of a prefix command is allowed."""
        self.allow_slash_cmd = allow_slash_cmd
        """If the creation of a slash command is allowed."""
        self.parent_cmd = parent_cmd
        """Command object of the parent command if this command is a subcommand."""

        self.goldy = goldy
        self.logger = LoggerAdapter(
            LoggerAdapter(goldy_bot_logger, prefix="Command"), 
            prefix = Colours.GREY.apply((lambda x: self.func.__name__ if x is None else x)(self.name))
        )

        # If cmd_name is null, set it to function name.
        if self.name is None:
            self.name = self.func.__name__
        
        if self.description is None:
            self.description = "This command has no description. Sorry about that."

        if self.required_roles is None:
            self.required_roles = []

        if self.slash_options is None:
            self.slash_options = {}
        
        # Get list of function params.
        self.params = list(self.func.__code__.co_varnames)
        
        # Check if command is inside extension by checking if self is first parameter.
        self.__in_extension = False

        if self.params[0] == "self":
            self.__in_extension = True
            self.params.pop(0)

        self.params.pop(0) # Remove 'platter' argument.

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
            return (lambda x: x[1] if x is not None else None)(utils.cache_lookup(self.extension_name, extensions_cache))
        
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

    async def invoke(self, gold_platter: GoldenPlatter) -> bool:
        """Runs/triggers this command. This method is mostly supposed to be used internally."""
        self.logger.debug(f"Attempting to invoke '{gold_platter.type.name}'...")

        if self.__got_perms(gold_platter):

            # Prefix/normal command.
            # ------------------------
            if gold_platter.type.value == PlatterType.PREFIX_CMD.value:
                data:MessageData = gold_platter.data

                self.logger.info(
                    Colours.BLUE.apply(
                        f"Prefix command invoked by '{data['author']['username']}#{data['author']['discriminator']}'."
                    )
                )

                params = nextcore_utils.invoke_data_to_params(data, gold_platter.type)

                # Run callback.
                # --------------
                try:

                    if self.in_extension:
                        await self.func(self.extension, gold_platter, *params)
                    else:
                        await self.func(gold_platter, *params)

                except TypeError as e:
                    # This could mean the args are missing or it could very well be a normal type error so let's check and handle it respectively.
                    if f"{self.func.__name__}() missing" in e.args[0]:
                        # If params are missing raise MissingArgument exception.
                        raise front_end_errors.MissingArgument(
                            missing_args = self.params[len(params):], 
                            platter = gold_platter, 
                            logger = self.logger
                        )
                    
                    if f"{self.func.__name__}() takes from" in e.args[0]:
                        raise front_end_errors.TooManyArguments(
                            platter = gold_platter, 
                            logger = self.logger
                        )

                    raise e

            # Slash command.
            # ----------------
            if gold_platter.type.value == PlatterType.SLASH_CMD.value:
                data:InteractionData = gold_platter.data

                self.logger.info(
                    Colours.CLAY.apply(
                        f"Slash command invoked by '{data['member']['user']['username']}#{data['member']['user']['discriminator']}'."
                    )
                )
                
                params = nextcore_utils.invoke_data_to_params(data, gold_platter.type)

                # Run callback.
                # --------------
                if self.in_extension:
                    await self.func(self.extension, gold_platter, **params)
                else:
                    await self.func(gold_platter, **params)

                return True
        
        # Member has no perms.
        # TODO: Add no perms discord message.

        return False
    
    def __got_perms(self, platter: GoldenPlatter) -> bool:
        """Internal method that checks if the command author has the perms to run this command."""

        if not self.required_roles == []:

            # If the required roles contain 'bot_dev' and the bot dev is running the command allow the command to execute.
            # --------------------------------------------------------------------------------------------------------------
            if "bot_dev" in self.required_roles:
                if platter.author.id == self.goldy.config.bot_dev:
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

        # Creating payload.
        # ------------------
        payload = ApplicationCommandPayload(
            name = self.name,
            description = self.description,
            options = nextcore_utils.params_to_options(self),
            type = 1
        )

        # Add slash command for each allowed guild.
        # -------------------------------------------
        for guild in self.goldy.guilds.allowed_guilds:

            r = await self.goldy.http_client.request(
                Route(
                    "POST",
                    "/applications/{application_id}/guilds/{guild_id}/commands",
                    application_id = self.goldy.application_data["id"],
                    guild_id = guild[0],
                ),
                rate_limit_key = self.goldy.nc_authentication.rate_limit_key,
                headers = self.goldy.nc_authentication.headers,
                json = payload
            )

            list_of_application_command_data.append(
                (
                    guild[0],
                    await r.json()
                )
            )

            self.logger.debug(f"Created slash for guild '{guild[1]}'.")

        self.list_of_application_command_data = list_of_application_command_data
        return list_of_application_command_data
    
    async def remove_slash(self) -> None:
        """Un-registers the slash command."""
        self.logger.debug(f"Removing slash command for '{self.name}'...")

        for slash_command in self.list_of_application_command_data:

            await self.goldy.http_client.request(
                Route(
                    "GET",
                    "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                    application_id = self.goldy.application_data["id"],
                    guild_id = slash_command[0],
                    command_id = slash_command[1]["id"],
                ),
                rate_limit_key = self.goldy.nc_authentication.rate_limit_key,
                headers = self.goldy.nc_authentication.headers
            )

            self.logger.debug(f"Deleted slash for guild with id '{slash_command[0]}'.")

        return None


    async def load(self) -> bool:
        """Loads and creates the command."""
        if self.in_extension:

            if self.extension is None: # If the extension doesn't don't load this command.
                self.logger.warn(
                    f"Not loading command '{self.name}' because the extension '{self.extension_name}' is being ignored or has failed to load!"
                )
                return False

            self.extension.commands.append(self)
            self.logger.debug(f"Added to extension '{self.extension.code_name}'.")

        if self.allow_slash_cmd:
            await self.create_slash()

        self.__loaded = True

        self.logger.info(
            f"Command '{self.name}' has been loaded!"
        )

        return True
    

    async def unload(self) -> None:
        """Unloads and removes the command from cache."""

        if self.allow_slash_cmd:
            await self.remove_slash()

        self.__loaded = False

        commands_cache.remove((self.name, self))

        self.logger.debug(
            f"Command '{self.name}' has been unloaded!"
        )

        return None

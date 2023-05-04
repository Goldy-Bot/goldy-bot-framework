from __future__ import annotations

from devgoldyutils import Colours
from typing import List, Callable, Tuple, TYPE_CHECKING, Dict
from discord_typings import ApplicationCommandData, MessageData, InteractionData, ApplicationCommandPayload, ApplicationCommandOptionData, GuildMemberData

from nextcore.http import Route
from nextcore.http.errors import BadRequestError

from .. import utils, nextcore_utils
from ..nextcore_utils import front_end_errors
from ..objects import GoldPlatter, PlatterType
from ... import LoggerAdapter, goldy_bot_logger
from ..extensions import Extension, extensions_cache

if TYPE_CHECKING:
    from ... import Goldy

commands_cache: List[Tuple[str, object]] = []
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
        else:
            # This makes sure the GoldyBot.Perms enum objects are converted to their string values.
            self.required_roles = [str(role) for role in self.required_roles]

        if self.slash_options is None:
            self.slash_options = {}

        self.params = nextcore_utils.get_function_parameters(self)
        """List of command function parameters."""

        commands_cache.append(
            (self.name, self)
        )

        self.__loaded = False

        self.logger.debug("Command initialized!")

    @property
    def extension_name(self) -> str:
        """Returns extension's code name."""
        return str(self.func).split(" ")[1].split(".")[0]

    @property
    def extension(self) -> Extension | None:
        """Finds and returns the object of the command's extension. Returns None if command's extension is not found."""
        return (lambda x: x[1] if x is not None else None)(utils.cache_lookup(self.extension_name, extensions_cache))
    
    @property
    def slash_cmd_payload(self):
        """Returns the payload needed to create a slash command."""
        return ApplicationCommandPayload(
            name = self.name,
            description = self.description,
            options = nextcore_utils.params_to_options(self),
            type = 1
        )
    
    @property
    def is_loaded(self) -> bool:
        """Returns whether the command has been loaded by the command loader or not."""
        return self.__loaded

    @property
    def is_child(self):
        """Returns if command is child or not. Basically is it a subcommand or not, essentially."""
        if self.parent_cmd is None:
            return False
        else:
            return True


    async def invoke(self, gold_platter: GoldPlatter) -> None:
        """Runs/triggers this command. This method is usually used internally."""
        self.logger.debug(f"Attempting to invoke '{gold_platter.type.name}'...")

        if await self.__got_perms(gold_platter):

            # Prefix/normal command.
            # ------------------------
            if gold_platter.type.value == PlatterType.PREFIX_CMD.value:
                data:MessageData = gold_platter.data

                self.logger.info(
                    Colours.BLUE.apply(
                        f"Prefix command invoked by '{data['author']['username']}#{data['author']['discriminator']}'."
                    )
                )

                params = await nextcore_utils.invoke_data_to_params(data, gold_platter)

                # Run callback.
                # --------------
                try:

                    await self.func(self.extension, gold_platter, *params)

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
                    
                    # TODO: When exceptions raise in commands wrap them in a goldy bot command exception.
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
                
                params = await nextcore_utils.invoke_data_to_params(data, gold_platter)

                # Run callback.
                # --------------
                await self.func(self.extension, gold_platter, **params)

            return True
        
        # If member has no perms raise MissingPerms exception.
        raise front_end_errors.MissingPerms(gold_platter, self.logger)
    
    async def __got_perms(self, platter: GoldPlatter) -> bool:
        """Internal method that checks if the command author has the perms to run this command."""
        logger = LoggerAdapter(self.logger, prefix=Colours.PURPLE.apply("Permission System"))

        if not self.required_roles == []:
            logger.debug("Checking if member has perms...")

            # If the required roles contain 'bot_dev' and the bot dev is running the command allow the command to execute.
            # --------------------------------------------------------------------------------------------------------------
            if "bot_dev" in self.required_roles:
                if platter.author.id == self.goldy.config.bot_dev:
                    return True

            # Check if member has any of the required roles.
            #----------------------------------------------------

            # Get the member's guild data.
            r = await self.goldy.http_client.request(
                Route(
                    "GET",
                    "/guilds/{guild_id}/members/{user_id}",
                    guild_id = platter.guild.id,
                    user_id = platter.author.id
                ),
                rate_limit_key = self.goldy.nc_authentication.rate_limit_key,
                headers = self.goldy.nc_authentication.headers,
            )

            member_data: GuildMemberData = await r.json()

            for role_code_name in self.required_roles:

                if role_code_name not in ["bot_dev"]:
                    try:
                        role_id_uwu = platter.guild.roles[role_code_name]
                    except KeyError:
                        # Maybe there is a better way of handling this but I'll leave this as temporary solution for now.
                        logger.error(
                            f"This guild ({platter.guild.code_name}) hasn't been configured to include the required role '{role_code_name}' you entered for the command '{self.name}'."
                        )
                        return False

                    # Loop through each role of the member and check if the role id is equal to that required.
                    for member_role_id in member_data["roles"]:
                        if str(member_role_id) == role_id_uwu:
                            logger.debug(f"The author has the required role '{role_code_name}'.")
                            return True
                    

                    # TODO: Might be better to create a Role() object and add a .has_role() method to Member object.

            return False
        
        return True

    async def unload(self) -> None:
        """Unloads and removes the command from cache."""

        self.__loaded = False

        commands_cache.remove(
            (self.name, self)
        )

        self.logger.debug(
            f"Command '{self.name}' has been unloaded and removed from cache!"
        )

        return None

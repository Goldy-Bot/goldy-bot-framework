from __future__ import annotations

from devgoldyutils import Colours
from typing import List, Callable, Tuple, TYPE_CHECKING, Dict
from discord_typings import MessageData, InteractionData, ApplicationCommandPayload, ApplicationCommandOptionData, GuildMemberData

from nextcore.http import Route
from nextcore.http.errors import BadRequestError

from . import params_utils
from .. import utils
from ..nextcore_utils import front_end_errors
from ..objects import GoldPlatter, PlatterType
from ... import LoggerAdapter, goldy_bot_logger
from ..extensions import Extension, extensions_cache

if TYPE_CHECKING:
    from ... import Goldy, SlashOption

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
        hidden: bool = False,
        parent_cmd: Command = None
    ):
        """A class representing a GoldyBot command."""
        self.func: Callable = func
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
        self.hidden = hidden
        """Should this command be hidden? For slash commands the command is just set to admins only."""
        self.parent_cmd = parent_cmd
        """Command object of the parent command if this command is a subcommand."""

        self.goldy = goldy
        self.logger = LoggerAdapter(
            LoggerAdapter(goldy_bot_logger, prefix="Command"), 
            prefix = Colours.GREY.apply((lambda x: self.func.__name__ if x is None else x)(self.name))
        )
        self.sub_commands: List[Tuple[str, Command]] = []
        """A tuple list of this commands's child commands."""

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

        self.params = params_utils.get_function_parameters(self)
        """List of command function parameters."""
        
        if self.parent_cmd is not None:
            self.parent_cmd.sub_commands.append(
                (self.name, self)
            )
            self.logger.debug(f"Command '{self.name}' was added to the command '{self.parent_cmd.name}' as a sub command.")
        else:
            commands_cache.append(
                (self.name, self)
            )

        self.__loaded = True

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
    def slash_cmd_payload(self) -> ApplicationCommandPayload:
        """Returns the payload needed to create a slash command."""
        return ApplicationCommandPayload(
            name = self.name,
            description = self.description,
            options = params_utils.params_to_options(self) + [sub_command[1].slash_cmd_payload for sub_command in self.sub_commands], # TODO: Add subcommands to this.
            default_member_permissions = str(1 << 3) if self.hidden else None,
            type = 1
        )

    @property
    def is_loaded(self) -> bool:
        """Returns whether the command has been loaded by the command loader or not."""
        return self.__loaded

    @property
    def is_child(self) -> bool:
        """Returns if command is child or not. Basically is it a subcommand or not, essentially."""
        if self.parent_cmd is None:
            return False

        return True

    @property
    def is_parent(self) -> bool:
        """Returns if the command is a parent of a sub command or not."""
        if len(self.sub_commands) >= 1:
            return True

        return False

    @property
    def command_usage(self) -> str:
        command_args_string = " "
        for param in self.params:
            command_args_string += f"{{{param}}} "

        command_sub_cmds_string = "<"
        for sub_cmd in self.sub_commands:
            command_sub_cmds_string += f"{sub_cmd[0]}|"

        if len(command_sub_cmds_string) >= 2:
            command_sub_cmds_string = command_sub_cmds_string[:-1] + "> "

        return f"{self.parent_cmd.name + ' ' if self.is_child else ''}{self.name} {command_args_string[:-1]}{command_sub_cmds_string[:-1]}"


    def sub_command(
        self,
        name: str = None, 
        description: str = None, 
        required_roles: List[str]=None, 
        slash_options: Dict[str, SlashOption] = None
    ):
        """
        Create a sub command of this command with this decorator.
        
        ---------------
        
        ⭐ Example:
        -------------
        This is how you can create a sub command in GoldyBot::

            @GoldyBot.command()
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
        
        """
        def decorate(func):
            def inner(func) -> Command:
                command = Command(
                    goldy = self.goldy, 
                    func = func, 
                    name = name, 
                    description = description, 
                    required_roles = required_roles, 
                    slash_options = slash_options,
                    allow_prefix_cmd = self.allow_prefix_cmd, 
                    allow_slash_cmd = self.allow_slash_cmd,
                    parent_cmd = self
                )

                command.logger = LoggerAdapter(self.logger, prefix=Colours.ORANGE.apply(command.name))

                return command
            
            return inner(func)

        return decorate


    async def invoke(self, gold_platter: GoldPlatter) -> None:
        """Runs/triggers this command. This method is usually used internally."""
        self.logger.debug(f"Attempting to invoke '{gold_platter.type.name}'...")

        if gold_platter.guild.is_extension_allowed(gold_platter.command.extension) is False:
            raise front_end_errors.ExtensionNotAllowedInGuild(gold_platter, self.logger)

        if await self.__got_perms(gold_platter):

            # Prefix/normal command.
            # ------------------------
            if gold_platter.type.value == PlatterType.PREFIX_CMD.value:
                data: MessageData = gold_platter.data

                self.logger.info(
                    Colours.BLUE.apply(
                        f"Prefix command invoked by '{data['author']['username']}#{data['author']['discriminator']}'."
                    )
                )

                # Yep your right, parent commands of sub commands don't get any arguments. Ha, chew on that!
                params = (lambda x: x if self.is_parent is False else [])(params_utils.invoke_data_to_params(data, gold_platter))
                self.logger.debug(f"Got args --> {params}")

                # Run callback.
                # --------------
                try:
                    return_value = await self.func(self.extension, gold_platter, *params)

                    # Invoke sub command if there is one in invoke data.
                    if return_value is not False and self.is_parent is True:
                        await self.__invoke_sub_cmd(data, gold_platter)

                except TypeError as e:
                    # This could mean the args are missing or it could very well be a normal type error so let's check and handle it respectively.
                    if f"{self.func.__name__}() missing" in e.args[0]:
                        # If params are missing raise MissingArgument exception.
                        raise front_end_errors.MissingArgument(
                            missing_args = self.params[len(params):], 
                            platter = gold_platter, 
                            logger = self.logger
                        )

                    if f"{self.func.__name__}() takes" in e.args[0] or f"{self.extension_name}.{self.func.__name__}() takes" in e.args[0]:
                        raise front_end_errors.TooManyArguments(
                            platter = gold_platter, 
                            logger = self.logger
                        )
                    
                    # TODO: When exceptions raise in commands wrap them in a goldy bot command exception.
                    raise e 

            # Slash command.
            # ----------------
            if gold_platter.type.value == PlatterType.SLASH_CMD.value:
                data: InteractionData = gold_platter.data

                self.logger.info(
                    Colours.CLAY.apply(
                        f"Slash command invoked by '{data['member']['user']['username']}#{data['member']['user']['discriminator']}'."
                    )
                )
                
                params = params_utils.invoke_data_to_params(data, gold_platter)
                self.logger.debug(f"Got args --> {params}")

                # Run callback.
                # --------------
                return_value = await self.func(self.extension, gold_platter, **params)

                # Invoke sub command if there is one in invoke data.
                if return_value is not False and self.is_parent is True:
                    await self.__invoke_sub_cmd(data, gold_platter)

            return True
        
        # If member has no perms raise MissingPerms exception.
        raise front_end_errors.MissingPerms(gold_platter, self.logger)

    async def __invoke_sub_cmd(self, invoke_data: InteractionData | MessageData, platter: GoldPlatter):
        """Some goofy shit to invoke a sub command if it's in invoke data. Bio hazard inside, DO NOT LOOK!"""
        sub_cmd_data = invoke_data.copy()
        command: Tuple[str, Command] = None

        if platter.type.value == 1:
            for option in invoke_data["data"].get("options", []):
                if option["type"] == 1:
                    command = utils.cache_lookup(option["name"], self.sub_commands)

                    if command is not None:
                        sub_cmd_data["data"]["options"] = option["options"]
                        break

        else: # TODO: Now add this shit for prefix commands. 💀💀💀
            for arg in invoke_data["content"].split(" ")[1:]:
                command = utils.cache_lookup(arg, self.sub_commands)

                if command is not None:
                    sub_cmd_data["content"] = sub_cmd_data["content"].replace(arg, "")
                    break


        if command is not None:

            sub_cmd_platter = GoldPlatter(
                data = sub_cmd_data, 
                type = platter.type, 
                author = platter.author,
                command = command[1],
                goldy = self.goldy,
            )

            self.logger.debug(Colours.PINK_GREY.apply(f"Invoking sub command '{command[1].name}'."))

            await command[1].invoke(sub_cmd_platter)
            return None

        # Perhaps the user passed in the wrong sub command.
        raise front_end_errors.MissingArgument(["<sub_command>"], platter)
    
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

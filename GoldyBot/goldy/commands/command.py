from __future__ import annotations
from abc import abstractmethod
from typing import Callable, Any, List, Dict, TYPE_CHECKING
from discord_typings import ApplicationCommandOptionData

import regex
from devgoldyutils import LoggerAdapter, Colours

from ..extensions import extensions_cache
from ... import goldy_bot_logger, utils
from ..objects import Invokable
from ... import errors
from ..perms import Perms
from ..nextcore_utils import front_end_errors

if TYPE_CHECKING:
    from ... import Goldy, Extension
    from .. import objects

class Command(Invokable):
    """Class that all commands in goldy bot inherit from."""
    def __init__(
        self, 
        goldy: Goldy, 
        func: Callable[[Extension, objects.GoldPlatter], Any], 
        name: str = None, 
        description: str = None, 
        required_perms: List[Perms | str] = None, 
        slash_options: Dict[str, ApplicationCommandOptionData] = None, 
        hidden: bool = False, 
        pre_register = True
    ):
        self.func = func
        """The command's callback function."""

        self.extension_name = str(self.func).split(" ")[1].split(".")[0]
        """Returns extension's code name."""

        if name is None:
            name = func.__name__

        if description is None:
            description = "🪹 Oopsie daisy, looks like no description was set for this command."

        if required_perms is None:
            self.__required_perms = []
        else:
            self.__required_perms = required_perms

        if slash_options is None:
            self.__slash_options = {}
        else:
            self.__slash_options = slash_options

        self.__hidden = hidden

        self.__params = self.__get_function_parameters()

        self._parent_command = None
        self._is_loaded = False
        self.__is_disabled = False

        super().__init__(
            name, 
            {
                "name": name,
                "description": description,
                "options": self.params_to_options(),
                "default_member_permissions": str(1 << 3) if hidden else None,
                "type": 1
            }, 
            func,
            goldy, 
            LoggerAdapter(LoggerAdapter(goldy_bot_logger, prefix=self.__class__.__name__), prefix=Colours.PINK_GREY.apply(name)),
            pre_register
        )

    @property
    def name(self) -> str:
        """The command's code name."""
        return self.get("name")

    @property
    def description(self) -> str:
        """The command's set description. None if there is no description set."""
        return self.get("description")

    @property
    def required_perms(self):
        """The code names for the roles needed to access this command."""
        return self.__required_perms

    @property
    def slash_options(self):
        """Allows you to customize slash command arguments and make them beautiful 🥰."""
        return self.__slash_options

    @property
    def hidden(self):
        """Should this command be hidden? For slash commands the command is just set to admins only."""
        return self.__hidden
    
    @property
    def params(self) -> List[str]:
        """List of command function parameters."""
        return self.__params

    @property
    def extension(self) -> Extension | None:
        """Finds and returns the object of the command's extension. Returns None if the extension doesn't exits. (failed to load)"""
        return (lambda x: x[1] if x is not None else None)(
            utils.cache_lookup(self.extension_name, extensions_cache)
        )

    @property
    def is_loaded(self) -> bool:
        """Returns whether the command has been loaded by the command loader or not."""
        return self._is_loaded

    @property
    def is_disabled(self) -> bool:
        """Returns whether the command is disabled or not."""
        return self.__is_disabled

    @property
    def parent_command(self) -> Command | None:
        """Command object of the parent command if this command is a subcommand."""
        return self._parent_command

    @property
    def is_child(self) -> bool:
        """Returns if command is child or not. Basically is it a subcommand or not, in other words."""
        if self.parent_command is None:
            return False

        return True

    def disable(self) -> None:
        """A method to disable this command."""
        self.__is_disabled = True
        self.logger.debug(Colours.GREY.apply("Command has been disabled!"))

    def enable(self) -> None:
        """A method to enable this command."""
        self.__is_disabled = False
        self.logger.debug(Colours.GREEN.apply("Command has been enabled!"))

    def delete(self):
        """Method to remove/delete command."""
        self.unregister()

    @abstractmethod
    def register_sub_command(self, command: Command) -> None:
        """
        Method that is called when a sub command want's to register.

        You must override this to handle it for your command type.
        """
        ...

    @abstractmethod
    async def invoke(self, platter: objects.GoldPlatter, lambda_func: Callable) -> None:
        self.logger.debug("Attempting to invoke command...")

        if await platter.guild.is_extension_allowed(self.extension) is False:
            raise front_end_errors.ExtensionNotAllowedInGuild(platter, self.logger)

        if self.is_disabled:
            raise front_end_errors.CommandIsDisabled(platter, self.logger)

        # I'm using a lambda function here so all the parameter bullshit 
        # can be handled by the child class instead of this method.
        if await self.goldy.permission_system.got_perms(platter):
            self.logger.info(
                Colours.BLUE.apply(
                    f"Command invoked by '{platter.author.username}#{platter.author.discriminator}'."
                )
            )
            return await lambda_func()

        # If member has no perms raise MissingPerms exception.
        raise front_end_errors.MissingPerms(platter, self.logger)


    def __get_function_parameters(self) -> List[str]:
        """Returns the function parameters of a command respectively."""
        
        # Get list of function params.
        func_params = list(self.func.__code__.co_varnames)
        
        # Removes 'self' argument.
        func_params.pop(0)

        # Removes 'platter' argument.
        func_params.pop(0)

        # Filters out other variables resulting in just function parameters. It's weird I know.
        params = func_params[:self.func.__code__.co_argcount - 2]

        return params
    
    def params_to_options(self) -> List[ApplicationCommandOptionData]:
        """A function that converts slash command parameters to slash command options."""
        options: List[ApplicationCommandOptionData] = []

        # Discord chat input regex as of https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-naming
        chat_input_patten = regex.compile(r"^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$", regex.UNICODE)

        for param in self.params:
            if param.isupper() or bool(chat_input_patten.match(param)) is False: # Uppercase parameters are not allowed in the discord API.
                raise errors.InvalidParameter(self, param)

            if param in self.slash_options:
                option_data = self.slash_options[param]
                
                if option_data.get("name") is None:
                    option_data["name"] = param

                options.append(
                    option_data
                )
            
            else:
                options.append({
                    "name": param,
                    "description": "This option has no description. Sorry about that.",
                    "type": 3,
                    "required": True,
                })

        return options
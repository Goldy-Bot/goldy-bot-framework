from __future__ import annotations
from typing import Any, Callable, List, TYPE_CHECKING
from discord_typings import MessageData

from .. import objects
from ..nextcore_utils import front_end_errors

if TYPE_CHECKING:
    from .. import Goldy
    from ... import Extension

from .command import Command

class PrefixCommand(Command):
    def __init__(
        self, 
        goldy: Goldy, 
        func: Callable[[Extension, objects.GoldPlatter], Any], 
        name: str = None, 
        description: str = None, 
        required_perms: List[str] = None, 
        hidden: bool = False,
        pre_register: bool = True
    ):
        self.__sub_commands: List[PrefixCommand] = []

        super().__init__(
            goldy = goldy, 
            func = func, 
            name = name, 
            description = description, 
            required_perms = required_perms, 
            hidden = hidden,
            pre_register = pre_register
        )

        self.logger.debug("Prefix command has been initialized!")

    @property
    def command_usage(self) -> str:
        command_args_string = " "
        for param in self.params:
            command_args_string += f"{{{param}}} "

        command_sub_cmds_string = "<"
        for sub_cmd in self.__sub_commands:
            command_sub_cmds_string += f"{sub_cmd.name}|"

        if len(command_sub_cmds_string) >= 2:
            command_sub_cmds_string = command_sub_cmds_string[:-1] + "> "

        return f"{self.parent_command.name + ' ' if self.is_child else ''}{self.name} {command_args_string[:-1]}{command_sub_cmds_string[:-1]}"


    def register_sub_command(self, command: PrefixCommand) -> None:
        """Method that registers prefix sub command."""
        command._parent_command = self
        self.__sub_commands.append(command)


    async def invoke(self, platter: objects.GoldPlatter) -> None:
        """Runs and triggers a slash command. This method is usually ran internally."""
        data: MessageData = platter.data

        params = self.__invoke_data_to_params(data)
        if not params == []: self.logger.debug(f"Got args --> {params}")

        try:
            return_value = await super().invoke(
                platter, lambda: self.func(platter.invokable.extension, platter, *params)
            )

            # Handle sub commands.
            # ----------------------
            # Invoke sub command if there is one in invoke data.
            if return_value is not False:
                await self.__invoke_sub_command(data, platter)

        except TypeError as e:
            # This could mean the args are missing or it could very well be a normal type error so let's check and handle it respectively.
            if f"{self.func.__name__}() missing" in e.args[0]:
                # If params are missing raise MissingArgument exception.
                raise front_end_errors.MissingArgument(
                    missing_args = self.params[len(params):], 
                    platter = platter, 
                    logger = self.logger
                )

            # The or condition is here because of newer python versions.
            if f"{self.func.__name__}() takes" in e.args[0] or f"{self.extension_name}.{self.func.__name__}() takes" in e.args[0]:
                raise front_end_errors.InvalidArguments(
                    platter = platter, 
                    logger = self.logger
                )

            raise front_end_errors.UnknownError(platter, logger = self.logger)

        except Exception as e:
            raise front_end_errors.UnknownError(platter, e, self.logger)

    async def __invoke_sub_command(self, data: MessageData, platter: objects.GoldPlatter) -> None:
        for arg in data["content"].split(" ")[1:]:
            for command in self.__sub_commands:
                if command.name == arg:
                    data["content"] = data["content"].replace(arg, "")
        
                    self.logger.debug("Calling sub command...")

                    platter = objects.GoldPlatter(
                        data = data, 
                        author = platter.author,
                        invokable = command,
                    )

                    await command.invoke(platter)
                    break


    def __invoke_data_to_params(self, data: MessageData) -> List[str]: 
        """A function that grabs prefix command arguments from invoke data and converts it to appropriate params."""
        self.logger.debug("Attempting to phrase invoke data into parameters...")

        # Where all the fucking magic happens.
        params = []

        # Yep your right, parent commands of sub commands don't get any arguments. Ha, chew on that!
        if len(self.__sub_commands) > 0:
            self.logger.debug("This command is a parent command so it won't be given arguments when ran.")
            return []

        for arg in data["content"].split(" ")[1:]:
            # Ignore sub commands.
            if arg in [x.name for x in self.__sub_commands]:
                self.logger.debug(f"Not phrasing the argument '{arg}' as it is a sub command.")
                continue

            # A really weird check I know but I promise it's needed okay.
            if arg == "" or arg[0] == " ":
                self.logger.debug(f"Not phrasing the argument '{arg}' as it is either blank or incorrect.")
                continue

            # If the argument is a user, a channel or a role strip the id from the mention. (Yes this means normal args can't start with these)
            if arg[:2] in ["<@", "<#"]:
                params.append(arg[2:-1])
            else:
                params.append(arg)

            self.logger.debug(f"Found arg '{arg}'.")

        return params
from __future__ import annotations

from typing import TYPE_CHECKING
from devgoldyutils import Colours

from . import goldy_bot_logger, log

if TYPE_CHECKING:
    from .goldy.commands.command import Command

class GoldyBotError(Exception):
    """Raises whenever there's a known error in goldy bot."""
    def __init__(self, message:str, logger:log.Logger=None):
        message = Colours.RED.apply_to_string(message)

        if logger is None:
            logger = goldy_bot_logger
        
        logger.error(message)
        super().__init__(message)


class InvalidTypeInMethod(GoldyBotError):
    """Raises whenever there is an invalid typing being inputted. Is normally is found in GoldyBot methods that default to None in it's arguments."""
    def __init__(self, message):
        super().__init__(
            f"You entered an invalid type in a method >> {message}"
        )


class InvalidParameter(GoldyBotError):
    """Raises whenever there is an invalid parameter in a command. Normally occurs when you have uppercase characters in a command argument."""
    def __init__(self, command: Command, invalid_param: str):
        super().__init__(
            f"The parameter used in the command '{command.name}' is NOT allowed >> {invalid_param}",
            logger = command.logger
        )


class NotSupportedYetForSlash(GoldyBotError):
    """Raises whenever there is an operation that isn't supported just yet for slash commands."""
    def __init__(self, operation, logger:log.Logger=None):
        super().__init__(
            f"'{operation}' is not supported yet for slash commands! Will be supported soon...",
            logger = logger
        )
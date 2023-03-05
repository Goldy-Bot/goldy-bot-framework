from devgoldyutils import Colours
from . import goldy_bot_logger, log

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
from devgoldyutils import Colours
from . import goldy_bot_logger

class GoldyBotError(Exception):
    """Raises whenever there's a known error in goldy bot."""
    def __init__(self, message:str):
        message = Colours.RED.apply_to_string(message)
        
        goldy_bot_logger.error(message)
        super().__init__(message)
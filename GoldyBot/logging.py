import logging as log
from devgoldyutils import Colours, add_custom_handler, LoggerAdapter

LOGGER_NAME = f"{Colours.YELLOW.value}Goldy {Colours.ORANGE.value}Bot{Colours.RESET_COLOUR.value}"

goldy_bot_logger = add_custom_handler(log.getLogger(LOGGER_NAME), level=log.DEBUG)
"""The logger object for Goldy Bot."""
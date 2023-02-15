"""
💛 Goldy Bot V5 - Rewrite of Goldy Bot V4

Copyright (C) 2023 - Goldy
"""
from devgoldyutils import Colours

from .logging import add_custom_handler, log, LoggerAdapter

LOGGER_NAME = f"{Colours.YELLOW.value}Goldy {Colours.ORANGE.value}Bot{Colours.RESET_COLOUR.value}"

goldy_bot_logger = add_custom_handler(log.getLogger(LOGGER_NAME)); goldy_bot_logger.setLevel(log.DEBUG)
"""The logger object for Goldy Bot."""

from .info import VERSION, DISPLAY_NAME
from .paths import Paths

from .goldy import Goldy, Token, get_goldy_instance
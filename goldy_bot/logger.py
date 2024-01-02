import logging as log
from devgoldyutils import Colours, add_custom_handler

__all__ = (
    "goldy_bot_logger",
)

goldy_bot_logger = add_custom_handler(
    log.getLogger(f"{Colours.YELLOW.value}Goldy {Colours.ORANGE.value}Bot{Colours.RESET_COLOUR.value}"), 
    level = log.DEBUG
)
"""
The logger object for Goldy Bot 🥞 Pancake.
"""
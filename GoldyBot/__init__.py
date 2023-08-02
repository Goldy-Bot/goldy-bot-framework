"""
💛 Goldy Bot V5 - Rewrite of Goldy Bot V4

Copyright (C) 2023 - Goldy
"""
from .logging import LoggerAdapter, log, goldy_bot_logger, LOGGER_NAME

from .info import VERSION, DISPLAY_NAME, __version__
from .paths import Paths

from .goldy import Goldy, get_goldy_instance
from .goldy.token import Token
from .goldy.perms import Perms
from .goldy.extensions import Extension
from .goldy.commands.decorator import command
from .goldy.commands.group_command import GroupCommand
from .utils import *

# Recipes
# --------
from .goldy.recipes import Recipe
from .goldy.recipes.buttons.button import Button, ButtonStyle

# Database
# ----------
from .goldy.database import DatabaseEnums
from .goldy.database.wrappers import DatabaseWrapper

# Nextcore utils and api wrappers.
# ----------------------------------
from .goldy import nextcore_utils
from .goldy.nextcore_utils import (
    Colours,
    File,
    Embed, EmbedField, EmbedImage, EmbedFooter,
    SlashOption, SlashOptionChoice, SlashOptionTypes,
    SlashOptionAutoComplete,
    send_msg, delete_msg,
    get_channel, get_channels, delete_channel,
    front_end_errors
)

# Objects
# ---------
from .goldy import objects
from .goldy.objects import (
    GoldPlatter, Ctx, Context,
    Channel,
    Message,
    Member
)
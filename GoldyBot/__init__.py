"""
💛 Goldy Bot V5 - Rewrite of Goldy Bot V4

Copyright (C) 2023 - Goldy
"""
from devgoldyutils import Colours

from .logging import LoggerAdapter, log, goldy_bot_logger, LOGGER_NAME

from .info import VERSION, DISPLAY_NAME
from .paths import Paths

from .goldy import Goldy, get_goldy_instance
from .goldy.token import Token
from .goldy.extensions import Extension
from .goldy.commands.decorator import command
from .goldy.utils import *

from .goldy.nextcore_utils import ( Embed, send_msg, delete_msg )

from .goldy.objects.gold_platter import GoldPlatter, PlatterType
from .goldy.objects.message import Message
from .goldy.objects.member import Member

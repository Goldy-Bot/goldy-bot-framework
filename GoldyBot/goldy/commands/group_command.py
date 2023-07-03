from __future__ import annotations
from typing import Any, Callable, Dict, List, TYPE_CHECKING
from discord_typings import ApplicationCommandOptionData, InteractionData

from devgoldyutils import Colours, LoggerAdapter

if TYPE_CHECKING:
    from .. import Goldy, objects
    from ... import Extension

from . import params_utils
from .slash_command import SlashCommand
from .prefix_command import PrefixCommand
from ... import get_goldy_instance, goldy_bot_logger

class GroupCommand():
    def __init__(
        self, 
        name: str = None, 
        description: str = None, 
        required_roles: List[str] = None, 
        slash_options: Dict[str, ApplicationCommandOptionData] = None, 
        slash_cmd_only: bool = False, 
        hidden: bool = False
    ):
        self.goldy = get_goldy_instance()
        self.logger = LoggerAdapter(goldy_bot_logger, prefix="GroupCommand")

        self.command = (
            SlashCommand(self.goldy),
            PrefixCommand(self.goldy) if slash_cmd_only else None
        )

        self.logger.debug("Group command has been initialized!")

    def sub_command(self):
        ...
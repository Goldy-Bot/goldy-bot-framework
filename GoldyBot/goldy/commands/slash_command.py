from __future__ import annotations
from typing import Any, Callable, Dict, List, TYPE_CHECKING

from discord_typings import ApplicationCommandOptionData

from GoldyBot.goldy import objects

if TYPE_CHECKING:
    from .. import Goldy, objects

from .command import Command

class SlashCommand(Command):
    def __init__(
        self, 
        goldy: Goldy, 
        func: Callable[[objects.GoldPlatter], Any], 
        name: str, 
        description: str, 
        required_roles: List[str], 
        slash_options: Dict[str, ApplicationCommandOptionData], 
        allow_prefix_cmd: bool, 
        hidden: bool
    ):
        super().__init__(
            goldy, 
            func, 
            name, 
            description, 
            required_roles, 
            slash_options, 
            allow_prefix_cmd, 
            hidden
        )

    async def invoke(self, platter: objects.GoldPlatter) -> None:
        ...
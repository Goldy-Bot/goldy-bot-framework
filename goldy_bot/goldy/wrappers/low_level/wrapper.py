from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...goldy import Goldy

from devgoldyutils import LoggerAdapter, Colours

from ....logger import goldy_bot_logger

from .user import User
from .channel import Channel
from .application import Application
from .interaction import Interaction
from .guild import Guild

__all__ = (
    "LowLevelWrapper",
)

class LowLevelWrapper(Application, User, Interaction, Channel, Guild):
    """A class that wraps common discord HTTP routes for the framework."""
    def __init__(self, goldy: Goldy) -> None:
        self.goldy = goldy
        self.logger = LoggerAdapter(goldy_bot_logger, prefix = Colours.GREY.apply("Low-Level"))

        super().__init__()
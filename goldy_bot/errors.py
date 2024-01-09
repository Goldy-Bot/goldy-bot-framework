from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Optional

    from logging import Logger

    from GoldyBot import Embed # TODO: Change to pancake embed object when available.

from GoldyBot.errors import GoldyBotError

from .logger import goldy_bot_logger

__all__ = (
    "GoldyBotError",
    "FrontEndError",
    "raise_or_error"
)

class FrontEndError(GoldyBotError):
    def __init__(
        self, 
        embed: Embed, 
        message: str, 
        logger: Optional[Logger] = None
    ):

        self.embed = embed

        super().__init__(message, logger)

def raise_or_error(
        message: str,
        condition: Callable[[], bool],
        logger: Optional[Logger] = None
    ) -> None:
    if logger is None:
        logger = goldy_bot_logger

    if condition():
        raise GoldyBotError(message, logger)

    logger.error(message)
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Optional

    from logging import Logger

from GoldyBot.errors import GoldyBotError

from .logger import goldy_bot_logger

__all__ = (
    "GoldyBotError",
    "raise_or_error"
)

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
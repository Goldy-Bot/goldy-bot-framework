from __future__ import annotations

from enum import Enum
from typing import Literal
from devgoldyutils import Colours

from . import Goldy
from ..errors import InvalidTypeInMethod
from .. import LoggerAdapter, goldy_bot_logger

class Status(Enum):
    """Goldy Bot enum class of nextcore status."""
    ONLINE = "online"
    IDLE = "idle"
    DND = "dnd"
    INVISIBLE = "invisible"

    # Aliases
    # ---------
    AWAY = IDLE
    DO_NOT_DISTURB = DND

    # TODO: Create some sort of class to pass into presence methods for changing all status so we can handle the arguments in the methods better.

class Presence():
    """Class that allows you to control the status, game activity and more of Goldy Bot"""
    def __init__(self, goldy:Goldy) -> None:
        self.goldy = goldy

        self.logger = LoggerAdapter(
            goldy_bot_logger, 
            prefix = Colours.BLUE.apply_to_string("Presence")
        )

    async def change(self, status:Status=None, afk:bool=None) -> None:
        """Updates the presence of Goldy Bot. Like e.g ``online, idle, dnd``."""
        if status is None and afk is None:
            raise InvalidTypeInMethod("arguments status and afk in 'presence.change()' cannot both be None.")

        self.logger.debug("Changing Goldy Bot presence...")

        old_presence = self.goldy.shard_manager.presence.copy()

        for shard in self.goldy.shard_manager.active_shards:
            presence = shard.presence

            if not status is None:
                if isinstance(status, Status):
                    presence["status"] = status.value

                elif isinstance(status, str):
                    presence["status"] = Status(status.lower()).value
                
                else:
                    raise InvalidTypeInMethod("status in 'presence.change()' has to be either Status enum or string.")
                    
            if not afk is None:
                presence["afk"] = afk

            await shard.presence_update(presence)
            self.logger.debug(f"Updated presence for shard {shard.shard_id}!")

        self.logger.info(f"Goldy Bot presence changed successfully from {old_presence} to {self.goldy.shard_manager.presence}!")
        return None
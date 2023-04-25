from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from devgoldyutils import Colours
from discord_typings import PartialActivityData

from . import Goldy
from ..errors import InvalidTypeInMethod
from .. import LoggerAdapter, goldy_bot_logger

class Status(Enum):
    """Goldy Bot enum class of discord status."""
    ONLINE = "online"
    IDLE = "idle"
    DND = "dnd"
    INVISIBLE = "invisible"

    # Aliases
    # ---------
    AWAY = IDLE
    DO_NOT_DISTURB = DND

    # TODO: Create some sort of class to pass into presence methods for changing all status so we can handle the arguments in the methods better.

class ActivityTypes(Enum):
    """Goldy Bot enum class of different discord activity types."""
    PLAYING_GAME = 0
    LIVE_ON_TWITCH = 1
    LISTENING_TO = 2
    WATCHING = 3

@dataclass
class Activity:
    """Goldy bot discord activity."""
    name:str
    type:ActivityTypes
    url:str|None = field(default=None)


class Presence():
    """Class that allows you to control the status, game activity and more of Goldy Bot"""
    def __init__(self, goldy: Goldy) -> None:
        self.goldy = goldy

        self.logger = LoggerAdapter(
            goldy_bot_logger, 
            prefix = Colours.BLUE.apply_to_string("Presence")
        )

        self.shard_manager = self.goldy.shard_manager

    async def change(self, status:Status|str = None, activity:Activity = None, afk:bool = None) -> None:
        """Updates the presence of Goldy Bot. Like e.g ``online, idle, dnd``."""
        self.logger.debug("Changing presence...")

        old_presence = self.shard_manager.presence.copy()
        presence = self.shard_manager.presence

        if status is not None:
            if isinstance(status, Status):
                presence["status"] = status.value

            elif isinstance(status, str):
                presence["status"] = Status(status.lower()).value
            
            else:
                # TODO: Let's remove this.
                raise InvalidTypeInMethod("status in 'presence.change()' has to be either Status enum or string.")
        
        if activity is not None:
            presence["activities"] = [
                PartialActivityData(
                    name=activity.name, 
                    type=(lambda x: x.value if isinstance(x, ActivityTypes) else x)(activity.type), 
                    url=activity.url
                )
            ]
                
        if afk is not None:
            presence["afk"] = afk

        for shard in self.shard_manager.active_shards:
            await shard.presence_update(presence)
            self.logger.debug(f"Updated for shard {shard.shard_id}.")

        self.logger.info(f"Presence changed from {old_presence} to {self.shard_manager.presence}!")
        return None
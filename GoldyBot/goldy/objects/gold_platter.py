from __future__ import annotations
from enum import Enum

from discord_typings import MessageData, InteractionData

class PlatterType(Enum):
    PREFIX_CMD = 0
    SLASH_CMD = 1

class GoldPlatter():
    """
    🟠 The gold platter is equivalent to the context/ctx/interaction name your used to. You can use the alias context/ctx if your not a fan of the FUNNY name. 
    It's actually returned on both interactions and normal message/prefix commands. You can use this object to grab the command author, reply to the command, send a message in the command's channel and a lot more.

    ⚡ With this class I'm able to handle both slash and prefix commands simultaneously.

    ✨ Behold the gold platter. ✨😁
    """
    def __init__(self, data:MessageData|InteractionData, type:PlatterType|int) -> None:
        self.data = data

        self.type:PlatterType = (lambda x: PlatterType(x) if isinstance(x, int) else x)(type)
    
    # TODO: Add send/reply method for both interaction and message command.
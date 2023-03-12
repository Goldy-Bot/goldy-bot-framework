from __future__ import annotations
from enum import Enum

from typing import TYPE_CHECKING
from discord_typings import MessageData, InteractionData

if TYPE_CHECKING:
    from ...goldy import Goldy
    from .message import Message
    from ..commands import Command


class PlatterType(Enum):
    PREFIX_CMD = 0
    SLASH_CMD = 1

class GoldPlatter():
    """
    🟡 The gold platter is equivalent to the context/ctx/interaction name your used to. You can use the alias context/ctx if your not a fan of the FUNNY name. 
    It's actually returned on both interactions and normal message/prefix commands. You can use this object to grab the command author, reply to the command, send a message in the command's channel and a lot more.

    ⚡ With this class I'm able to handle both slash and prefix commands simultaneously.

    ✨ Behold the gold platter. ✨😁
    """
    def __init__(self, data:MessageData|InteractionData, type:PlatterType|int, goldy:Goldy, command:Command) -> None:
        # TODO: We got to somehow test this stuff with pytest because this being error prone is sort of a catastrophe.

        self.data = data
        """The raw data received right from discord that triggered this prefix or slash command."""
        self.goldy = goldy
        """An instance of the goldy class."""
        self.command = command
        """The object for this command. 😱"""

        self.type:PlatterType = (lambda x: PlatterType(x) if isinstance(x, int) else x)(type)
        """The type of command this is."""

        if self.type.value == PlatterType.SLASH_CMD.value:
            self.author = Member(data["member"]["user"], goldy)
        else:
            self.author = Member(data["author"], goldy)

        self.interaction_responded = False
        """An internal property that is set by the ``nextcore_utils.send_msg()`` method when a slash command is responded to."""

    async def send_message(self, text:str, reply:bool=False) -> Message:
        return await nextcore_utils.send_msg(self, text, reply)


from .member import Member
from .. import nextcore_utils
from __future__ import annotations
from enum import Enum

from typing import TYPE_CHECKING, List
from discord_typings import MessageData, InteractionData, EmbedData

if TYPE_CHECKING:
    from ...goldy import Goldy
    from .message import Message
    from ..commands import Command
    from ..guilds import Guild


class PlatterType(Enum):
    PREFIX_CMD = 0
    SLASH_CMD = 1

class GoldenPlatter():
    """
    🟡 The golden platter is equivalent to the context/ctx/interaction name your used to. You can use the alias context/ctx if your not a fan of the FUNNY name. 
    It's actually returned on both interactions and normal message/prefix commands. You can use this object to grab the command author, reply to the command, send a message in the command's channel and a lot more.

    ⚡ With this class I'm able to handle both slash and prefix commands simultaneously.

    ✨ Behold the golden platter. ✨😁
    """
    def __init__(self, data:MessageData|InteractionData, type:PlatterType|int, goldy:Goldy, command:Command) -> None:
        # TODO: We got to somehow test this stuff with pytest because this being error prone is sort of a catastrophe.

        self.data = data
        """The raw data received right from discord that triggered this prefix or slash command."""
        self.goldy = goldy
        """An instance of the goldy class."""
        self.command = command
        """The object for this command. 😱"""

        self.type: PlatterType = (lambda x: PlatterType(x) if isinstance(x, int) else x)(type)
        """The type of command this is."""

        if self.type.value == PlatterType.SLASH_CMD.value:
            self.author = Member(data["member"]["user"], goldy)
        else:
            self.author = Member(data["author"], goldy)

        self.guild: Guild = self.goldy.guilds.get_guild(data["guild_id"])

        self.interaction_responded = False
        """An internal property that is set by the ``nextcore_utils.send_msg()`` method when a slash command is responded to."""

    async def send_message(self, text:str=None, embeds:List[EmbedData]=None, reply:bool=False, delete_after:float=None, **extra) -> Message:
        """
        Allows you to create and send a message to the channel the command was invoked from as a form of reply.
        
        ------------------

        Parameters
        ----------
        ``text``
            The content of the message.
        ``embeds``
            Embeds to include in the message.
        ``reply``
            Whether goldy bot should liberally reply to the message the command was invoked.
        ``delete_after``
            Deletes the message after this amount of seconds. 
        ``**extra``
            Allows you to pass the extra parameters that are missing.

        Returns
        -------
        ``GoldyBot.goldy.objects.message.Message``
            The message that was sent.
        
        """
        return await nextcore_utils.send_msg(self, text, embeds, reply, delete_after, **extra)


from .member import Member
from .. import nextcore_utils
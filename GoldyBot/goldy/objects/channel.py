from __future__ import annotations
from dataclasses import dataclass, field

from typing import TYPE_CHECKING, List
from discord_typings import ChannelData
from devgoldyutils import DictDataclass

from .. import goldy_bot_logger, LoggerAdapter

if TYPE_CHECKING:
    from . import Message
    from .. import Goldy
    from ..nextcore_utils.embeds.embed import Embed
    from ..recipes import Recipe
    from ..guilds.guild import Guild

logger = LoggerAdapter(goldy_bot_logger, prefix="Channel")

# TODO: Change this into a normal class.
@dataclass
class Channel(DictDataclass):
    data: ChannelData = field(repr=False)
    guild: Guild = field(repr=False)
    goldy: Goldy = field(repr=False)

    id: str = field(init=False)
    # TODO: Add more!

    mention: str = field(init=False)
    """This channel represented as a mention."""

    def __post_init__(self):
        super().__post_init__()

        self.logger = logger

        self.id = self.get("id")
        self.mention = f"<#{self.id}>"

    async def send_message(
        self, 
        text: str = None, 
        embeds: List[Embed] = None, 
        recipes: List[Recipe] = None, 
        reply: bool = False, 
        delete_after: float = None, 
        **extra
    ) -> Message:
        """
        Allows you to send a message to this channel.
        
        ------------------

        Parameters
        ----------
        ``text``
            The content of the message.
        ``embeds``
            Embeds to include in the message.
        ``recipes``
            Components to include in the message, e.g buttons and dropdowns.
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
        return await nextcore_utils.send_msg(self, text, embeds, recipes, reply, delete_after, **extra)

    async def delete(self, reason: str = None) -> Channel:
        return await nextcore_utils.delete_channel(self, reason)


from .. import nextcore_utils
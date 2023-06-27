from __future__ import annotations

from typing import TYPE_CHECKING, List
from discord_typings import MessageData, InteractionData

from . import Platter

if TYPE_CHECKING:
    from ..message import Message
    from ...guilds import Guild
    from ...nextcore_utils.components import Recipe
    from ...nextcore_utils.embeds.embed import Embed
    from ...commands import Command

class GoldPlatter(Platter):
    """
    🟡 The gold platter is equivalent to the context/ctx/interaction name your used to. You can use the alias context/ctx if your not a fan of the FUNNY name. 
    It's actually returned on both interactions and normal message/prefix commands. You can use this object to grab the command author, reply to the command, send a message in the command's channel and a lot more.

    ⚡ With this class I'm able to handle both slash and prefix commands simultaneously.

    ✨ Behold the golden platter. ✨😁
    """
    def __init__(self, data: MessageData|InteractionData, author: Member, command: Command) -> None:
        # TODO: We got to somehow test this stuff with pytest because this being error prone is sort of a catastrophe.
        super().__init__(
            data = data, 
            invoker = author, 
            invokable = command
        )

        self.guild: Guild = self.goldy.guild_manager.get_guild(self.get("guild_id"))

        self._interaction_responded = False
        """An internal property that is set by the :py:meth:`~GoldyBot.nextcore_utils.send_msg` method when a slash command is responded to."""

    @property
    def author(self) -> Member:
        """The member who triggered this command."""
        return self.invoker

    @property
    def command(self) -> Command:
        """The command object that was invoked."""
        return self.invokable

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
        Allows you to create and send a message to the channel the command was invoked from as a form of reply.
        
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


from ..member import Member
from ...goldy import nextcore_utils
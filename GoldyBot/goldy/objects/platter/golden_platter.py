from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Union
    from discord_typings import MessageData, InteractionData

    from ..member import Member
    from ...guilds import Guild
    from ..message import Message
    from ...recipes import Recipe
    from ...nextcore_utils.embeds.embed import Embed
    from ...nextcore_utils.files import File

    from ...commands.slash_command import SlashCommand
    from ...commands.prefix_command import PrefixCommand

    GOLD_PLATTER_INVOKABLE_TYPES = Union[SlashCommand, PrefixCommand, Recipe]

from . import Platter

class GoldPlatter(Platter):
    """
    🟡 The gold platter is equivalent to the context/ctx/interaction name your used to. You can use the alias context/ctx if your not a fan of the FUNNY name. 
    It's actually returned on both interactions and normal message/prefix commands. You can use this object to grab the command author, reply to the command, send a message in the command's channel and a lot more.

    ⚡ With this class I'm able to handle both slash and prefix commands simultaneously.

    ✨ Behold the golden platter. ✨😁
    """
    def __init__(self, data: MessageData | InteractionData, author: Member, invokable: GOLD_PLATTER_INVOKABLE_TYPES) -> None:
        # TODO: We got to somehow test this stuff with pytest because this being error prone is sort of a catastrophe.
        super().__init__(
            data = data, 
            invoker = author, 
            invokable = invokable
        )

        self.invokable: GOLD_PLATTER_INVOKABLE_TYPES

        self.guild: Guild = self.goldy.guild_manager.get_guild(self.get("guild_id"))

        self._interaction_responded = False
        """
        An internal property that is set by the :py:meth:`~GoldyBot.nextcore_utils.send_msg` method when a slash command is responded to.
        Basically don't mess around with it please.
        """

    @property
    def author(self) -> Member:
        """The author that invoked this invokable."""
        return self.invoker


    async def wait(self) -> None:
        """
        Use this to inform Discord and the member that this command will take longer than usual to respond or that a respond is being cooked up. 🍳🍲
        
        ------------------

        Returns
        -------
        ``None``
        """
        return await nextcore_utils.wait(self)

    async def send_message(
        self, 
        text: str = None, 
        embeds: List[Embed] = None, 
        recipes: List[Recipe] = None, 
        files: List[File] = None,
        reply: bool = False, 
        delete_after: float = None, 
        hide: bool = False,
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
        ``files``
            Files you may upload with this message.
        ``reply``
            Whether goldy bot should liberally reply to the message the command was invoked.
        ``delete_after``
            Deletes the message after this amount of seconds.
        ``hide``
            Hides the message in interaction commands and deletes the message after a few seconds on prefix commands.
        ``**extra``
            Allows you to pass the extra parameters that are missing.

        Returns
        -------
        ``GoldyBot.goldy.objects.message.Message``
            The message that was sent.
        
        """
        return await nextcore_utils.send_msg(self, text, embeds, recipes, files, reply, delete_after, hide, **extra)

from ... import nextcore_utils # This must be here to avoid circular import. (shit will blow up if this is moved, trust me)
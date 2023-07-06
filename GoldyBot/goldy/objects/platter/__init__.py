from __future__ import annotations

from abc import ABC
from devgoldyutils import DictClass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..member import Member
    from ..invokable import Invokable
    from ..message import Message
    from ...recipes import Recipe
    from ...nextcore_utils.embeds.embed import Embed

class Platter(ABC, DictClass):
    def __init__(self, data: dict, invoker: Member, invokable: Invokable) -> None:
        self.data = data
        """The raw data received right from discord that triggered this."""
        self.invoker = invoker
        """The member who triggered this platter."""
        self.invokable = invokable
        """The invokable object that was triggered. E.g. Command"""
        self.goldy = invokable.goldy
        """An instance of the goldy class."""
        self.logger = invokable.logger
        """A logger object you may use to log."""

        super().__init__(logger = invokable.logger)

        self._interaction_responded = False
        """An internal property that is set by the :py:meth:`~GoldyBot.nextcore_utils.send_msg` method when a slash command is responded to."""

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

from ... import nextcore_utils # This must be here to avoid circular import.
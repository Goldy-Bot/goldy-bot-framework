from __future__ import annotations

from typing import TYPE_CHECKING
from discord_typings import MessageData, InteractionData

from . import Platter

if TYPE_CHECKING:
    from ..member import Member
    from ...guilds import Guild
    from ...commands.command import Command

class GoldPlatter(Platter):
    """
    🟡 The gold platter is equivalent to the context/ctx/interaction name your used to. You can use the alias context/ctx if your not a fan of the FUNNY name. 
    It's actually returned on both interactions and normal message/prefix commands. You can use this object to grab the command author, reply to the command, send a message in the command's channel and a lot more.

    ⚡ With this class I'm able to handle both slash and prefix commands simultaneously.

    ✨ Behold the golden platter. ✨😁
    """
    def __init__(self, data: MessageData | InteractionData, author: Member, command: Command) -> None:
        # TODO: We got to somehow test this stuff with pytest because this being error prone is sort of a catastrophe.
        super().__init__(
            data = data, 
            invoker = author, 
            invokable = command
        )

        self.guild: Guild = self.goldy.guild_manager.get_guild(self.get("guild_id"))

    @property
    def author(self) -> Member:
        """The member who triggered this command."""
        return self.invoker

    @property
    def command(self) -> Command:
        """The command object that was invoked."""
        return self.invokable
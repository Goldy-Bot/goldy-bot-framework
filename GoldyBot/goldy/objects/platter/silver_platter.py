from __future__ import annotations

from typing import TYPE_CHECKING
from discord_typings import ComponentInteractionData

from . import Platter

if TYPE_CHECKING:
    from ..member import Member
    from ...guilds import Guild
    from ...recipes import Recipe

class SilverPlatter(Platter):
    def __init__(self, data: ComponentInteractionData, author: Member, recipe: Recipe) -> None:
        # TODO: We got to somehow test this stuff with pytest because this being error prone is sort of a catastrophe.
        super().__init__(
            data = data, 
            invoker = author, 
            invokable = recipe
        )

        self.guild: Guild = self.goldy.guild_manager.get_guild(self.get("guild_id"))

    @property
    def author(self) -> Member:
        """The member who triggered this command."""
        return self.invoker

    @property
    def recipe(self) -> Recipe:
        """The recipe that was invoked."""
        return self.invokable
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple

    from ..objects.platter import Platter
    from ..typings import RequirementFunctionT

__all__ = (
    "is_guild_owner",
)

def is_guild_owner() -> RequirementFunctionT:
    """
    Returns a built-in requirement to restrict commands to only guild owners.
    """

    async def requirement(self, platter: Platter, **kwargs) -> Tuple[bool, str]:
        guild = await platter.guild

        id_of_command_author = platter.data["member"]["user"]["id"]

        if guild.data["owner_id"] == id_of_command_author:
            return True, "command author is guild owner"

        return False, "you are not the guild owner"

    return requirement
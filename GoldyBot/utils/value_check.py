from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List
    from discord_typings import SelectMenuOptionData, ApplicationCommandOptionData

from .. import errors

__all__ = ("choices_value_check",)

def choices_value_check(choices: List[SelectMenuOptionData | ApplicationCommandOptionData]) -> None:
    allowed_type = type(choices[0]["value"])

    if not all([type(choice["value"]) == allowed_type for choice in choices]):
        raise errors.GoldyBotError(
            f"All choices got to have the same value type! The allowed type here was '{allowed_type}'."
        )
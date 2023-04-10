from __future__ import annotations

from enum import Enum
from discord_typings import ButtonComponentData

from .. import BowlRecipe

class ButtonStyle(Enum):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5

    BLURPLE = PRIMARY
    GREY = SECONDARY
    GREEN = SUCCESS
    RED = DANGER

# Some development notes, ignore it.
"""
label?	string	Text that appears on the button; max 80 characters
emoji?	partial emoji	name, id, and animated
custom_id?	string	Developer-defined identifier for the button; max 100 characters
url?	string	URL for link-style buttons
disabled?	boolean	Whether the button is disabled (defaults to false)
"""

class Button(BowlRecipe):
    """A class used to create a slash command button."""
    def __init__(self, style: ButtonStyle | int, **extra: ButtonComponentData) -> None:

        data: ButtonComponentData = {}

        if isinstance(style, ButtonStyle):
            style = style.value

        data["type"] = 2 # ID type for button.
        data["style"] = style

        data.update(extra)

        super().__init__(data)
from __future__ import annotations

import os
from enum import Enum
from typing import overload, Literal
from discord_typings import ButtonComponentData

from .. import BowlRecipe, RECIPE_CALLBACK

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

class Button(BowlRecipe):
    """A class used to create a slash command button."""
    @overload
    def __init__(
        self, 
        style: ButtonStyle | int, 
        label: str, 
        callback: RECIPE_CALLBACK, 
        emoji: str = None, 
        custom_id: str = None, 
        **extra: ButtonComponentData
    ) -> ButtonComponentData:
        ...

    @overload
    def __init__(
        self, 
        style: Literal[5], 
        label: str, 
        url: str, 
        emoji: str = None, 
        **extra: ButtonComponentData
    ) -> ButtonComponentData:
        ...

    def __init__(
        self, 
        style: ButtonStyle | int, 
        label: str, 
        custom_id: str = None, 
        url: str = None, 
        emoji: str = None, 
        callback: RECIPE_CALLBACK = None, 
        **extra: ButtonComponentData
    ) -> ButtonComponentData:
        """
        Creates a discord button to use in action rows. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/interactions/message-components#buttons
        """
        data: ButtonComponentData = {}

        if isinstance(style, ButtonStyle):
            style = style.value

        if custom_id is None:
            custom_id = os.urandom(16).hex()

        data["type"] = 2 # ID type for button.
        data["style"] = style
        data["label"] = label

        if emoji is not None:
            # I don't personally use emojis any other way so for now I'll implement it like this. 
            # We may have an Emoji creator class in the future to improve things.
            data["emoji"] = {
                "id": None,
                "name": f"{emoji}"
            }

        if style == ButtonStyle.LINK.value:
            data["url"] = url
        else:
            data["custom_id"] = custom_id

        data.update(extra)

        super().__init__(data, data["label"], callback)
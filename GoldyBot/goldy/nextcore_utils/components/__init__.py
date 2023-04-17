from __future__ import annotations

from typing import List, Callable, TYPE_CHECKING, Any, Type
from discord_typings import ActionRowData, ComponentData

from ... import objects

RECIPE_CALLBACK = Callable[[objects.GoldPlatter], Any]

# TODO: Add functionality to register recipes callback just like a command with a decorator. 
# (i think a bowl recipe should also be a command object too or at least should contain a command object.)

class BowlRecipe(dict):
    """A bowl recipe is equivalent to an item or message component. This is inherited by all messages components in Goldy Bot. This can be passed into a GoldenBowl() class."""
    def __init__(self, data: ComponentData, callback: RECIPE_CALLBACK = None) -> ComponentData:
        """
        Creates an component in discord to use in action rows. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/interactions/message-components#action-rows
        """
        if callback is not None:
            # TODO: Add to cache.
            #data["custom_id"]
            ...

        self.callback = callback
        """The function to be executed on recipe interaction."""
        
        super().__init__(data)

class GoldenBowl(dict):
    """A golden bowl is equivalent to a view/action row but it's a little more fancy."""
    def __init__(self, recipes: List[BowlRecipe], **extra: ActionRowData) -> ActionRowData:
        """
        Creates an action row in discord. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/interactions/message-components#action-rows
        """
        data = ActionRowData(
            type = 1,
            components = [recipe for recipe in recipes]
        )

        data.update(extra)
        
        super().__init__(data)
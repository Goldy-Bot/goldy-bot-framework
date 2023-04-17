from __future__ import annotations

from typing import List, Callable, Any, Tuple
from discord_typings import ActionRowData, ComponentData
from devgoldyutils import LoggerAdapter

from GoldyBot import goldy_bot_logger
from ... import objects

RECIPE_CALLBACK = Callable[[objects.GoldPlatter], Any]

registered_recipes: List[Tuple[str, object]] = []
"""
This list contains all the recipes that have been registered and it's memory location to the class.
"""

class BowlRecipe(dict):
    """A bowl recipe is equivalent to an item or message component. This is inherited by all messages components in Goldy Bot. This can be passed into a GoldenBowl() class."""
    def __init__(self, data: ComponentData, callback: RECIPE_CALLBACK = None) -> ComponentData:
        """
        Creates an component in discord to use in action rows. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/interactions/message-components#action-rows
        """
        self.callback = callback
        """The function to be executed on recipe interaction."""

        self.logger = LoggerAdapter(
            logger = LoggerAdapter(goldy_bot_logger, prefix=self.__class__.__name__),
            prefix = data.get('label', None)
        )

        super().__init__(data)

    async def invoke(self, platter: objects.GoldPlatter) -> None:
        """Runs/triggers this recipe. This method is usually used internally."""
        self.logger.debug(f"Attempting to invoke RECIPE...")

        try:
            await self.callback(
                platter
            )
        
        except TypeError as e:
            if "object NoneType can't be used in 'await' expression" in e.args[0]:
                self.logger.debug("The callback wasn't an async function so we called it without await.")
            else:
                raise e


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

        # Add recipes to cache.
        for recipe in recipes:
            if recipe.callback is not None:
                registered_recipes.append((recipe["custom_id"], recipe))

        data.update(extra)
        
        super().__init__(data)
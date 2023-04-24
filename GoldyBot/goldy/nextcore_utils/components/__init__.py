from __future__ import annotations

from typing import List, Callable, Any, Tuple
from discord_typings import ActionRowData, ComponentData
from devgoldyutils import LoggerAdapter, Colours

from GoldyBot import goldy_bot_logger
#from GoldyBot.goldy.utils import is_lambda
from ... import objects
from ...nextcore_utils import front_end_errors

RECIPE_CALLBACK = Callable[[objects.GoldPlatter], Any]

registered_recipes: List[Tuple[str, object]] = []
"""
This list contains all the recipes that have been registered and it's memory location to the class.
"""

class BowlRecipe(dict):
    """A bowl recipe is equivalent to an item or message component. This is inherited by all messages components in Goldy Bot. This can be passed into a GoldenBowl() class."""
    def __init__(self, data: ComponentData, name: str, author_only: bool = True, callback: RECIPE_CALLBACK = None, **callback_args: dict) -> ComponentData:
        """
        Creates an component in discord to use in action rows. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/interactions/message-components#action-rows
        """
        self.callback = callback
        """The function to be executed on recipe interaction."""

        self.author_only = author_only
        self.callback_args = callback_args

        self.logger = LoggerAdapter(
            logger = LoggerAdapter(goldy_bot_logger, prefix=self.__class__.__name__),
            prefix = Colours.PINK_GREY.apply(name)
        )

        super().__init__(data)

    async def invoke(self, platter: objects.GoldPlatter, cmd_platter: objects.GoldPlatter) -> None:
        """Runs/triggers this recipe. This method is usually used internally."""
        self.logger.debug("Attempting to invoke RECIPE...")

        if self.author_only:
            if not platter.author.id == cmd_platter.author.id:
                raise front_end_errors.OnlyAuthorCanInvokeRecipe(platter, self.logger)

        try:
            await self.callback(
                platter,
                **self.callback_args
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

        # This is assigned by the send_msg nextcore util.
        self.cmd_platter = None
        """The platter object of the command this bowl was initialized from."""

        # Add recipes to cache.
        for recipe in recipes:
            if recipe.callback is not None:
                registered_recipes.append((recipe["custom_id"], recipe, self))

        data.update(extra)
        
        super().__init__(data)
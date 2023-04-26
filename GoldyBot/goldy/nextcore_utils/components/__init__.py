from __future__ import annotations

from typing import List, Callable, Any, Tuple
from discord_typings import ComponentData
from devgoldyutils import LoggerAdapter, Colours

from GoldyBot import goldy_bot_logger
from ... import objects
from ...nextcore_utils import front_end_errors

RECIPE_CALLBACK = Callable[[objects.GoldPlatter], Any]

registered_recipes: List[Tuple[str, object]] = []
"""
This list contains all the recipes that have been registered and it's memory location to the class.
"""

class Recipe(dict):
    """A recipe is equivalent to an item or message component. This is inherited by all message components in Goldy Bot. This can be passed into a send_msg function."""
    def __init__(self, data: ComponentData, name: str, author_only: bool = True, callback: RECIPE_CALLBACK = None, **callback_args: dict) -> ComponentData:
        """
        Creates an component in discord to use in action rows. 😋
        """
        self.callback = callback
        """The function to be executed on recipe interaction."""

        self.author_only = author_only
        self.callback_args = callback_args

        self.logger = LoggerAdapter(
            logger = LoggerAdapter(goldy_bot_logger, prefix=self.__class__.__name__),
            prefix = Colours.PINK_GREY.apply(name)
        )

        # This is assigned by the send_msg nextcore util.
        self.cmd_platter = None
        """The platter object of the command this bowl was initialized from."""

        if self.callback is not None:
            registered_recipes.append((data["custom_id"], self))
            self.logger.debug("I've been registered and added cache.")
            
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
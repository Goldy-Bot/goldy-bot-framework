from __future__ import annotations

from typing import Callable, Any, TYPE_CHECKING, Awaitable
from discord_typings import ComponentData
from devgoldyutils import LoggerAdapter, Colours

from abc import abstractmethod
from ... import goldy_bot_logger
from ..objects.invokable import Invokable
from ..objects.platter.golden_platter import GoldPlatter
from ..nextcore_utils import front_end_errors

if TYPE_CHECKING:
    from ... import objects

__all__ = ("RECIPE_CALLBACK", "Recipe")

RECIPE_CALLBACK = Callable[[GoldPlatter], Any]

class Recipe(Invokable):
    """A recipe is equivalent to an item or message component. This is inherited by all message components in Goldy Bot. This can be passed into a send_msg function."""
    def __init__(self, data: ComponentData, name: str, callback: RECIPE_CALLBACK, author_only: bool = True) -> ComponentData:
        """
        Creates an component in discord to use in action rows. 😋
        """
        self.callback = callback
        """The function to be executed on recipe interaction."""
        self.author_only = author_only

        self.logger = LoggerAdapter(
            logger = LoggerAdapter(goldy_bot_logger, prefix = self.__class__.__name__),
            prefix = Colours.PINK_GREY.apply(name)
        )

        self.command_platter: objects.GoldPlatter | None = None
        """The platter object from the command that sent this recipe."""

        from ... import get_goldy_instance

        super().__init__(
            name = name,
            data = data,
            callable = callback,
            goldy = get_goldy_instance(),
            logger = self.logger 
        )

    @abstractmethod
    async def invoke(self, platter: objects.GoldPlatter, lambda_func: Callable[..., Awaitable]) -> Any:
        """Runs/triggers this recipe. This method is usually used internally."""
        self.logger.debug(f"Attempting to invoke '{self.__class__.__name__}'...")

        if self.author_only:
            if not platter.author.id == platter.invokable.command_platter.author.id:
                raise front_end_errors.OnlyAuthorCanInvokeRecipe(platter, self.logger)

        try:
            return await lambda_func()

        except TypeError as e:
            if "object NoneType can't be used in 'await' expression" in e.args[0]:
                self.logger.debug("The callback wasn't an async function so we called it without await.")
            else:
                raise e
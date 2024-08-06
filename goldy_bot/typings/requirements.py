from typing import Callable, Awaitable, Tuple, Union

from ..helpers import Embed
from ..objects import Platter

__all__ = (
    "RequirementFunctionT",
)

RequirementFunctionT = Callable[[object, Platter], Awaitable[Tuple[bool, Union[str, Embed]]]]
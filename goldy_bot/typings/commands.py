from typing import Callable, Awaitable, Any

from ..objects import Platter

__all__ = (
    "CommandFuncT",
)

CommandFuncT = Callable[[object, Platter], Awaitable[Any]]
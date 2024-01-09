from typing import Callable, Awaitable, Any

from ..platter import Platter

__all__ = (
    "CommandFuncT",
)

CommandFuncT = Callable[[object, Platter], Awaitable[Any]]
from typing import Callable, Awaitable, Any, Union

from ..objects import Platter
from ..commands.slash_options import SlashOption, SlashOptionAutoComplete

__all__ = (
    "CommandFuncT",
    "SlashOptionsT"
)

SlashOptionsT = Union[SlashOption, SlashOptionAutoComplete]
CommandFuncT = Callable[[object, Platter], Awaitable[Any]]
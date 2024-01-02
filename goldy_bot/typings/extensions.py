from typing import Callable, TypedDict

from ..goldy import Goldy
from ..extensions import Extension

__all__ = (
    "ExtensionLoadFuncT",
    "ExtensionMetadataData"
)

ExtensionLoadFuncT = Callable[[Goldy], Extension]

class ExtensionMetadataData(TypedDict):
    name: str
    dependencies: str
    version: str
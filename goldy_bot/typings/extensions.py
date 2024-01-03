from typing import Callable, TypedDict, Dict, Union

from ..goldy import Goldy
from ..extensions import Extension

__all__ = (
    "ExtensionLoadFuncT",
    "ExtensionMetadataData",
    "RepoData",
    "ExtensionRepoData"
)

ExtensionLoadFuncT = Callable[[Goldy], Extension]

class ExtensionMetadataData(TypedDict):
    name: str
    dependencies: str
    version: str

ExtensionRepoData = TypedDict("ExtensionRepoData", {"git_url": str})

class RepoData(TypedDict):
    version: int
    extensions: Dict[str, Union[ExtensionRepoData, str]]
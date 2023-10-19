from __future__ import annotations
from typing import  TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict, Tuple, Set

    T = TypeVar("T")

__all__ = ("cache_lookup",)

def cache_lookup(key: str, cache: Dict[str, Tuple[str, T]] | List[Tuple[str, T]] | Set[Tuple[str, T]], cap_sensitive = True) -> Tuple[str, T] | None:
    """Finds and returns object using key from any goldy bot cache object."""

    if cap_sensitive is False:
        key = key.lower()

    if isinstance(cache, (list, set)):
        for obj in cache:
            
            if isinstance(obj, tuple):
                if key == (lambda x: x.lower() if cap_sensitive is False else x)(obj[0]):
                    return obj

    elif isinstance(cache, dict):

        for obj in cache:
            if key == (lambda x: x.lower() if cap_sensitive is False else x)(obj):
                return cache[obj]

    return None

    # TODO: Add support for more different cache types.
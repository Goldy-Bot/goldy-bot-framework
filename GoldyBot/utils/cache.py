from __future__ import annotations

from typing import Any, Tuple, overload, List

@overload
def cache_lookup(key: str|int, cache: dict) -> Any | None:
    ...

@overload
def cache_lookup(key: str, cache: dict, cap_sensitive = True) -> Tuple[str, ...] | None:
    ...


@overload
def cache_lookup(key: str|int, cache: List[tuple]) -> Tuple[str, ...] | None:
    ...

@overload
def cache_lookup(key: str, cache: list, cap_sensitive = True) -> Tuple[str, ...] | None:
    ...


def cache_lookup(key: str|int, cache: dict|list|set, cap_sensitive = True) -> Tuple[str, ...] | Any | None:
    """Finds and returns object using key from any goldy bot cache object."""
    if cap_sensitive is False:
        key = key.lower()

    if isinstance(cache, (list, set)):
        for obj in cache:
            
            if isinstance(obj, tuple):
                if key == (lambda x: x.lower() if cap_sensitive is False else x)(obj[0]):
                    return obj


    if isinstance(cache, dict):

        for obj in cache:
            if key == (lambda x: x.lower() if cap_sensitive is False else x)(obj):
                return cache[obj]

    return None

    # TODO: Add support for more different cache types.
from __future__ import annotations

from typing import Any, Tuple

def cache_lookup(key:str|int, cache:dict|list) -> Tuple[str, ...] | Any | None:
    """Finds and returns object using key from any goldy bot cache object."""
    if isinstance(cache, list):
        for obj in cache:
            
            if isinstance(obj, tuple):
                if key == obj[0]:
                    return obj


    if isinstance(cache, dict):

        for obj in cache:
            if key == obj:
                return cache[obj]

    return None

    # TODO: Add support for more different cache types.
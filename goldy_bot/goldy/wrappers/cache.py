from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, TypeVar
    from typing_extensions import Self

    from io import TextIOWrapper

    from ..goldy import Goldy
    from ...typings import GoldySelfT

    T = TypeVar("T", Any)

import json
from pathlib import Path
from devgoldyutils import Colours, LoggerAdapter

from ...logger import goldy_bot_logger

__all__ = (
    "Cache",
)

logger = LoggerAdapter(
    goldy_bot_logger, prefix = Colours.BLUE.apply("Cache")
)

class Cache():
    """Goldy bot's caching system."""
    def __init__(self) -> None:
        self._cache_file = Path(".goldy_cache.owo")

        super().__init__()

    def get_cache(self, cache_name: str) -> Optional[Any]:
        logger.debug(f"Getting '{cache_name}' cache...")

        data: Dict[str, Any] = {}

        with self.__get_cache_file("r") as file:
            data = json.load(file)

        return data.get(cache_name)

    def set_cache(self, cache_name: str, value: T) -> T:
        logger.debug(f"Setting '{cache_name}' cache...")

        json_data: dict = {}

        with self.__get_cache_file("r") as file:
            json_data = json.load(file)

        with self.__get_cache_file("w") as file:
            json.dump({**json_data, **{cache_name: value}}, file)

        return value

    def clear_cache(self: Goldy) -> None:
        self.logger.info("Deleting cache file...")
        self._cache_file.unlink(True)

    def __get_cache_file(self: GoldySelfT[Self], mode: str) -> TextIOWrapper:

        if not self._cache_file.exists():
            self.logger.debug("Cache file didn't exist so I'm creating one...")

            with self._cache_file.open("w") as file:
                file.write("{}")

        return self._cache_file.open(mode, encoding = "utf+8")
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from typing_extensions import Self

    from ...typings import GoldySelfT

__all__ = (
    "Stats",
)

class Stats():
    def __init__(self) -> None:
        super().__init__()

    @property
    def latency(self: GoldySelfT[Self]) -> Optional[float]:
        """Returns the latency in milliseconds between discord and goldy bot. ``Goldy -> Discord -> Goldy``"""
        try:
            return self.shard_manager.active_shards[0].latency
        except RuntimeError:
            return None
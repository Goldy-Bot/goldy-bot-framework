from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from typing_extensions import Self

    from ...typings import GoldySelfT

import os
import psutil

__all__ = (
    "Stats",
)

class Stats():
    def __init__(self) -> None:
        self.__process = psutil.Process(os.getpid())

        super().__init__()

    @property
    def latency(self: GoldySelfT[Self]) -> Optional[float]:
        """Returns the latency in milliseconds between discord and goldy bot. ``Goldy -> Discord -> Goldy``"""
        try:
            return self.shard_manager.active_shards[0].latency
        except RuntimeError:
            return None

    @property
    def cpu_usage(self) -> int:
        """Returns the percentage of CPU the framework is using on your system."""
        return self.__process.cpu_percent(0) / psutil.cpu_count()

    @property
    def ram_usage(self) -> int:
        """Returns amount of RAM the framework is using on your system in megabytes."""
        return self.__convert_to_MB(self.__process.memory_info().rss)

    @property
    def disk_usage(self) -> int:
        """Returns disk usage of the framework in megabytes."""
        disk_process = self.__process.io_counters() 
        disk_usage_process = disk_process[2] + disk_process[3]

        disk_system = psutil.disk_io_counters()
        disk_system_total = disk_system[2] + disk_system[3]

        return self.__convert_to_MB(disk_usage_process / disk_system_total * 100)

    def __convert_to_MB(self, size):
        return (f"{size/float(1<<20):,.2f}")
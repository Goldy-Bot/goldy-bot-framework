from __future__ import annotations

import os
import psutil
import platform

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Goldy

class System():
    """Goldy Bot class used to check how much resources Goldy is utilizing on the host system."""
    def __init__(self, goldy: Goldy):
        self.goldy = goldy
        self.process = psutil.Process(os.getpid())

    @property
    def os(self) -> str:
        """Returns the operating system the bot is running on."""
        return f"{platform.system()} {platform.release()}"

    @property
    def cpu(self) -> int:
        """Returns the percentage of CPU Goldy Bot is using on your system."""
        return self.process.cpu_percent(0)/psutil.cpu_count()

    @property
    def ram(self) -> int:
        """Returns amount of ram Goldy Bot is using on your system in megabytes."""
        return self.__convert_to_MB(self.process.memory_info().rss)

    @property
    def disk(self):
        disk_process = self.process.io_counters() 
        disk_usage_process = disk_process[2] + disk_process[3]

        disk_system = psutil.disk_io_counters()
        disk_system_total = disk_system[2] + disk_system[3]

        return self.__convert_to_MB(disk_usage_process/disk_system_total * 100)
    
    @property
    def python_version(self) -> str:
        """Returns the python version goldy bot is running in."""
        return platform.python_version()

    @property
    def in_docker(self) -> bool:
        """Returns True/False whether goldy bot is running in a docker container."""
        if "DOCKER" in os.environ:
            return True
        
        return False

    def __convert_to_GB(self, size):
        return(f"{size/float(1<<30):,.2f}")

    def __convert_to_MB(self, size):
        return (f"{size/float(1<<20):,.2f}")
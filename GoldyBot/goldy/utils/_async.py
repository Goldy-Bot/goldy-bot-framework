from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ... import Goldy

def delay(coro, seconds:float, goldy: Goldy):
    """Delays a asynchronous function."""
    goldy.async_loop.create_task(__delay_async(coro, seconds))

async def __delay_async(coro, seconds:float):
    await asyncio.sleep(seconds)
    await coro
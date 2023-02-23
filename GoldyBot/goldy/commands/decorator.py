from __future__ import annotations
import asyncio
from typing import Dict, List

from . import Command

def command(
    cmd_name:str = None, 
    description:str = None, 
    required_roles:List[str]=None, 
    slash_cmd_only=False, 
    normal_cmd_only=False
    ):
    """
    Add a command to Goldy Bot with this decorator.
    
    ---------------
    ### ***``Example:``***

    This is how you create a command in GoldyBot. 😀

    ```python
    @GoldyBot.command()
    async def uwu(ctx):
        await send(ctx, f'Hi, {ctx.author.mention}! UwU!')
    ```
    """
    def decorate(func):
        def inner() -> Command:
            func:function = func
            
            # TODO: Use code from goldy bot v4.
            

        return inner()

    return decorate
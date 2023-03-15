from __future__ import annotations
from ... import get_goldy_instance
from typing import List

from . import Command
from ...errors import GoldyBotError



def command(
    name:str = None, 
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
        def inner(func) -> Command:
            goldy = get_goldy_instance()

            if goldy is None:
                raise GoldyBotError("Please initialize goldy class before registering commands.")

            create_slash = True; create_normal = True

            if slash_cmd_only: create_normal = False
            if normal_cmd_only: create_slash = False

            return Command(
                goldy, 
                func, 
                name, 
                description, 
                required_roles, 
                allow_prefix_cmd=create_normal, 
                allow_slash_cmd=create_slash
            )
        
        return inner(func)

    return decorate
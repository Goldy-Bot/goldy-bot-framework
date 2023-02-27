from __future__ import annotations
from ... import get_goldy_instance
from typing import List

from . import Command

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
            command = Command(goldy, func, name, description, required_roles)
            extension = command.extension

            create_slash = True; create_normal = True

            if slash_cmd_only: create_normal = False
            if normal_cmd_only: create_slash = False

            if create_slash:
                goldy.async_loop.create_task(
                    command.create_slash()
                )

            if create_normal:
                goldy.async_loop.create_task(
                    command.create_normal()
                )

            extension.add_command(command)

            return command
            
            # TODO: Use code from goldy bot v4.
            

        return inner(func)

    return decorate
from __future__ import annotations

from typing import List, Dict
from discord_typings import ApplicationCommandOptionData

from . import Command
from ... import errors
from ... import get_goldy_instance


def command(
    name: str = None, 
    description: str = None, 
    required_roles: List[str]=None, 
    slash_options: Dict[str,  ApplicationCommandOptionData] = None,
    slash_cmd_only:bool = False, 
    normal_cmd_only:bool = False
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
                raise errors.GoldyBotError("Please initialize goldy class before registering commands.")

            create_slash = True; create_normal = True

            if slash_cmd_only: create_normal = False
            if normal_cmd_only: create_slash = False

            return Command(
                goldy = goldy, 
                func = func, 
                name = name, 
                description = description, 
                required_roles = required_roles, 
                slash_options = slash_options,
                allow_prefix_cmd = create_normal, 
                allow_slash_cmd = create_slash
            )
        
        return inner(func)

    return decorate
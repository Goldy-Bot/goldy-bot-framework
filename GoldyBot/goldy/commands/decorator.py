from __future__ import annotations

from typing import List, Dict, TYPE_CHECKING

from . import Command
from ... import get_goldy_instance

if TYPE_CHECKING:
    from GoldyBot import SlashOption


def command(
    name: str = None, 
    description: str = None, 
    required_roles: List[str]=None, 
    slash_options: Dict[str, SlashOption] = None,
    slash_cmd_only:bool = False, 
    normal_cmd_only:bool = False
):
    """
    Add a command to Goldy Bot with this decorator.
    
    ---------------
    
    ⭐ Example:
    -------------
    This is how you create a command in GoldyBot::

        @GoldyBot.command()
        async def hello(self, platter: GoldyBot.GoldPlatter):
            await platter.send_message("👋hello", reply=True)

    .. warning::

        Do note that standalone commands are no longer a thing in goldy bot v5 so you WILL need to register this command inside an Extension. Visit `here`_ to find out how to create extensions.

    .. _here: https://goldybot.devgoldy.me/goldy.extensions.html#how-to-create-an-extension
    
    """
    def decorate(func):
        def inner(func) -> Command:
            goldy = get_goldy_instance()

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
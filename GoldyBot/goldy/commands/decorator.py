from __future__ import annotations

from typing import List, Dict, TYPE_CHECKING, overload, Callable, Literal

from .group_command import GroupCommand
from .slash_command import SlashCommand
from .prefix_command import PrefixCommand
from ... import get_goldy_instance

if TYPE_CHECKING:
    from GoldyBot import SlashOption

@overload
def command(
    name: str = None, 
    description: str = None, 
    required_roles: List[str] = None, 
    slash_options: Dict[str, SlashOption] = None,
    slash_cmd_only: bool = False, 
    hidden: bool = False,
    group: Literal[False] = False
) -> Callable[..., None]:
    ...

@overload
def command(
    name: str = None, 
    description: str = None, 
    required_roles: List[str] = None, 
    slash_cmd_only: bool = False, 
    hidden: bool = False,
    group: Literal[True] = False
) -> Callable[..., GroupCommand]:
    ...

def command(
    name: str = None, 
    description: str = None, 
    required_roles: List[str] = None, 
    slash_options: Dict[str, SlashOption] = None,
    slash_cmd_only: bool = False, 
    hidden: bool = False,
    group: bool = False
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

    .. _here: https://goldybot.devgoldy.xyz/goldy.extensions.html#how-to-create-an-extension
    
    """
    def decorate(func):
        def inner(func):
            goldy = get_goldy_instance()

            commands = (
                SlashCommand(
                    goldy = goldy, 
                    func = func, 
                    name = name, 
                    description = description, 
                    required_roles = required_roles, 
                    slash_options = slash_options,
                    hidden = hidden
                ),
                PrefixCommand(
                    goldy = goldy,
                    func = func,
                    name = name,
                    description = description,
                    required_roles = required_roles,
                    hidden = hidden
                ) if slash_cmd_only is False else None
            )

            return GroupCommand(base_commands = commands) if group else None

        return inner(func)

    return decorate
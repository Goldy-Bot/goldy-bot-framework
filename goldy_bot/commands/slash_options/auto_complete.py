from __future__ import annotations
from typing import List, TYPE_CHECKING, overload

if TYPE_CHECKING:
    from typing import Optional, Callable, Dict
    from discord_typings import AutocompleteInteractionData

    from ...goldy import Goldy

    AutoCompleteCallbackT = Callable[[object, str, Dict[str, str]], List[SlashOptionChoice]]

from devgoldyutils import LoggerAdapter, Colours

from nextcore.http import Route

from ...logger import goldy_bot_logger
from .slash_option import SlashOption, SlashOptionTypes, SlashOptionChoice

__all__ = (
    "SlashOptionAutoComplete",
)

logger = LoggerAdapter(
    goldy_bot_logger, prefix = Colours.BLUE.apply("SlashOptionAutoComplete")
)

class SlashOptionAutoComplete(SlashOption):
    r"""
    Like :py:meth:`~GoldyBot.SlashOption` but it auto completes while the member is typing and it doesn't force them to pick those options.
    You can also override the callback and implement your own auto complete mechanism like I did in mal_cord (https://github.com/THEGOLDENPRO/mal_cord/blob/main/__init__.py#L23).

    ---------------

    ⭐ Example:
    -------------
    This is how you use auto complete slash options::

        @GoldyBot.command(
            slash_options = {
                "bear_name": SlashOptionAutoComplete( # Now when you type these choices will be recommended to you but not forced on you.
                    description = "⭐ Pick a custom bear name.",
                    recommendations = [
                        "Simba",
                        "Paddington",
                        "Goldilocks",
                        "Toto"
                    ]
                )
            }
        )
        async def custom_bear(self, platter: GoldyBot.GoldPlatter, bear_name: str):
            if bear_name.lower() == "goldilocks":
                return await platter.send_message("*Goldilocks is not a bear you fool!*", reply=True)

            text = \
                "*> In the woods, there lived three bears in their cozy house. " \
                "There was a small wee bear, a middle-sized bear, " \
                f"and a great, huge bear known as* **{bear_name}**..." \

            await platter.send_message(text, reply=True)

    .. note::

        More at https://goldybot.devgoldy.xyz/examples.slash_options.html

    """
    @overload
    def __init__(
        self, 
        callback: AutoCompleteCallbackT, 
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        required: bool = True, 
        **kwargs
    ) -> None:
        ...

    @overload
    def __init__(
        self, 
        recommendations: List[SlashOptionChoice | str], 
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        required: bool = True, 
        **kwargs
    ) -> None:
        ...

    def __init__(
        self, 
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        callback: Optional[AutoCompleteCallbackT] = None, 
        recommendations: Optional[List[SlashOptionChoice | str]] = None, 
        required: bool = True, 
        **kwargs
    ) -> None:

        if callback is None and recommendations is None:
            raise ValueError("wait what, you didn't assign a value to callback or recommendations.")

        if recommendations is not None:
            recommendations = [SlashOptionChoice(x, x) if isinstance(x, str) else x for x in recommendations]

        self.callback = callback
        self.recommendations: Optional[List[SlashOptionChoice]] = recommendations

        super().__init__(
            name = name, 
            description = description, 
            required = required, 
            type = SlashOptionTypes.STRING,
            autocomplete = True,
            **kwargs
        )

    async def send_auto_complete(
        self, 
        data: AutocompleteInteractionData, 
        typing_value: str, 
        params: Dict[str, str], 
        command_class: object,
        goldy: Goldy
    ) -> None:

        payload = {}
        payload["choices"] = []

        choices: List[SlashOptionChoice] = []

        author_name = data['member']['user']['username']

        logger.debug(f"We got --> '{typing_value}' from '{author_name}'.")

        if self.callback is not None:
            choices = await self.callback(command_class, typing_value, **params)
        else:
            # Some shit fuzzy searching. I'll improve it later :L
            choices = [choice for choice in self.recommendations if typing_value.lower() in choice.data["name"].lower()]

        payload["choices"] = SlashOptionChoice.strip(choices)[:24] # Discord only allows max of 25 choices.

        logger.debug(
            f"Sending auto complete '{payload['choices']}' to --> command invoked by '{author_name}'..."
        )

        await goldy.client.request(
            Route(
                "POST", 
                "/interactions/{interaction_id}/{interaction_token}/callback", 
                interaction_id = data["id"], 
                interaction_token = data["token"]
            ),
            rate_limit_key = goldy.key_and_headers["rate_limit_key"],
            json = {
                "type": 8, 
                "data": payload
            }
        )

        return None
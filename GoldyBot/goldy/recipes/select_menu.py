from __future__ import annotations
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from ... import GoldPlatter
    from typing import Callable, Any, List, Literal, Union
    from discord_typings import SelectMenuComponentData, SelectMenuOptionData, ComponentInteractionData

    SELECT_MENU_SINGLE_VALUE_CALLBACK = Callable[[GoldPlatter, str], Any]
    SELECT_MENU_MULTIPLE_VALUES_CALLBACK = Callable[[GoldPlatter, List[str]], Any]

    SELECT_MENU_CALLBACKS = Union[SELECT_MENU_SINGLE_VALUE_CALLBACK, SELECT_MENU_MULTIPLE_VALUES_CALLBACK]

import os
from . import Recipe
from ... import utils
from enum import Enum

__all__ = ("SelectMenuTypes", "SelectMenuChoice", "SelectMenu")

class SelectMenuTypes(Enum):
    """An enum class containing all the select menu types."""
    STRING = 3
    USER = 5
    ROLE = 6
    MENTIONABLE = 7
    CHANNEL = 8

class SelectMenuChoice(dict):
    """A class used to create select menu choices."""
    def __init__(
        self, 
        label: str, 
        value: str | int, 
        description: str = None,
        emoji: str = None,
        default: bool = None,
        **extra
    ):
        """
        Creates a select menu choice.
        """
        data: SelectMenuOptionData = {}

        data["label"] = label
        data["value"] = value

        if description is not None:
            data["description"] = description

        if emoji is not None:
            data["emoji"] = {"id": None, "name": emoji}

        if default is not None:
            data["default"] = default

        data.update(extra)

        super().__init__(data)

class SelectMenu(Recipe):
    @overload
    def __init__(
        self, 
        callback: SELECT_MENU_SINGLE_VALUE_CALLBACK, 
        type: Literal[SelectMenuTypes.STRING] = SelectMenuTypes.STRING,
        choices: List[SelectMenuChoice | str] = None, 
        placeholder_text: str = None,
        min_values: Literal[1] = 1,
        max_values: Literal[1] = 1,
        author_only: bool = True, 
        **callback_args
    ):
        ...

    @overload
    def __init__(
        self, 
        callback: SELECT_MENU_SINGLE_VALUE_CALLBACK, 
        type: Literal[SelectMenuTypes.USER, SelectMenuTypes.ROLE, SelectMenuTypes.MENTIONABLE, SelectMenuTypes.CHANNEL] = SelectMenuTypes.STRING,
        placeholder_text: str = None,
        min_values: Literal[1] = 1,
        max_values: Literal[1] = 1,
        author_only: bool = True, 
        **callback_args
    ):
        ...

    @overload
    def __init__(
        self, 
        callback: SELECT_MENU_MULTIPLE_VALUES_CALLBACK, 
        type: Literal[SelectMenuTypes.STRING] = SelectMenuTypes.STRING,
        choices: List[SelectMenuChoice | str] = None, 
        placeholder_text: str = None,
        min_values: int = 1,
        max_values: int = 1,
        author_only: bool = True, 
        **callback_args
    ):
        ...

    @overload
    def __init__(
        self, 
        callback: SELECT_MENU_MULTIPLE_VALUES_CALLBACK, 
        type: Literal[SelectMenuTypes.USER, SelectMenuTypes.ROLE, SelectMenuTypes.MENTIONABLE, SelectMenuTypes.CHANNEL] = SelectMenuTypes.STRING,
        placeholder_text: str = None,
        min_values: int = 1,
        max_values: int = 1,
        author_only: bool = True, 
        **callback_args
    ):
        ...

    def __init__(
        self, 
        callback: SELECT_MENU_CALLBACKS, 
        type: SelectMenuTypes = SelectMenuTypes.STRING,
        choices: List[SelectMenuChoice | str] = None, 
        placeholder_text: str = None,
        min_values: int = 1,
        max_values: int = 1,
        custom_id: str = None, 
        author_only: bool = True, 
        **callback_args
    ):
        if TYPE_CHECKING:
            self.callback: SELECT_MENU_CALLBACKS

        data: SelectMenuComponentData = {}

        if custom_id is None:
            custom_id = os.urandom(16).hex()

        if type is not None:
            data["type"] = type.value if isinstance(type, SelectMenuTypes) else type
        else:
            data["type"] = SelectMenuTypes.STRING.value

        if choices is not None:
            if isinstance(choices[0], str):
                choices = [SelectMenuChoice(x, x) for x in choices]

            utils.choices_value_check(choices)

            data["options"] = choices[:24]

        if placeholder_text is not None:
            data["placeholder"] = placeholder_text

        if min_values is not None:
            data["min_values"] = min_values

        if max_values is not None:
            data["max_values"] = max_values

        data["custom_id"] = custom_id

        super().__init__(
            data, 
            self.__class__.__name__, 
            callback,
            author_only
        )

        self.register(custom_id)

    async def invoke(self, platter: GoldPlatter) -> Any:
        data: ComponentInteractionData = platter.data
        values = data["data"]["values"][0]

        if dict(self)["max_values"] > 1:
            values = data["data"]["values"]

        return await super().invoke(
            platter, lambda: self.callback(platter, values)
        )
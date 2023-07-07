from __future__ import annotations

from typing import overload, Literal

import dateparser
from datetime import datetime
from enum import Enum

class HumanDatetimeOptions(Enum):
    TIME = 0
    DATE = 1
    BOTH = 2

    def __init__(self, option: int) -> None:
        ...

@overload
def get_datetime(
    human_time: str, 
    option: Literal[HumanDatetimeOptions.TIME, 0], 
    time_formats = ["%H:%M"]
) -> datetime | None:
    ...

@overload
def get_datetime(
    human_date: str, 
    option: Literal[HumanDatetimeOptions.DATE, 1], 
    date_formats = ["%d/%m/%Y", "%Y/%m/%d"]
) -> datetime | None:
    ...

@overload
def get_datetime(
    human_datetime: str, 
    option: Literal[HumanDatetimeOptions.BOTH, 2], 
    datetime_formats = ["%d/%m/%Y %H:%M", "%Y/%m/%d %H:%M", "%d.%m.%Y %H:%M", "%Y.%m.%d %H:%M"]
) -> datetime | None:
    ...

def get_datetime(
    human_datetime: str, 
    option: HumanDatetimeOptions | int, 
    time_formats = ["%H:%M"], 
    date_formats = ["%d/%m/%Y", "%Y/%m/%d"],
    datetime_formats = ["%d/%m/%Y %H:%M", "%Y/%m/%d %H:%M", "%d.%m.%Y %H:%M", "%Y.%m.%d %H:%M"]
) -> datetime | None:
    """
    A Goldy Bot utils function that can read human time and date and convert them to a datetime object.

    Returns None if the human datetime string can't be recognized.
    """
    if isinstance(option, int):
        option = HumanDatetimeOptions(option)

    if option == HumanDatetimeOptions.TIME:
        return dateparser.parse(human_datetime, date_formats = time_formats)

    elif option == HumanDatetimeOptions.DATE:
        return dateparser.parse(human_datetime, date_formats = date_formats)
    
    elif option == HumanDatetimeOptions.BOTH:
        return dateparser.parse(human_datetime, date_formats = datetime_formats)
from __future__ import annotations

import GoldyBot
from GoldyBot import ( 
    get_datetime,
    DatabaseEnums,
    front_end_errors,
    HumanDatetimeOptions 
)

import pytz
import datetime as dt

class Timestamps(GoldyBot.Extension):
    """⏱️ Timestamps extension ported over from Goldy Bot V4 to V5. ⚡"""
    def __init__(self):
        super().__init__()

        self.default_timezone = "Europe/London"
        self.default_datetime_formats = ["%d/%m/%Y %H:%M", "%Y/%m/%d %H:%M", "%d.%m.%Y %H:%M", "%Y.%m.%d %H:%M"]

        self.failed_read_embed = GoldyBot.Embed(
            title = "❓ Did you enter it correctly?",
            description = "I couldn't read either your time or date properly, please could you try again. Perhaps you mistyped something.",
            colour = GoldyBot.Colours.RED
        )

        self.unknown_timezone_embed = GoldyBot.Embed(
            title = "⏱️ Unknown Time Zone!", 
            description = """
            *This is how the ``timezone`` parameter should be used.*

            ``Europe/London`` = **UK Time**
            ``America/New_York`` = **New York Time**
            ``Europe/Stockholm`` = **Sweden Time**

            *The list goes on... To see the full list click [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).*
            """, 
            colour = GoldyBot.Colours.RED
        )

    timestamp = GoldyBot.GroupCommand("timestamp")

    @timestamp.sub_command(description = "Sends a discord timestamp of that time and date.", slash_options = {
        "date": GoldyBot.SlashOptionAutoComplete(
            description = "The date goes here like example, 13.08.2022 or even 2022/08/22.", 
            recommendations = [
                "today"
            ],
            required = True,
        ),
        "time": GoldyBot.SlashOptionAutoComplete(
            description = "The time goes here like example, 15:00.", 
            recommendations = [
                "now"
            ],
            required = True
        ),
        "flag": GoldyBot.SlashOption(
            description = "Choose a flag.", 
            required = True, 
            choices = [
                GoldyBot.SlashOptionChoice("08/13/2022", "d"),
                GoldyBot.SlashOptionChoice("August 13, 2022", "D"),
                GoldyBot.SlashOptionChoice("6:00 PM", "t"),
                GoldyBot.SlashOptionChoice("6:00:00 PM", "T"),
                GoldyBot.SlashOptionChoice("August 13, 2022 6:00 PM", "f"),
                GoldyBot.SlashOptionChoice("Saturday, August 13, 2022 6:00 PM", "F"),
                GoldyBot.SlashOptionChoice("in 3 hours", "R")
            ]
        ),
        "timezone": GoldyBot.SlashOption(
            description = "The timezone to use. Goldy Bot defaults to Europe/London timezone.", required = False),
        "date_format": GoldyBot.SlashOption(
            description = "The format we should read your date in. The order more specifically.", 
            choices = [
                GoldyBot.SlashOptionChoice("D/M/Y", 0),
                GoldyBot.SlashOptionChoice("Y/M/D", 1)
            ],
            required = False
        )
    })
    async def create(self, platter: GoldyBot.GoldPlatter, date, time, flag, timezone: str = None, date_format: str = None):
        member_data = await platter.author.database

        if date_format is None:
            datetime_formats = (lambda x: x if x is not None else self.default_datetime_formats)(member_data.get("datetime_formats", optional=True))
        else:
            datetime_formats = ["%d/%m/%Y %H:%M", "%d.%m.%Y %H:%M"] if date_format == 0 else ["%Y/%m/%d %H:%M", "%Y.%m.%d %H:%M"]

        if date == "today":
            date = dt.datetime.now().strftime(datetime_formats[0][:8])

        if time == "now":
            time = dt.datetime.now().strftime(datetime_formats[0][9:])

        datetime = get_datetime(f"{date} {time}", option = HumanDatetimeOptions.BOTH, datetime_formats = datetime_formats)

        if timezone is None:
            timezone = (lambda x: x if x is not None else self.default_timezone)(member_data.get("timezone", optional=True))

        if datetime is None:
            raise front_end_errors.FrontEndErrors(
                embed = self.failed_read_embed,
                message = "Datetime failed to read the member's input.",
                platter = platter,
                delete_after = 30
            )

        try:
            # Convert to chosen timezone.
            chosen_timezone = pytz.timezone(timezone)
            datetime = chosen_timezone.normalize(chosen_timezone.localize(datetime, is_dst=True))

            posix_timestamp = int(datetime.timestamp())

            copy_button = GoldyBot.Button(
                style = GoldyBot.ButtonStyle.GREY,
                label = "📋 Copy",
                callback = lambda x: x.send_message(f"``<t:{posix_timestamp}:{flag}>``", flags = 1 << 6),
                author_only = False
            )

            await platter.send_message(f"<t:{posix_timestamp}:{flag}>", recipes = [copy_button])

            return True

        except pytz.UnknownTimeZoneError as e:
            raise front_end_errors.FrontEndErrors(
                embed = self.unknown_timezone_embed,
                message = f"The time zone the member entered is incorrect. Error --> {e}",
                platter = platter,
                delete_after = 30,
                logger = self.logger
            )

        except Exception as e:
            raise front_end_errors.FrontEndErrors(
                embed = self.failed_read_embed,
                message = f"We got an unknown exception when we tried to process and send the timestamp. Error --> {e}",
                platter = platter,
                delete_after = 30,
                logger = self.logger
            )


    @timestamp.sub_command(description = "Allows you to sets default timezone and date format for /timestamp command.", slash_options = {
        "timezone" : GoldyBot.SlashOption(
            description = "The time zone. Must be like this --> Europe/London, America/New_York, Europe/Stockholm", 
            required = True
        ),
        "date_format": GoldyBot.SlashOption(
            description = "The format we should read your date in. The order more specifically.", 
            choices = [
                GoldyBot.SlashOptionChoice("D/M/Y", 0),
                GoldyBot.SlashOptionChoice("Y/M/D", 1)
            ],
            required = False
        )
    })
    async def set_defaults(self, platter: GoldyBot.GoldPlatter, timezone: str, date_format: int = None):
        datetime_formats = None

        if date_format is not None:
            datetime_formats = ["%d/%m/%Y %H:%M", "%d.%m.%Y %H:%M"] if date_format == 0 else ["%Y/%m/%d %H:%M", "%Y.%m.%d %H:%M"]

        timezone = timezone.lower()
        member_data = await platter.author.database

        try:
            pytz.timezone(timezone) # Test timezone.
            await member_data.push(DatabaseEnums.MEMBER_GLOBAL_DATA, {"timezone": timezone, "datetime_formats": datetime_formats})

            embed = GoldyBot.Embed(
                title = "⏱️ Timestamp Defaults Set!",
                description = f"""
                - Timezone: ``{timezone}``
                - Date Format: ``{None if date_format is None else 'D/M/Y' if date_format == 0 else 'Y/M/D'}``
                """,
                color = GoldyBot.Colours.GREEN
            )

            await platter.send_message(embeds = [embed])

        except pytz.UnknownTimeZoneError as e:
            raise front_end_errors.FrontEndErrors(
                embed = self.unknown_timezone_embed,
                message = f"Member supposedly entered false time zone. Error >> {e}",
                platter = platter,
                delete_after = 30
            )


def load():
    Timestamps()
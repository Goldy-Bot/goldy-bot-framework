from __future__ import annotations

import GoldyBot
from GoldyBot.goldy.utils.human_datetime import get_datetime, HumanDatetimeOptions
from GoldyBot.goldy.nextcore_utils import front_end_errors

import pytz
from datetime import datetime

class Timestamps(GoldyBot.Extension):
    """⏱️ Timestamps extension ported over from Goldy Bot V4 to V5. ⚡"""
    def __init__(self):
        super().__init__()

        self.default_timezone = "Europe/London"

        self.failed_read_embed = GoldyBot.Embed(
            title = "❓ Did you enter it correctly?",
            description = "I couldn't read either your time or date properly, please could you try again. Perhaps you mistyped something.",
            colour = GoldyBot.Colours.RED
        )

        self.unknown_timezone_embed = GoldyBot.Embed(
            title = "❤ Unknown Time Zone!", 
            description = """
            *This is how the ``timezone`` parameter should be used.*

            ``Europe/London`` = **UK Time**
            ``America/New_York`` = **New York Time**
            ``Europe/Stockholm`` = **Sweden Time**

            *The list goes on... To see the full list click [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).*
            """, 
            colour = GoldyBot.Colours.RED
        )

        self.unknown_error_embed = GoldyBot.Embed(
            title = "❓ Did you enter it correctly?",
            description = "I couldn't read either your time or date properly, please could you try again. Perhaps you mistyped something.",
            colour = GoldyBot.Colours.RED
        )


    @GoldyBot.command(description = "Sends a discord timestamp of that time and date.", slash_options = {
        "date": GoldyBot.SlashOption(description="The date goes here like example, 13.08.2022 or even 2022/08/22.", required=True),
        "time": GoldyBot.SlashOption(description="The time goes here like example, 15:00.", required=True),
        "flag": GoldyBot.SlashOption(description="Choose a flag.", required=True, 
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
        "timezone": GoldyBot.SlashOption(description="The timezone to use. Goldy Bot defaults to Europe/London timezone.", required=False),
        "date_format": GoldyBot.SlashOption(description="The format we should read your date in. The order more specifically.", 
            choices = [
                GoldyBot.SlashOptionChoice("D/M/Y", 0),
                GoldyBot.SlashOptionChoice("Y/M/D", 1)
            ],
            required = False
        )
    })
    async def timestamp(self, platter: GoldyBot.GoldPlatter, date, time, flag, timezone: str = None, date_format: str = 0):
        if date_format == 1:
            dt_formats = ["%Y/%m/%d %H:%M", "%Y.%m.%d %H:%M"]
        else:
            dt_formats = ["%d/%m/%Y %H:%M", "%d.%m.%Y %H:%M"]

        # TODO: ^ Add this setting to the database.

        datetime: datetime = get_datetime(f"{date} {time}", option = HumanDatetimeOptions.BOTH, datetime_formats=dt_formats)

        # TODO: Phrase the timezone.

        if timezone is None:
            member_data = await platter.author.database
            timezone = (lambda x: x if x is not None else self.default_timezone)(member_data.get("timezone"))

        if datetime is None:
            await platter.send_message(embeds=[self.failed_read_embed], delete_after=30)
            return False

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
                delete_after = 30,
                logger = self.logger
            )

        except Exception as e:
            raise front_end_errors.FrontEndErrors(
                embed = self.unknown_error_embed,
                message = f"We got an unknown exception when we tried to process and send the timestamp. Error --> {e}",
                delete_after = 30,
                logger = self.logger
            )


    """
    @GoldyBot.command(help_des="Sets default timezone for /timestamp command.", slash_cmd_only=True, slash_options={
        "timezone" : GoldyBot.nextcord.SlashOption(description="The time zone. Must be like this --> Europe/London, America/New_York, Europe/Stockholm", required=True)
    })
    async def timezone_set(self:Timestamps, ctx, timezone):
        member = GoldyBot.Member(ctx)
        member_data = await member.get_member_data()

        try:
            pytz.timezone(timezone)
            member_data[member.member_id]["timezone"] = timezone
            await member.edit_member_data(member_data)

            message = await send(ctx, embed=GoldyBot.Embed(
                title="💚 Time Zone Set!",
                description="Your default timezone was set **UwU**!",
                color=GoldyBot.Colours().GREEN
            ))

            await message.delete(delay=15)

        except pytz.UnknownTimeZoneError as e:
            GoldyBot.log("error", e)

            message = await send(ctx, embed=self.unknown_timezone_embed)

            await message.delete(delay=30)
    """


def load():
    Timestamps()
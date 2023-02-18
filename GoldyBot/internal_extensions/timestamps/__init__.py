from __future__ import annotations

import GoldyBot
from GoldyBot.utility.commands import *
import pytz

AUTHOR = 'Dev Goldy'
AUTHOR_GITHUB = 'https://github.com/THEGOLDENPRO'
OPEN_SOURCE_LINK = ''

class Timestamps(GoldyBot.Extension):
    """Timestamps extension."""
    def __init__(self, package_module=None):
        super().__init__(self, package_module_name=package_module)

        self.default_timezone = "Europe/London"

        self.unknown_timezone_embed = GoldyBot.Embed(title="❤ Unknown Time Zone!", description="""
*This is how the ``timezone`` parameter should be used.*

``Europe/London`` = **Uk Time**
``America/New_York`` = **New York Time**
``Europe/Stockholm`` = **Sweden Time**

*The list goes on... To see the full list click [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).*
            """, colour=GoldyBot.utility.goldy.colours.RED
        ).set_thumbnail(GoldyBot.assets.ANIME_ONE_PUNCH_CLOCK_GIF)

    def loader(self):

        @GoldyBot.command(help_des="Sends a discord timestamp of that time and date.",slash_cmd_only=True, slash_options={
            "date" : GoldyBot.nextcord.SlashOption(description="The date goes here like example, 13.08.2022 or even 2022/08/22.", required=True),
            "time" : GoldyBot.nextcord.SlashOption(description="The time goes here like example, 15:00.", required=True),
            "flag" : GoldyBot.nextcord.SlashOption(description="Choose a flag.", required=True, choices={
                "08/13/2022": "d",
                "August 13, 2022": "D",
                "6:00 PM": "t",
                "6:00:00 PM": "T",
                "August 13, 2022 6:00 PM" : "f",
                "Saturday, August 13, 2022 6:00 PM" : "F",
                "in 3 hours": "R"
            }),
            "timezone" : GoldyBot.nextcord.SlashOption(description="The timezone to convert to; Goldy Bot defaults to Europe/London timezone.", required=False)
        })
        async def timestamp(self:Timestamps, ctx, date, time, flag, timezone=None):
            member = GoldyBot.Member(ctx)
            datetime = GoldyBot.utility.datetime.user_input.get_time_and_date(f"{date} {time}")
            timezone:str|None

            if timezone is None:
                member_data = await member.get_member_data()
                member_saved_timezone = member_data[member.member_id].get("timezone", None)

                if member_saved_timezone is None:
                    member_data[member.member_id]["timezone"] = self.default_timezone
                    await member.edit_member_data(member_data)
                    
                    timezone = member_data[member.member_id]["timezone"]
                else:
                    timezone = member_saved_timezone

            if not datetime == None:
                try:
                    # Convert to chosen timezone.
                    chosen_timezone = pytz.timezone(timezone)
                    datetime = chosen_timezone.normalize(chosen_timezone.localize(datetime, is_dst=True))

                    await send(ctx, f"<t:{int(datetime.timestamp())}:{flag}>")

                    return True

                except pytz.UnknownTimeZoneError as e:
                    GoldyBot.log("error", e)
                    message = await send(ctx, embed=self.unknown_timezone_embed)
                    
                except Exception as e:
                    GoldyBot.log("error", e)

                    message = await send(ctx, embed=GoldyBot.utility.goldy.embed.Embed(
                        title="❓ Did you enter it correctly?",
                        description="I couldn't read either your time or date properly, please could you try again. Perhaps you mistyped something.",
                        colour=GoldyBot.utility.goldy.colours.RED
                    ))

            else:
                message = await send(ctx, embed=GoldyBot.utility.goldy.embed.Embed(
                        title="❓ Did you enter it correctly?",
                        description="I couldn't read either your time or date properly, please could you try again. Perhaps you mistyped something.",
                        colour=GoldyBot.utility.goldy.colours.RED
                    )
                )

            await message.delete(delay=30)
            return False


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


def load():
    Timestamps(__name__)
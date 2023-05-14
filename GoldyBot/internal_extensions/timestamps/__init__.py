from __future__ import annotations

import GoldyBot
from GoldyBot.goldy.utils import time_and_date
from datetime import datetime

import pytz

class Timestamps(GoldyBot.Extension):
    """Timestamps extension from Goldy Bot V4 ported over to V5."""
    def __init__(self):
        super().__init__(self)

        self.default_timezone = "Europe/London"

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
        "timezone": GoldyBot.SlashOption(description="The timezone to use. Goldy Bot defaults to Europe/London timezone.", required=False)
    })
    async def timestamp(self, platter: GoldyBot.GoldPlatter, date, time, flag, timezone: str = None):
        datetime: datetime = time_and_date.phrase_both(f"{date} {time}")

        if timezone is None:
            member_data = await platter.author.get_database() # TODO: think about how this will be implemented.
            member_saved_timezone = member_data[member.member_id].get("timezone", None)

            if member_saved_timezone is None:
                member_data[member.member_id]["timezone"] = self.default_timezone
                await member.edit_member_data(member_data)
                
                timezone = member_data[member.member_id]["timezone"]
            else:
                timezone = member_saved_timezone

        if not datetime is None:
            try:
                # Convert to chosen timezone.
                chosen_timezone = pytz.timezone(timezone)
                datetime = chosen_timezone.normalize(chosen_timezone.localize(datetime, is_dst=True))

                posix_timestamp = int(datetime.timestamp())

                view = CopyButtonView(posix_timestamp, flag)

                await send(ctx, f"<t:{posix_timestamp}:{flag}>", view=view)

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


class CopyButtonView(GoldyBot.nextcord.ui.View):
    def __init__(self, posix_timestamp:int, flag:str):
        super().__init__()
        self.posix_timestamp = posix_timestamp
        self.flag = flag

        self.response_message:GoldyBot.nextcord.PartialInteractionMessage = None

    @GoldyBot.nextcord.ui.button(label="📋 Copy", style=GoldyBot.nextcord.ButtonStyle.gray)
    async def copy(self, button: GoldyBot.nextcord.ui.Button, interaction: GoldyBot.nextcord.Interaction):
        self.response_message = await interaction.response.send_message(f"``<t:{self.posix_timestamp}:{self.flag}>``", ephemeral=True)
        self.value = True


def load():
    Timestamps(__name__)
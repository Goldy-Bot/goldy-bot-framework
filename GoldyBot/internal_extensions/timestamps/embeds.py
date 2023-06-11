import GoldyBot

unknown_timezone_embed = GoldyBot.Embed(
    title = "❤ Unknown Time Zone!", 
    description = """
    *This is how the ``timezone`` parameter should be used.*

    ``Europe/London`` = **Uk Time**
    ``America/New_York`` = **New York Time**
    ``Europe/Stockholm`` = **Sweden Time**

    *The list goes on... To see the full list click [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).*
    """, 
    colour = GoldyBot.Colours.RED
)
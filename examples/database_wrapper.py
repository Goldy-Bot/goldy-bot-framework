import GoldyBot

# Need more help with creating extensions, visit our docs --> https://goldybot.devgoldy.xyz/goldy.extensions.html

from GoldyBot import DatabaseEnums

class Example(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

    @GoldyBot.command()
    async def rank(self, platter: GoldyBot.GoldPlatter):
        member_data = await platter.author.database # The database property is always async so you must await when retrieving it.

        # This is how we retrieve data from the database.
        rank = member_data.get("rank")

        await platter.send_message(f"Your rank is ``{rank}``. 😁")

    @GoldyBot.command()
    async def set_rank(self, platter: GoldyBot.GoldPlatter, rank: str):
        member_data = await platter.author.database

        # This is how we push data to the database.
        await member_data.push(
            type = DatabaseEnums.MEMBER_GUILD_DATA, # We set the type to guild data as we want our rank data to ONLY be stored within the guild.
            data = {"rank": int(rank)} # When we push, we push data back as a dictionary.
        )

        # Now you may think that this rank is up to date but that isn't true.
        await platter.send_message(f"Your old rank was *{member_data.get('rank')}*. 🤔")

        # You must run .update() if you would like an update to date rank.
        await member_data.update()

        # Now we're up to date with the database.
        await platter.send_message(f"Your new rank is now **{member_data.get('rank')}**. 😄")

        # So don't forget to .update() if you would like to pull up to date information from the database.

def load():
    Example()
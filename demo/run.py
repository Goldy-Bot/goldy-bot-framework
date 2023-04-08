import sys; sys.path.insert(0, '..')
import GoldyBot

GoldyBot.goldy_bot_logger.setLevel(GoldyBot.log.DEBUG) # Set logging level.

goldy = GoldyBot.Goldy() # Initialize goldy.

goldy.start() # Launch goldy bot.
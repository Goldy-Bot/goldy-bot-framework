"""
This module contains common things we send to discord, 
like e.g embeds, slash options the list goes on.

It also contains numerous http wrappers like ``send_msg()`` and ``get_channels()``.

If there's something you would like to get added, feel free to open an issue.
"""

DISCORD_CDN = "https://cdn.discordapp.com/"

from .embeds.embed import Embed, EmbedField, EmbedImage, EmbedFooter

from .slash_options.auto_complete import SlashOptionAutoComplete
from .slash_options.slash_option import SlashOption, SlashOptionChoice, SlashOptionTypes

from .defer import wait
from .messages.send_msg import send_msg
from .messages.delete_msg import delete_msg
from .guilds.get_channels import get_channels
from .guilds.get_guild_data import get_guild_data
from .channels.get_channel import get_channel
from .channels.delete_channel import delete_channel

from .files import File
from .colours import Colours
from .front_end_errors import FrontEndErrors
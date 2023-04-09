DISCORD_CDN = "https://cdn.discordapp.com/"

from .embeds.embed import Embed, EmbedField
from .slash_options.slash_option import SlashOption, SlashOptionChoice

from .messages.send_msg import send_msg
from .messages.delete_msg import delete_msg

from .colours import Colours
from .params import params_to_options, invoke_data_to_params, get_function_parameters
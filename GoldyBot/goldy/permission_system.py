from __future__ import annotations
from typing import TYPE_CHECKING
from discord_typings import GuildMemberData

from nextcore.http import Route
from devgoldyutils import LoggerAdapter, Colours

from .perms import Perms
from .. import goldy_bot_logger

if TYPE_CHECKING:
    from . import Goldy
    from .objects.platter.golden_platter import GoldPlatter

class PermissionSystem():
    """A goldy bot class that contains methods to handle member/command permissions."""
    def __init__(self, goldy: Goldy) -> None:
        self.goldy = goldy

        self.logger = LoggerAdapter(goldy_bot_logger, prefix=Colours.PURPLE.apply("PermissionSystem"))

    async def got_perms(self, platter: GoldPlatter) -> bool: # TODO: I might rename this method.
        """Method that checks if the command author has the perms to run this command."""
        
        if not platter.invokable.required_perms == []:
            self.logger.debug("Checking if member has perms to run command...")

            # If the required roles contain 'bot_dev' and the bot dev is running the command allow the command to execute.
            # --------------------------------------------------------------------------------------------------------------
            if Perms.BOT_DEV in platter.invokable.required_perms:
                if platter.author.id == self.goldy.config.bot_dev:
                    self.logger.debug("Member is a bot developer :)")
                    return True

            # TODO: Add bot admin.

            # Server owner check.
            # --------------------
            if Perms.GUILD_OWNER in platter.invokable.required_perms:
                if platter.author.id == platter.guild.get("owner_id"):
                    self.logger.debug("Member is server owner ✅")
                    return True

            # Check if member has any of the required roles.
            #----------------------------------------------------

            # Get the member's guild data.
            r = await self.goldy.http_client.request(
                Route(
                    "GET",
                    "/guilds/{guild_id}/members/{user_id}",
                    guild_id = platter.guild.id,
                    user_id = platter.author.id
                ),
                rate_limit_key = self.goldy.nc_authentication.rate_limit_key,
                headers = self.goldy.nc_authentication.headers,
            )

            member_data: GuildMemberData = await r.json()

            for role_code_name in platter.invokable.required_perms:

                if role_code_name not in Perms:
                    try:
                        role_id_uwu = platter.guild.config_wrapper.roles[role_code_name]
                    except KeyError:
                        # Maybe there is a better way of handling this but I'll leave this as temporary solution for now.
                        self.logger.error(
                            f"This guild ({platter.guild.code_name}) hasn't been configured to include the required role '{role_code_name}' you entered for the command '{platter.invokable.name}'."
                        )
                        return False

                    # Loop through each role of the member and check if the role id is equal to that required.
                    for member_role_id in member_data["roles"]:
                        if str(member_role_id) == role_id_uwu:
                            self.logger.debug(f"The author has the required role '{role_code_name}' :)")
                            return True
                    

                    # TODO: Might be better to create a Role() object and add a .has_role() method to Member object.

            self.logger.info("The author has no perms to run this command.")
            return False

        self.logger.debug("This command has no required perms. Your free! 🔓")
        return True
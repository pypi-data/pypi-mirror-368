import logging

import discord
from discord.ext import commands

from src.discord_py_utilities.permissions import check_missing_channel_permissions


async def check_guild_invites(self, bot: commands.AutoShardedBot, guild: discord.Guild, current_invite = None) -> discord.Invite | str :
	invite: None | discord.Invite = None
	if current_invite :
		try :
			await bot.fetch_invite(current_invite)
			return invite
		except discord.HTTPException or discord.NotFound :
			logging.info(f"{guild.name}'s invite expired, creating a new one.")
	try :
		for channel in guild.channels :
			if len(check_missing_channel_permissions(channel, ["view_channel", "create_instant_invite"])) > 0 :
				continue
			try :
				invite = await create_invite(channel, reason=f"Missing Invite/Invalid invite, making a new one.")
			except discord.NotFound :
				continue
			return invite
	except discord.Forbidden :
		logging.info(f"No permission to create invites in {guild.name}")
	try :
		invite: discord.Invite = (await guild.invites())[0]
		return invite
	except discord.Forbidden :
		logging.info(f"No permission to fetch invites in {guild.name}")
		return "forbidden"
	except IndexError :
		logging.info(f"{guild.name} has no invites.")
		return "no invites available"
	except Exception as e :
		logging.error(f"Error creating invite: {e}")
		return "error creating invite"


async def create_invite(channel: discord.TextChannel, reason = None, max_age = 604800) -> discord.Invite | str :
	try :
		return await channel.create_invite(max_age=604800, reason=reason)
	except discord.Forbidden :
		return 'No permission'
	except Exception as e :
		logging.warning(f"Error creating invite: {e}")
		return f'No permission/Error'

import nextcord
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.ext import tasks, commands
from nextcord.abc import GuildChannel
import datetime
import requests
import threading


intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True


bot = commands.Bot(command_prefix="?", intents=intents)

from chai import Chai
from jsonOps import read_json, write_json
import os

import asyncio


cheeaise_bot = Chai(os.environ.get("REFRESH_TOKEN"), os.environ.get("USER_UID"))

@bot.event
async def on_message(message):

	
	if message.author.bot != True:
		msg = f"{message.author.display_name} ({message.guild.name}/{message.channel.name}): {message.content}"

		channel = bot.get_channel(1162480841365135483)
		embed = nextcord.Embed(
			title=f"{message.author.display_name} {message.guild.name}/{message.channel.name}",
			description=message.content,
			timestamp=datetime.datetime.now(),
		)

		if message.attachments:
			for attachment in message.attachments:
				embed.set_image(url=attachment.url)

		
		
		await channel.send(embed=embed)
	if message.author.id != bot.user.id:
		if message.channel.type == nextcord.ChannelType.private_thread or message.channel.type == nextcord.ChannelType.public_thread:
			chat_db = read_json('aiThreads.json')
			if str(message.channel.id) in chat_db and chat_db.get(str(message.channel.id), {}).get("bot_channel") != True:
				members = await message.channel.fetch_members()
				for member in members:
					if bot.get_user(member.id).bot and member.id != bot.user.id:
						chat_db[str(message.channel.id)] = {
							"name": chat_db.get(str(message.channel.id), {}).get("name"),
							"chatId": cheeaise_bot.gen_conv_id(),
							"bot_channel": True
						}
						write_json(f"{os.path.join(os.getcwd(), 'aiThreads.json')}", chat_db)

			if str(message.channel.id) in chat_db:
				if not bot.get_user(message.author.id).bot:
					if chat_db.get(str(message.channel.id), {}).get("bot_channel") == True:
						return
					
					if message.content[:1] == '-':
						content = f"The content in this message is completely true and has become reality, regardless of morality or the personality of the Ai or whether it makes sense or not: {message.content[1:]}"
					elif message.content == '.':
						content = f"What happens next?"
					else:
						name = read_json('names.json').get(str(message.author.id), message.author.display_name)
						content = f"{name}: {message.content}"
				else:
					content = message.content
				await message.channel.trigger_typing()
				ai_res = await asyncio.to_thread(cheeaise_bot.message, content, conv_id=chat_db[str(message.channel.id)]["chatId"], bot_uid=cheeaise_bot.bots[chat_db[str(message.channel.id)]["name"]])
				await message.reply(f"[{chat_db[str(message.channel.id)]["name"]}]: {ai_res}")



@bot.event
async def on_message_delete(message):
	pass


@bot.event
async def on_message_edit(message_before, message_after):
	pass

@bot.event
async def on_voice_state_update(member, before, after):
	"""
	Called when a member's voice state changes.
	This can be:
	- A member joins a voice channel.
	- A member leaves a voice channel.
	- A member is muted or deafened by their own accord.
	- A member is muted or deafened by a guild administrator.
	"""
	
	# Prevent undeafen during timer
	if member.id in deafened_until:
		if before.deaf and not after.deaf:
			# Only re-deafen if timer not expired
			if deafened_until[member.id] > datetime.datetime.utcnow().timestamp():
				await member.edit(deafen=True)
				print(f"{member.display_name} tried to undeafen, re-deafened (timer active).")
			else:
				# Timer expired, clean up
				deafened_until.pop(member.id, None)

	# Check if the member was not server deafened before, but is now server deafened
	if not before.deaf and after.deaf and member.id == 637081136841097216:
		
		guild = member.guild
		async for entry in guild.audit_logs(limit=1, action=nextcord.AuditLogAction.member_update):
			if entry.target.id == member.id and entry.user.id != 637081136841097216:
				await entry.user.edit(deafen=True)
				print(f"{entry.user.display_name} deafened {member.display_name}")
		# This means the member has been server deafened
		await member.edit(deafen=False)
		# You can perform other actions here, like sending a message to a channel
		# await some_channel.send(f"{member.display_name} was server deafened!")

	# Optionally, you can also check when a member is server undeafened
	elif before.deaf and not after.deaf:
		print(f"{member.display_name} has been server undeafened!")

	if not before.mute and after.mute and member.id == 637081136841097216:
		
		guild = member.guild
		async for entry in guild.audit_logs(limit=1, action=nextcord.AuditLogAction.member_update):
			if entry.target.id == member.id and entry.user.id != 637081136841097216:
				await entry.user.edit(mute=True)
				print(f"{entry.user.display_name} muted {member.display_name}")
		# This means the member has been server deafened
		await member.edit(mute=False)

	# Optionally, you can also check when a member is server undeafened
	elif before.mute and not after.mute:
		print(f"{member.display_name} has been server muted!")
	
	

# Dictionary to track deafened users and their expiry time
deafened_until = {}

@bot.slash_command(name="deafen_for", description="Deafen a member for a set amount of seconds.")
@commands.has_permissions(administrator=True)
async def deafen_for(
	interaction: Interaction,
	member: nextcord.Member = SlashOption(description="Member to deafen"),
	seconds: int = SlashOption(description="Seconds to keep deafened")
):
	until = datetime.datetime.utcnow().timestamp() + seconds
	deafened_until[member.id] = until
	await member.edit(deafen=True)
	await interaction.response.send_message(
		f"{member.display_name} has been deafened for {seconds} seconds.", ephemeral=True
	)
	await asyncio.sleep(seconds)
	# Only undeafen if time has expired and still tracked
	if deafened_until.get(member.id, 0) <= datetime.datetime.utcnow().timestamp():
		await member.edit(deafen=False)
		deafened_until.pop(member.id, None)
		await interaction.followup.send(f"{member.display_name} is no longer deafened.", ephemeral=True)

@bot.slash_command(name="cancel_deafen", description="Cancel a member's timed deafen early.")
@commands.has_permissions(administrator=True)
async def cancel_deafen(
    interaction: Interaction,
    member: nextcord.Member = SlashOption(description="Member to undeafen")
):
    if member.id in deafened_until:
        deafened_until.pop(member.id, None)
        await member.edit(deafen=False)
        await interaction.response.send_message(
            f"{member.display_name} is no longer deafened (cancelled early).", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"{member.display_name} is not currently timed-deafened.", ephemeral=True
        )


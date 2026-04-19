# type: ignore
import nextcord
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.ext import tasks, commands
from nextcord.abc import GuildChannel
import sys
import asyncio

#HelloWorld(print)

from dotenv import load_dotenv
load_dotenv()
from jsonOps import read_json, write_json



copy = ''
spec = False
server = 1155656128173178960

from botevents import *  # make sure this imports your bot instance

@bot.slash_command(name="restart", description="Restart the bot.")
@commands.has_permissions(administrator=True)
async def restart(interaction: nextcord.Interaction):
	if interaction.user.id == 637081136841097216:
		await interaction.response.send_message("Restarting bot...", ephemeral=True)
		os.execv(sys.executable, [sys.executable] + sys.argv)
	else:
		await interaction.response.send_message("Missing permissions.", ephemeral=True)

@bot.slash_command(name="die", description="Kill the bot.")
@commands.has_permissions(administrator=True)
async def die(interaction: nextcord.Interaction):
	if interaction.user.id == 637081136841097216:
		await interaction.response.send_message("Killing bot...", ephemeral=True)
		await bot.close()
		sys.exit(0)
	else:
		await interaction.response.send_message("Missing permissions.", ephemeral=True)

@bot.event
async def on_ready():
	user = bot.get_user(637081136841097216)
	await user.send("Cheesebot on!")

"""
@bot.slash_command(name="join", description="Make the bot join a voice channel")
async def join(
	interaction: Interaction,
	channel: nextcord.VoiceChannel = SlashOption(
		name="channel",
		description="Voice channel to join",
		required=False,
		channel_types=[ChannelType.voice]
	)
):
	await interaction.response.defer(ephemeral=True)

	# Determine channel
	if channel is None:
		if not interaction.user.voice:
			await interaction.followup.send("You must be in a voice channel or specify one.")
			return
		channel = interaction.user.voice.channel

	vc = interaction.guild.voice_client
	

	try:
		if vc and vc.is_connected():
			await vc.move_to(channel)
			await interaction.followup.send(f"Moved to **{channel.name}**")
		else:
			# Optional: timeout so it doesn't hang forever
			vc = await asyncio.wait_for(channel.connect(), timeout=10)
			await interaction.followup.send(f"Joined **{channel.name}**")
			
	except asyncio.TimeoutError:
		print(interaction.guild.voice_client)
		await interaction.followup.send("Connection timed out.")
	except Exception as e:
		await interaction.followup.send(f"Error: {e}")

@bot.slash_command(name="leave", description="Make the bot leave the voice channel")
async def leave(interaction: Interaction):
	await interaction.response.defer(ephemeral=True)

	vc = interaction.guild.voice_client

	if not vc or not vc.is_connected():
		await interaction.followup.send("Not in a voice channel.")
		return

	try:
		await vc.disconnect()
		await interaction.followup.send("Disconnected.")
	except Exception as e:
		await interaction.followup.send(f"Error: {e}")
"""
@bot.slash_command(name="name", description="Name yourself in the bot's eyes.")
async def name(interaction: nextcord.Interaction, name: str = nextcord.SlashOption(required=False, name="name")):
	if name == None:
		name = interaction.user.display_name
	await interaction.response.send_message(f"Your name has been set to {name}.", ephemeral=True)
	write_json("names.json", {interaction.user.id: name})

@bot.slash_command(name="create_thread", description="Start a new thread")
async def create_thread(interaction: nextcord.Interaction, character: str = nextcord.SlashOption(required=False, name="characters", choices=list(cheeaise_bot.bots.keys())), bot_uid: str = nextcord.SlashOption(required=False, name="bot_uid")):
	# This creates a public thread in the current channel
	if character == None:
		if bot_uid == None:
			await interaction.response.send_message("Please provide a character or bot UID.", ephemeral=True)
			return
		bot_info = cheeaise_bot.get_char_info(bot_uid)
		name = bot_info.get("name", "Unknown Character")
	else:
		bot_uid = cheeaise_bot.bots[character]
		bot_info = cheeaise_bot.get_char_info(cheeaise_bot.bots[character])
		name = character
	conv_id = cheeaise_bot.gen_conv_id()
	thread = await interaction.channel.create_thread(name = f"Session {conv_id}", type=nextcord.ChannelType.public_thread, auto_archive_duration=60)
	
	await thread.add_user(interaction.user)
	await interaction.response.send_message(f"Thread 'Session {conv_id}' created!", ephemeral=True)
	thread_data = {
		"name": name,
		"chatId": conv_id
	}
	await thread.send(f"{name}: {cheeaise_bot.message(conv_id=thread_data["chatId"], bot_uid=bot_uid)}")
	write_json("aiThreads.json", {str(thread.id): thread_data})

@bot.slash_command(name="add_to_thread", description="Add to an existing thread")
async def add_to_thread(interaction: nextcord.Interaction, character: str = nextcord.SlashOption(required=False, name="characters", choices=list(cheeaise_bot.bots.keys())), bot_uid: str = nextcord.SlashOption(required=False, name="bot_uid")):
	# This adds to an existing thread
	if character == None:
		if bot_uid == None:
			await interaction.response.send_message("Please provide a character or bot UID.", ephemeral=True)
			return
		bot_info = cheeaise_bot.get_char_info(bot_uid)
		name = bot_info.get("name", "Unknown Character")
	else:
		bot_uid = cheeaise_bot.bots[character]
		bot_info = cheeaise_bot.get_char_info(cheeaise_bot.bots[character])
		name = character
	conv_id = cheeaise_bot.gen_conv_id()
	thread = interaction.channel
	if isinstance(thread, nextcord.Thread):
		await interaction.response.send_message(f"Added to thread '{thread.name}'!", ephemeral=True)
		thread_data = {
			"name": name,
			"chatId": conv_id
		}
		await thread.send(f"{name}: {cheeaise_bot.message(conv_id=conv_id, bot_uid=bot_uid)}")
		write_json("aiThreads.json", {str(thread.id): thread_data})
	else:
		await interaction.response.send_message("This command can only be used in a thread.", ephemeral=True)

@bot.slash_command(name="delete_from_thread", description="Delete an existing thread")
async def delete_thread(interaction: nextcord.Interaction, thread: nextcord.Thread = nextcord.SlashOption(required=False, name="thread")):
	if thread == None:
		if isinstance(interaction.channel, nextcord.Thread):
			thread = interaction.channel
		else:
			await interaction.response.send_message("Please provide a thread or use this command in a thread.", ephemeral=True)
			return
	async with chat_db_lock:
		if isinstance(thread, nextcord.Thread) and str(thread.id) in chat_db:
			chat_db.pop(str(thread.id), None)
			write_json("aiThreads.json", chat_db)
			await interaction.response.send_message(f"Deleted from thread '{thread.name}'!", ephemeral=True)
			
		else:
			await interaction.response.send_message("This command can only be used in a valid thread.", ephemeral=True)

async def main():
	# run bot (blocks until disconnect)
	await bot.start(os.environ.get('DISCORD_BOT_TOKEN'))

if __name__ == '__main__':
	asyncio.run(main())


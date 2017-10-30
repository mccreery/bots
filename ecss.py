#!/usr/bin/env python3

import discord, re, config
from datetime import datetime
client = discord.Client()

conf = config.config()

pending = []
server = role = requests = commands = None

DISCORD_EPOCH = datetime(2015, 1, 1).timestamp()

def get_id(id):
	try:
		x = int(id)

		return x if x >= 159799960412356608 \
			and (x >> 22) < int(datetime.utcnow().timestamp() - DISCORD_EPOCH)*1000 else None
	except ValueError: return None

#async def check_channels(*channels):
#	for channel in channels or server.channels:
#		print("Checking channel " + channel.name, type(channel))
#		if not channel.id in ["367779135533219840", "367781106461966346"] \
#				and channel.overwrites_for(client.user).read_messages:
#			overwrites = channel.overwrites_for(role)
#
#			if overwrites.read_messages != False:
#				print("Overwriting channel " + channel.name)
#				overwrites.read_messages = False
#				await client.edit_channel_permissions(channel, role, overwrites)

#@client.event
#async def on_channel_create(channel):
#	if channel in server.channels:
#		await check_channels(channel)

@client.event
async def on_ready():
	global server, role, requests, commands

	server = client.get_server("134307089823563776")
	requests = server.get_channel("367780140870139904")
	commands = server.get_channel("367779135533219840")

	role = discord.utils.find(lambda role: role.name == "User Bot", server.roles) \
		or await client.create_role(server, name="User Bot")

	#await check_channels()

@client.event
async def on_member_join(member):
	if member.bot:
		for pair in pending:
			if pair[1] == member:
				await client.add_roles(member, role)
				await client.send_message(commands, "{} :white_check_mark: Your bot `` {} `` has been accepted.".format(pair[0].mention, pair[1].name))

@client.event
async def on_reaction_add(reaction, user):
	print(reaction.name)
	if user != client.user and reaction:
		entry = discord.utils.find(lambda entry: entry[2] == reaction.message, pending)
		if entry:
			await client.send_message(commands, "{} :no_entry_sign: Your bot `` {} `` has been denied.".format(entry[0].mention, entry[1].name))

async def add_bot(message, id):
	id = get_id(id)
	if id is None: return False

	bot = None
	try:
		bot = await client.get_user_info(id)
	except (discord.NotFound, discord.HTTPException): return False

	if not bot.bot or bot in server.members: return False

	link = "https://discordapp.com/api/oauth2/authorize?client_id={}&scope=bot&guild_id={}".format(bot.id, conf["Servers"]["ecss"])

	await client.send_message(message.channel, "{} :white_check_mark: Your bot `` {} `` has been submitted.".format(message.author.mention, bot.name))
	pending.append((
		message.author,
		bot,
		await client.send_message(requests, "{} has requested for their bot `` {} `` to be added to the server. Use the following link to accept, or react :no_entry_sign: to deny.\n<{}>".format(
			message.author.mention, bot.name, link))
	))
	await client.add_reaction(pending[-1][2], "🚫")
	return True

@client.event
async def on_message(message):
	parts = message.content.split()
	if message.channel == commands and len(parts) == 2 and parts[0].lower() == "add":
		if not await add_bot(message, parts[1]):
			await client.send_message(message.channel, "{} :warning: The ID `` {} `` is not a valid Discord bot.".format(message.author.mention, parts[1]))

client.run(conf["Tokens"]["ecss"])

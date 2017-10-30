#!/usr/bin/env python3

import asyncio, discord, config
from datetime import datetime
from string import Formatter
client = discord.Client()
conf = config.config()

class LogFormatter(Formatter):
	def format_field(self, value, spec):
		if type(value) is datetime:
			value = value.strftime(
				"**%Y**-**%m**-**%d** **%H**\:**%M**\:**%S**")
		elif type(value) is discord.Member or type(value) is discord.User:
			value = "**{}**#_{}_ (_{}_)".format(
				value.name, value.discriminator, value.id)
		elif type(value) is discord.Message:
			value = "`" + value.content + "`"

		return super().format_field(value, spec)

async def log(message, *args, channel=None):
	return await client.send_message(channel or log_channel,
		LogFormatter().format(message, *args))

@client.event
async def on_ready():
	print("Sam") # Just so I know which one to close
	global main_channel, log_channel

	main_channel = client.get_channel(conf["Channels"]["sam"])
	log_channel  = client.get_channel(conf["Channels"]["tests"])

@client.event
async def on_member_join(member):
	await log("Member joined: {}", member)
	await client.send_message(main_channel,
		member.mention + " `Welcome, brother Sam.`")

pending_attachments = {}

@client.event
async def on_member_update(before, after):
	if after.id != conf["Users"]["me"]:
		return

	server = main_channel.server.icon != after.avatar
	bot = client.user.avatar != after.avatar

	if server or bot:
		print("Found new avatar:", after.avatar_url)
		data = await request(client.http, "GET", after.avatar_url)
		if server:
			await client.edit_server(main_channel.server, icon=data)
		if bot:
			await client.edit_profile(avatar=data)

@client.event
async def on_message(message):
	if type(message.channel) is discord.PrivateChannel \
			and len(message.attachments) > 0:
		await log("Submitted for review.", channel=message.channel)
		pending = await log("{} ({}) sent {} {}",
			message.author.mention, message.author, message, message.attachments[0]["url"])
		#pending_attachments[pending.id] = message
		await client.add_reaction(pending, "👍")
		await client.add_reaction(pending, "👎")
		reaction = await client.wait_for_reaction(["👎", "👍"], check=lambda reaction, user: user != client.user, message=pending)
		if reaction.reaction.emoji == "👍":
			await log("Sent by {}:\n{}{}\n_Images are moderated. " \
				"To send an image, DM it to this bot._",
				message.author.mention, message.content \
					+ (" " if len(message.content) > 0 else ""),
				message.attachments[0]["url"], channel=main_channel)

			#data = {
			#	"embeds": [{
			#		"title": "Sent by " + message.author.mention,
			#		"image": {"url": message.attachments[0]["url"]},
			#		"description": message.content,
			#		"author": {
			#			"name": message.author.display_name,
			#			"icon_url": message.author.avatar_url
			#		},
			#		"footer": {
			#			"text": "Images are moderated. " \
			#				"To send an image, DM it to the bot."
			#		}
			#	}]
			#}
			#await client.http.post(conf["Webhooks"]["moderator"], json=data)

			await log("Your image {} has been accepted.",
				message.attachments[0]["url"], channel=message.author)
		else:
			await log("Your image {} has been declined.",
				message.attachments[0]["url"], channel=message.author)

	if message.channel.id == conf["Channels"]["mimike"] \
			and message.content.startswith("$mimic"): # Duplicates
		cmd = message.content[6:].split(' ', 2)
		user = discord.utils.find(lambda m: m.mention == cmd[1],
			message.mentions)
		data = {
			"content": cmd[2],
			"username": user.display_name,
			"avatar_url": user.avatar_url
		}
		await client.http.post(conf["Webhooks"]["mimike"], json=data)
	elif message.channel.id == "" \ # Unknown value
			and message.content.startswith(client.user.mention):
		data = {
			"content": message.content[len(client.user.mention):]
		}
		await client.http.post("", json=data) # Unknown value

@client.event
async def on_member_remove(member):
	await log("Member left: {}", member)
	await client.send_message(main_channel, "Brothers, an unsamly one {} has revealed themselves. Rejoice in freedom from the curse of the uninitiated.".format(member.mention))

@client.event
async def on_message_delete(message):
	if message.channel != main_channel or message.author.bot: return

	log_message = "{} deleted {}, posted {}"
	if message.edited_timestamp: log_message += ", edited {}"

	await log(log_message, message.author, message, message.timestamp,
		message.edited_timestamp if message.edited_timestamp else None)

@client.event
async def on_message_edit(before, after):
	if before.channel == main_channel and before.content != after.content:
		await log("{} edited {} to {}, posted {}",
			before.author, before, after, before.timestamp)
	#elif before.channel == log_channel \
	#		and before.id in pending_attachments \
	#		and not before.pinned and after.pinned:
	#	await client.unpin_message(after)
	#	pending = pending_attachments[before.id]
	#	await log("Sent by {}:\n{}{}\n_Images are moderated. " \
	#		"To send an image, DM it to this bot._",
	#		pending.author.mention, pending.content \
	#			+ (" " if len(pending.content) > 0 else ""),
	#		pending.attachments[0]["url"], channel=main_channel)
	#	await log("Your image {} has been accepted.",
	#		pending.attachments[0]["url"], channel=pending.author)

@asyncio.coroutine
def request(http, method, url, *, bucket=None, **kwargs):
	lock = http._locks.get(bucket)
	if lock is None:
		lock = asyncio.Lock(loop=http.loop)
		if bucket is not None:
			http._locks[bucket] = lock

	kwargs['headers'] = {'User-Agent': http.user_agent}

	with (yield from lock):
		try:
			r = yield from http.session.request(method, url, **kwargs)
			data = yield from r.content.read()
			return data
		finally:
			yield from r.release()

client.run(conf["Tokens"]["sam"])

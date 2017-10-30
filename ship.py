#!/usr/bin/env python3

import discord, config
client = discord.Client()
conf = config.config()

@client.event
async def on_message(message):
	if message.channel.id == conf["Channels"]["bot_hole"] and message.content.startswith("rate this ship pls") and len(message.mentions) >= 2:
		a = message.mentions[0].name
		b = message.mentions[1].name
		rating = sum(ord(a[i])*5 | ord(b[i])*3 for i in range(min(len(a), len(b))))

		await client.send_message(message.channel, "i rate this {}/10".format(rating % 11))

client.run(conf["Tokens"]["stephen"])

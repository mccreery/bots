#!/usr/bin/env python3

import discord, asyncio, config
client = discord.Client()
conf = config.config()

@client.event
async def on_message(message):
	if message.content == "load" and message.author.id == conf["Users"]["me"]:
		start = 0
		while True:
			print("Editing to ")
			await client.edit_message(message, chr((start & 3) | 0x25DC))
			start += 1
			await asyncio.sleep(.5)

client.run(conf["Tokens"]["user"], bot = False)

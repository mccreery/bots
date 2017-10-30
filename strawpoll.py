#!/usr/bin/env python3

import discord, json, shlex, config
client = discord.Client()

@client.event
async def on_message(message):
	if message.content[0] == "$":
		cmd = shlex.split(message.content[1:])
		if cmd[0] == "sp" or cmd[0] == "strawpoll":
			response = await client.http.post(
				"https://strawpoll.me/api/v2/polls",
				json={"title": cmd[1], "options": cmd[2:]})

			response = json.loads(response)
			await client.send_message(message.channel,
				"http://strawpoll.me/" + str(response["id"]))

client.run(config.config()["Tokens"]["sam"])

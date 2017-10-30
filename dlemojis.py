#!/usr/bin/env python3

import discord, sys, os, urllib.request, config
client = discord.Client()

@client.event
async def on_ready():
	server_id = sys.argv[1]
	server = client.get_server(server_id)

	if not os.path.exists(server.name):
		os.makedirs(server.name)

	for emoji in server.emojis:
		filename = server.name + "/" + emoji.name + ".png"
		if os.path.isfile(filename): pass

		with open(filename, "wb") as file:
			req = urllib.request.Request(emoji.url, headers={"User-Agent": "Mozilla/5.0"})

			with urllib.request.urlopen(req) as remote:
				file.write(remote.read())

	print("Done!")

client.run(config.config()["Tokens"]["user"], bot=False)

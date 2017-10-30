#!/usr/bin/env python3

import discord, random, config

client = discord.Client()
server = runner = target = None
conf = config.config()

@client.event
async def on_ready():
	global server, runner, target, channels

	server = client.get_server(conf["Servers"]["jar"])
	runner = server.get_member(conf["Users"]["me"])
	target = server.get_member(conf["Users"]["me"])

	print("Runner: {}\nTarget: {}\nServer: {}".format(runner, target, server))

	channels = list(filter(lambda channel:
		channel != server.afk_channel and channel.permissions_for(target).connect, server.channels))

@client.event
async def on_voice_state_update(before, after):
	if runner.voice.voice_channel == target.voice.voice_channel:
		await client.move_member(runner, random.choice(channels))

client.run(conf["Tokens"]["user"], bot=False)

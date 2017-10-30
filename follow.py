#!/usr/bin/env python3

import discord, random, config

client = discord.Client()
server = follower = target = None
conf = config.config()

@client.event
async def on_ready():
	global server, follower, target, channels

	server = client.get_server(conf["Servers"]["jar"])
	follower = server.get_member(conf["Users"]["me")
	target = server.get_member(conf["Users"]["me"])

	print("follower: {}\nTarget: {}\nServer: {}".format(follower, target, server))

@client.event
async def on_voice_state_update(before, after):
	if follower.voice.voice_channel != target.voice.voice_channel:
		await client.move_member(follower, target.voice.voice_channel)

client.run(conf["Tokens"]["stephen"])

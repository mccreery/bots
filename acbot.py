#!/usr/bin/env python3

import discord, subprocess, sys, config
client = discord.Client()
conf = config.config()

root = conf["Misc"]["music"]

@client.event
async def on_ready():
	voice = await client.join_voice_channel(client.get_channel(conf["Channels"]["lowest"]))
	r, c = str(voice.encoder.sampling_rate), str(voice.encoder.channels)

	gen = subprocess.Popen([conf["Misc"]["music"] + "/acmusic.exe"], cwd=conf["Misc"]["music"], stdout=subprocess.PIPE, stderr=sys.stdout.buffer)

	# Basically just converts to the correct sample rate
	# I could be doing this myself
	stream = subprocess.Popen([
			"ffmpeg",
			"-f", "s16le", "-ar", "32728", "-ac", "2", "-i", "pipe:0",
			"-f", "s16le", "-ar", r, "-ac", c, "pipe:1",
			"-loglevel", "warning"
		], cwd=conf["Misc"]["music"], stdin=gen.stdout, stdout=subprocess.PIPE, stderr=sys.stdout.buffer)

	discord.voice_client.ProcessPlayer(stream, voice, None).start()

client.run(conf["Tokens"]["sam"])

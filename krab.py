#!/usr/bin/env python3

import discord, random, requests, asyncio, json, config
client = discord.Client()
conf = config.config()

async def get_playlist(id):
	loop = asyncio.get_event_loop()
	grabber = loop.run_in_executor(None, requests.get, "https://www.googleapis.com/youtube/v3/playlistItems?key=" + conf["Tokens"]["youtube"] + "&part=contentDetails&playlistId=" + id)
	data = await grabber

	playlist = json.loads(data.content.decode("utf-8"))["items"]
	return list(item["contentDetails"]["videoId"] for item in playlist)

@client.event
async def on_ready():
	server = client.get_server(conf["Server"]["bikini"])
	channel = server.get_channel(conf["Channel"]["krusty"])
	voice = await client.join_voice_channel(channel)

	playlist = await get_playlist("PLX7wEO2r1BhZh7Nb3NkIt2FDtIOcuEPi3")
	while True:
		player = await voice.create_ytdl_player("http://youtube.com/watch?v=" + random.choice(playlist), options="-af volume=0.1")
		player.start()
		while not player.is_done(): await asyncio.sleep(1)

client.run(conf["Tokens"]["sailor"])

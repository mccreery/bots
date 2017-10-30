#!/usr/bin/env python3

import discord, sys, argparse, os, config
client = discord.Client()
conf = config.config()

MOTD_MIMIC = 0

parser = argparse.ArgumentParser()
parser.add_argument("file")
parser.add_argument("channel", nargs="?", default="ninth")
parser.add_argument("-t", "--token", default="stephen")
parser.add_argument("-r", "--root")
parser.add_argument("--music", action="store_const",
	const=r"E:\Users\Sam\Music", dest="root")
parser.add_argument("-m", "--motd", nargs="?", const=MOTD_MIMIC)
parser.add_argument("-v", "--volume", default="100")
args = parser.parse_args()

if args.token and args.token in conf["Tokens"]:
	args.token = conf["Tokens"][args.token]
if args.channel and args.channel in conf["Channels"]:
	args.channel = conf["Channels"][args.channel]

if args.root:
	args.file = os.path.join(args.root, args.file)
if args.motd == MOTD_MIMIC:
	args.motd, _ = os.path.splitext(os.path.basename(args.file))
	args.motd = args.motd.title()

try:
	args.volume = int(args.volume)
	if args.volume < 0: raise
except: args.volume = 100

@client.event
async def on_ready():
	if not args.motd is None:
		await client.change_presence(game=discord.Game(name=args.motd))

	(await client.join_voice_channel(client.get_channel(args.channel))) \
		.create_ffmpeg_player(args.file, before_options="-stream_loop -1", options="-af volume=" + str(args.volume / 100)) \
		.start()

client.run(args.token)

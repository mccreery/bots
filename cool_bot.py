#!/usr/bin/env python3

import discord, asyncio, random, os, atexit, msvcrt, re, config
from datetime import datetime

conf = config.config()

COMMAND_FILTER = lambda message: message.channel.id == conf["Channels"]["bot_hole"]
HELP_FORMAT = "**{}** - {}"
USAGE_FORMAT = "\tUsage: _{}_"
RULE_FORMAT = "**{}.)** {}"
ALIASES_FORMAT = "\tAliases: _{}_"

client = discord.Client()

def purify(raw):
	to_replace = []
	for i in range(len(raw)):
		if raw[i] in "*_`~":
			to_replace.append(i)

	offset = 0
	for x in to_replace:
		x += offset
		raw = raw[:x] + '\\' + raw[x:]
		offset += 1
	return raw

commands = {}
class Command(object):
	def __init__(self, name, description, function, usage=None):
		self.name = name
		self.description = description
		self.function = function
		self.usage = usage
		self.aliases = []

	def register(self):
		commands[self.name] = self
	async def add_alias(self, alias):
		self.aliases.append(alias)
	async def get_help(self):
		output = HELP_FORMAT.format(self.name, self.description)
		if self.usage:
			output += '\n' + USAGE_FORMAT.format(self.usage)
		if len(self.aliases):
			output += '\n' + ALIASES_FORMAT.format(', '.join(self.aliases))
		return output

async def get_command(name):
	if name in commands:
		return commands[name]
	else:
		for command in commands:
			if name in commands[command].aliases:
				return commands[command]
	return None

def get_timestamp(sep='-', col=':'):
	return datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S" \
		.replace('-', sep).replace(':', col))

import sys
current_log = sys.stdout
#current_log = open("logs/log_{}.log".format(get_timestamp(col='-')), "w")
atexit.register(current_log.close)
def log(message):
	message = "[{}] {}".format(get_timestamp(), message)
	current_log.write(message + '\n')
	print(message)

message_interim = 0
last_channel = None

SPEAK_WHITELIST = list(conf["Users"][user] for user in [
	"me", "charlie", "ruben", "chris", "becca", "ollie"
])

@client.event
async def on_message(message):
	global message_interim, last_channel
	if message.author.bot: return

	if type(message.channel) is discord.PrivateChannel:
		if message.author.id in SPEAK_WHITELIST:
			cmd = message.content.split()
			if cmd[0][0] == '#':
				new_channel = None
				for channel in client.get_all_channels():
					if channel.name == cmd[0][1:]:
						new_channel = channel
						break
				cmd = cmd[1:]

				if new_channel is None:
					await client.send_message(message.channel,
						"Unable to find channel **" + cmd[0][1:] + "**")
					return
				else:
					last_channel = new_channel

			if not last_channel is None:
				if len(cmd) != 0:
					cmd = ' '.join(cmd)
					for emoji in last_channel.server.emojis:
						cmd = cmd.replace(':' + emoji.name + ':', str(emoji))
					await client.send_message(last_channel, cmd)
					print(message.author.name, "sent", cmd)
			else:
				await client.send_message(message.channel,
					"No channel specified. Use `#<channel> [message]`")
		else:
			await client.send_message(message.channel,
				"You don't have permission to use this command.")
		return

	if not COMMAND_FILTER(message): return

	message_interim += 1
	if len(message.content) > 0 and message.content[0] == '!':
		should_delete = False

		if len(message.content) >= 2 and message.content[1] == '~':
			args = message.content[2:].split()
			should_delete = True
		else:
			args = message.content[1:].split()

		for i in range(len(args)):
			args[i] = purify(args[i])

		command = await get_command(args[0])

		if command:
			message_interim -= 1
			if message_interim:
				log("{} non-command messages".format(message_interim))
			message_interim = 0

			log("Command {} executed by {}, args {}".format(args[0], (message.author.nick or message.author.name).encode("utf8"), str(args[1:])))
			await command.function(message, args)
		#else:
			#await client.send_message(message.channel, "{} is an invalid command. Use \"!help\" for help.".format(args[0]))

		if should_delete: await client.delete_message(message)
	elif message.author.id == conf["Users"]["charlie"] and random.random() < 0.0005:
		await client.send_message(message.channel, "Charlie smells")

# Begin functions

async def help(message, args):
	if len(commands) == 0:
		await client.send_message("_No commands have been registered._")
	else:
		if len(args) >= 2 and args[1] in commands:
			output = await commands[args[1]].get_help()
		else:
			output = ""
			for command in sorted(commands):
				output += await commands[command].get_help() + '\n'
			output = output[:-1]

		await client.send_message(message.channel, output)
Command("help", "Lists commands and how they work", help, "!help [commandname]").register()

notes = {}
async def note(message, args):
	if len(args) >= 2:
		if args[1] == "add" and len(args) >= 4:
			notes[args[2]] = ' '.join(args[3:])
			await client.send_message(message.channel, "Note **{}** added.".format(args[2]))
		elif args[1] == "remove":
			del notes[' '.join(args[2:])]
			await client.send_message(message.channel, "Note **{}** removed.".format(args[2]))
		elif args[1] == "list":
			await client.send_message(message.channel, "Notes: _{}_".format(", ".join(notes)))
		else:
			name = ' '.join(args[1:])
			if name in notes:
				await client.send_message(message.channel, notes[name])
			else:
				await client.send_message(message.channel, "No note **{}** exists.\nUse !help note for details".format(name))
Command("note", "Allows you to make notes and recall them at will.", note, "!note <name>, !note add <name> [content], !note remove <name>, !note list").register()

async def alias(message, args):
	if len(args) >= 3 and args[1] in commands:
		await commands[args[1]].add_alias(args[2])
		await client.send_message(message.channel, "Alias **{}** for command **{}** created.".format(args[2], commands[args[1]].name))
Command("alias", "Adds aliases for commands", alias, "!alias <commandname> <alias>").register()

async def jacksmel(message, args):
	await client.send_message(message.channel, "**{} SMELLS!!!**".format((message.author.nick or message.author.name).upper()))
Command("s", "smel", jacksmel).register()

capper = re.compile(" [a-z]")
async def star(message, args):
	await client.send_message(message.channel, re.sub(capper, lambda x:x.group(0).upper(), " " + "".join(random.choice("bcdfghjklmnpqrstvwxyz'''''' ") for i in range(random.randint(10, 30))))[1:])
Command("swng", "Star Wars Name Generator", star).register()

balls = [
	"It is certain", "It is decidedly so",
	"Without a doubt", "Yes, definitely",
	"You may rely on it", "As I see it, yes",
	"Most likely", "Outlook good",
	"Yes", "Signs point to yes",
	"Reply hazy try again", "Ask again later",
	"Better not tell you now", "Cannot predict now",
	"Concentrate and ask again", "Don't count on it",
	"My reply is no", "My sources say no",
	"Outlook not so good", "Very doubtful"
]
async def eightball(message, args):
	if len(args) >= 2:
		await client.send_message(message.channel, "{} :8ball: `{}`".format(message.author.mention, random.choice(balls)))
Command("8ball", "Gives a magic 8-ball answer", eightball, "!8ball <question>").register()

async def meme(message, args):
	await client.send_file(message.channel, "mems/" + random.choice(os.listdir("mems")))
Command("meme", "Sends a random mem", meme).register()

NORMAL = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
translations = {
	"tiny": "ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏᶫᵐᶰᵒᵖᑫʳˢᵗᵘᵛʷˣʸᶻᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᑫᴿˢᵀᵁᵛᵂˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹",
	"full": "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ0123456789",
	"j":    'j'*len(NORMAL)
}

async def translate(message, args):
	if len(args) >= 3:
		raw = ' '.join(args[2:])
		if args[1] in translations:
			new = translations[args[1]]
			await client.send_message(message.channel, ''.join(new[NORMAL.index(a)] if a in NORMAL else a for a in raw))
Command("t", "Translates a message into different styles", translate, "!tiny <{}> <content>".format("|".join(translations))).register()

# End functions

if __name__ == "__main__":
	client.run(conf["Tokens"]["sam_bot"])

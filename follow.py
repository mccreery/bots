#!/usr/bin/env python3
import discord, sys, wrapper
from wrapper import bot

follower = wrapper.secret("Users", sys.argv[0])
target = wrapper.secret("Users", sys.argv[1])

@bot.listen()
async def on_voice_state_update(member, before, after):
	if member.id == target:
		f = await member.guild.get_member(follower)
		await f.move_to(after.channel)

if __name__ == "__main__":
	wrapper.run()

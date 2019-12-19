#!/usr/bin/env python3
import wrapper
from wrapper import bot
from discord.ext.commands import UserConverter

@bot.command()
async def ship(ctx, first: UserConverter, second: UserConverter):
	first = map(ord, first.name)
	second = map(ord, second.name)

	rate = sum(a*5 | b*3 for (a, b) in zip(first, second))
	rate %= 11

	await ctx.message.channel.send(
		f"{ctx.message.author.mention}, I rate this {rate}/10")

if __name__ == "__main__":
	wrapper.run()

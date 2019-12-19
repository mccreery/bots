#!/usr/bin/env python3
import aiohttp, asyncio, discord, wrapper
from wrapper import bot, session

@bot.command(aliases=("sp",))
async def strawpoll(ctx, title, *options):
    async with session.post("https://www.strawpoll.me/api/v2/polls",
            json={"title": title, "options": options}) as response:
        json = await response.json()

    await ctx.message.channel.send(ctx.message.author.mention +
        ", your poll is https://www.strawpoll.me/" + str(json["id"]))

if __name__ == "__main__":
    wrapper.run()

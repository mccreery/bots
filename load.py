#!/usr/bin/env python3
import asyncio, discord, itertools, wrapper

@discord.ext.commands.is_owner()
@wrapper.bot.command()
async def load(ctx):
    chars ="◜◝◞◟"
    message = await ctx.message.channel.send(chars[-1])

    while True:
        for c in chars:
            await asyncio.sleep(0.5)
            await message.edit(content=c)

if __name__ == "__main__":
    wrapper.run()

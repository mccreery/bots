#!/usr/bin/env python3
import discord, os, wrapper, mimetypes
from wrapper import bot, session
from discord.ext.commands import EmojiConverter

@bot.group(invoke_without_command=True)
async def emoji(ctx, emoji: EmojiConverter):
    desc = f"**Name:** {emoji.name}\n**ID**: {emoji.id}\n**URL**: {emoji.url}"

    embed = discord.Embed(title=str(emoji), url=str(emoji.url),
        image=emoji.url, description=desc)
    await ctx.message.channel.send(embed=embed)

@discord.ext.commands.is_owner()
@emoji.command()
async def save(ctx, *emojis: EmojiConverter):
    guild = ctx.message.guild
    if not emojis:
        emojis = guild.emojis

    progress_prefix = f"Saving {len(emojis)} emojis..."
    progress = await ctx.message.channel.send(progress_prefix)

    for emoji in emojis:
        head = await session.head(str(emoji.url))
        ext = mimetypes.guess_extension(head.content_type)

        filename = f"{guild.name}/{emoji.name}{ext}"
        await progress.edit(content=progress_prefix + " " + filename)
        await emoji.url.save(filename)

    await progress.edit(content=progress_prefix + " Done")

if __name__ == "__main__":
    wrapper.run()

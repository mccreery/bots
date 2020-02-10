#!/usr/bin/env python3
import discord, io, math, wrapper, scipy.ndimage, urllib, os
from wrapper import bot
from PIL import Image, ImageFont, ImageDraw, ImageColor, ImageOps
import numpy as np

async def get_image_url(ctx):
    async for message in ctx.history():
        for attachment in reversed(message.attachments):
            if attachment.width:
                return attachment.url
        for embed in reversed(message.embeds):
            if embed.image:
                return embed.image.url

def domain_circle(radius):
    shape = radius * 2 + 1
    shape = shape, shape

    image = Image.new("1", shape)
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0) + shape, "white")

    return np.array(image)

def border_image(image, radius, fill="black"):
    # Alpha composite the constant fill color beneath the image
    border_image = Image.new(image.mode, image.size, fill)
    border_image.alpha_composite(image)

    # Alpha channel is put through a max filter with a circular domain
    a = image.getchannel("A")
    a_mode = a.mode
    a = np.array(a)
    a = scipy.ndimage.maximum_filter(a, footprint=domain_circle(radius))
    a = Image.fromarray(a, a_mode)

    border_image.putalpha(a)
    return border_image

def text_image(text, **kwargs):
    size_kwargs = {k: v for k, v in kwargs.items() if k in [
        "font", "spacing", "direction",
        "features", "language", "stroke_width"]}

    # Get size of text
    image = Image.new("RGBA", (1,1))
    draw = ImageDraw.Draw(image)
    size = draw.textsize(text, **size_kwargs)

    # Draw text on correctly sized image
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, **kwargs)
    return image

def match_height(font, height, text="X", *args, **kwargs):
    i = 1
    while True:
        variant = font.font_variant(size=i)
        if variant.getsize(text, *args, **kwargs)[1] >= height:
            return variant
        i += 1

def meme_text_image(text, font, radius):
    image = text_image(text, font=font, fill="white", align="center")
    image = ImageOps.expand(image, radius)
    image = border_image(image, radius=radius)

    return image

def meme_image(image, top_text, bottom_text):
    in_format = image.format

    # Text positioning and size parameters
    font_height = image.height / 10
    radius = int(font_height // 15)
    padding = image.height // 30

    font = ImageFont.truetype("impact.ttf")
    font = match_height(font, font_height)

    image = image.convert("RGBA")
    overlay = Image.new("RGBA", image.size)

    # Top text
    top_text_image = meme_text_image(top_text, font, radius)
    top_text_pos = ((image.width - top_text_image.width) // 2, padding)
    overlay.paste(top_text_image, top_text_pos)

    # Bottom text
    bottom_text_image = meme_text_image(bottom_text, font, radius)
    bottom_text_pos = ((image.width - bottom_text_image.width) // 2, image.height - padding - bottom_text_image.height)
    overlay.paste(bottom_text_image, bottom_text_pos)

    image = Image.alpha_composite(image, overlay)
    image.format = in_format
    return image

def limit_size(image, size=1024):
    ratio = image.width / image.height

    if image.width > size and image.width >= image.height:
        image = image.resize((size, round(size / ratio)))
    elif image.height > size and image.height >= image.width:
        image = image.resize((round(size * ratio), size))
    return image

@bot.command()
@wrapper.typing
async def meme(ctx, top_text, *bottom_text):
    top_text = top_text.upper()
    bottom_text = " ".join(bottom_text).upper()

    # Get last image in chat
    url = await get_image_url(ctx)

    if not url:
        await ctx.message.channel.send("Missing image")
        return

    filename = os.path.basename(urllib.parse.urlparse(url).path)
    fp = await wrapper.get(url)
    image = Image.open(fp)

    image = limit_size(image)
    image = meme_image(image, top_text, bottom_text)

    fp.seek(0)
    image.save(fp, image.format)
    fp.seek(0)
    await ctx.message.channel.send(file=discord.File(fp, filename=filename))
    fp.close()

if __name__ == "__main__":
    wrapper.run()

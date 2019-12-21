#!/usr/bin/env python3
import discord, io, math, wrapper, scipy.signal, urllib, os
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

def border(image, radius, fill="black"):
    a = image.getchannel("A")
    a = np.array(a)

    kernel_size = math.ceil(radius) * 2 + 1
    kernel_center = kernel_size // 2

    # Convolve alpha with outline kernel
    def kernel_func(x, y):
        d = np.sqrt((x - kernel_center) ** 2 + (y - kernel_center) ** 2)
        return np.clip(radius + 1 - d, 0, 1)

    kernel = np.fromfunction(kernel_func, (kernel_size, kernel_size))
    a = scipy.signal.convolve2d(a, kernel, mode="same")
    a = np.clip(a, 0, 255)
    a = a[..., np.newaxis]

    # Use fill as RGB channels
    fill = np.asarray(ImageColor.getrgb(fill))
    rgb = np.broadcast_to(fill, a.shape[:2] + fill.shape)

    rgba = np.concatenate((rgb, a), axis=2)
    rgba = np.uint8(rgba)
    border = Image.fromarray(rgba, "RGBA")
    return border

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

@bot.command()
@wrapper.typing
async def meme(ctx, top_text, *bottom_text):
    bottom_text = " ".join(bottom_text)
    top_text = top_text.upper()
    bottom_text = bottom_text.upper()

    # Get last image in chat
    url = await get_image_url(ctx)
    filename = os.path.basename(urllib.parse.urlparse(url).path)
    fp = await wrapper.get(url)
    image = Image.open(fp)

    # Text positioning and size parameters
    font_height = image.height / 10
    radius = font_height / 15
    padding = image.height // 30

    font = ImageFont.truetype("impact.ttf")
    variant = match_height(font, font_height)

    # Top text
    top_image = text_image(top_text, font=variant, fill="white", align="center")
    top_image = ImageOps.expand(top_image, math.ceil(radius))
    top_border = border(top_image, radius=radius)

    top_pos = ((image.width - top_image.width) // 2, padding)
    image.paste(top_border, top_pos, top_border)
    image.paste(top_image, top_pos, top_image)

    # Bottom text
    bottom_image = text_image(bottom_text, font=variant, fill="white", align="center")
    bottom_image = ImageOps.expand(bottom_image, math.ceil(radius))
    bottom_border = border(bottom_image, radius=radius)

    bottom_pos = ((image.width - bottom_image.width) // 2, image.height - padding - bottom_image.height)
    image.paste(bottom_border, bottom_pos, bottom_border)
    image.paste(bottom_image, bottom_pos, bottom_image)

    fp.seek(0)
    image.save(fp, image.format)
    fp.seek(0)
    await ctx.message.channel.send(file=discord.File(fp, filename=filename))
    fp.close()

if __name__ == "__main__":
    wrapper.run()

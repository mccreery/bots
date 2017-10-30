#!/usr/bin/env python3

from PIL import Image, ImageFont, ImageDraw, ImageColor
import discord, io, re, shlex, config
client = discord.Client()

IMPACT = ImageFont.truetype(r"C:\Windows\Fonts\impact.ttf", 30)
ARIAL  = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 10)
TRANSPARENT = (0, 0, 0, 0)
TILE = 64

def caption(draw, xy, text, **options):
	options["fill"] = "white"
	size = options["font"].getsize(text)
	padding = int((size[1] / 5) + 0.5)

	bounds = (
		xy[0] - padding, xy[1] - padding,
		xy[0] + size[0] + padding, xy[1] + size[1] + padding
	)
	draw.rectangle(bounds, fill=(0, 0, 0, 95))
	draw.text(xy, text, **options)

async def send_image(destination, image, *, filename=None, content=None, tts=False):
	file = io.BytesIO()
	image.save(file, "png")
	file.seek(0)
	await client.send_file(destination, file, filename=filename)
	file.close()

@client.event
async def on_ready():
	global mention_bang
	mention_bang = client.user.mention[:2] + '!' + client.user.mention[2:]

def draw_text(draw, text, x, y):
	draw.text((x,   y),   text, font=IMPACT, fill="black")
	draw.text((x+2, y),   text, font=IMPACT, fill="black")
	draw.text((x,   y+2), text, font=IMPACT, fill="black")
	draw.text((x+2, y+2), text, font=IMPACT, fill="black")
	draw.text((x+1, y+1), text, font=IMPACT, fill="white")

@client.event
async def on_message(message):
	if client.user.mentioned_in(message):
		if message.content.startswith(client.user.mention):
			command = message.content[len(client.user.mention):].strip()
		elif message.content.startswith(mention_bang):
			command = message.content[len(mention_bang):].strip()
		else: return

		if not command: return
		command = shlex.split(command)
		test = command[0].upper()

		print(message.author, command)

		if test == "MEME":
			await client.delete_message(message)
			text = ' '.join(command[1:]).upper().splitlines()

			line_height = IMPACT.getsize(text[0])[1]
			height = len(text) * line_height
			width = 0
			for line in text:
				line_width = IMPACT.getsize(line)[0]
				if line_width > width:
					width = line_width

			y = 2
			size = (width + 4, height + 4)
			image = Image.new("RGBA", size, TRANSPARENT)
			draw = ImageDraw.Draw(image)

			for line in text:
				draw_text(draw, line, 2, y)
				y += line_height

			await send_image(message.channel, image, filename=text[0] + ".png")
		elif test == "GRADIENT":
			print(command)
			if len(command) >= 4:
				try:
					start = ImageColor.getrgb(command[1])
					end = ImageColor.getrgb(command[2])
					stops = int(command[3])

					inc = 1 / (stops - 1) if stops != 1 else 0
					fac = 0

					colors = []
					for i in range(stops):
						print(len(start))
						stop = tuple(
							int(round(end[i] * fac + start[i] * (1 - fac))) \
							for i in range(len(start))
						)
						print(fac)
						colors.append(stop)

						fac += inc

					image = Image.new("RGB", (TILE * stops, TILE), TRANSPARENT)
					draw = ImageDraw.Draw(image, "RGBA")

					x = 0
					for color in colors:
						print(color)
						draw.rectangle((x, 0, x + TILE, TILE), fill=color)
						text = "#{0:02x}{1:02x}{2:02x}".format(*color)
						text_size = ARIAL.getsize(text)
						caption(draw, (x + (TILE - text_size[0]) / 2, (TILE - text_size[1]) / 2), text, font=ARIAL)
						x += TILE

					await send_image(message.channel, image, filename="gradient.png")
				except ValueError:
					await client.send_message(message.channel, "Invalid parameters.")

client.run(config.config()["Tokens"]["user"], bot=False)

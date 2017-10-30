#!/usr/bin/env python3

import discord, asyncio, config
client = discord.Client()
conf = config.config()

REACT_PREFIX = "samreact"

@asyncio.coroutine
def imgur_request(http, method, url, *, bucket=None, **kwargs):
	lock = http._locks.get(bucket)
	if lock is None:
		lock = asyncio.Lock(loop=http.loop)
		if bucket is not None:
			http._locks[bucket] = lock

	# header creation
	headers = {
		"User-Agent": http.user_agent,
		"Authorization": "Client-ID " + conf["Imgur"]["client"]
	}

	# some checking if it's a JSON request
	if 'json' in kwargs:
		headers['Content-Type'] = 'application/json'
		kwargs['data'] = utils.to_json(kwargs.pop('json'))

	if not "headers" in kwargs:
		kwargs["headers"] = {}
	kwargs['headers'].update(headers)

	with (yield from lock):
		for tries in range(5):
			r = yield from http.session.request(method, url, **kwargs)
			discord.http.log.debug(http.REQUEST_LOG.format(method=method, url=url, status=r.status, json=kwargs.get('data')))
			try:
				# even errors have text involved in them so this is safe to call
				data = (yield from discord.http.json_or_text(r))["data"]

				# the request was successful so just return the text/json
				if 300 > r.status >= 200:
					discord.http.log.debug(http.SUCCESS_LOG.format(method=method, url=url, text=data))
					return data

				# we are being rate limited
				if r.status == 429:
					fmt = 'We are being rate limited. Retrying in {:.2} seconds. Handled under the bucket "{}"'

					# sleep a bit
					retry_after = data['retry_after'] / 1000.0
					discord.http.log.info(fmt.format(retry_after, bucket))
					yield from asyncio.sleep(retry_after)
					continue

				# we've received a 502, unconditional retry
				if r.status == 502 and tries <= 5:
					yield from asyncio.sleep(1 + tries * 2)
					continue

				# the usual error cases
				if r.status == 403:
					raise Forbidden(r, data)
				elif r.status == 404:
					raise NotFound(r, data)
				else:
					raise HTTPException(r, data)
			finally:
				# clean-up just in case
				yield from r.release()

@client.event
async def on_message(message):
	if message.author.id == conf["Users"]["me"] and message.content.startswith(REACT_PREFIX):
		needle = message.content[len(REACT_PREFIX) + 1:]
		resp = await imgur_request(client.http, "GET", "https://api.imgur.com/3/album/" + conf["Imgur"]["album"])
		for image in resp["images"]:
			if image["title"] == needle:
				data = {
					"embeds": [{
						"title": image["title"],
						"image": {"url": image["link"]},
						"description": image["description"]
					}]
				}
				await client.http.post(conf["Webhook"]["moderator"], json=data)
				await client.delete_message(message)
				return
		print(needle, "Not found")

client.run(conf["Token"]["sam"])

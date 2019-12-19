import aiohttp, configparser, os
from discord.ext.commands import Bot

config = configparser.ConfigParser()
config.read(os.getenv("BOT_CONFIG", "config.ini"))

bot = Bot(os.getenv("BOT_PREFIX", "!"))
session = aiohttp.ClientSession(loop=bot.loop)

def secret(section, key_or_value):
    return config.get(section, key_or_value, fallback=key_or_value)

def run(*args, **kwargs):
    # 2 possible sources for token
    if args:
        token, *args = args
    if "BOT_TOKEN" in os.environ:
        token = os.environ["BOT_TOKEN"]

    # Only works if either of the conditions passed
    try:
        # Translate token if possible
        token = secret("Tokens", token)
        args = token, *args
    except (NameError, AttributeError):
        # Either no token or token is some weird value
        pass

    # Signature matches, missing token will raise in the same place as normal
    bot.run(*args, **kwargs)

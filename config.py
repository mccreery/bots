import configparser, os

config = configparser.ConfigParser()
config.read(os.getenv("BOT_CONFIG", "config.ini"))

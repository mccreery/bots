import configparser

def config(filename="config.ini"):
	config = configparser.ConfigParser()
	config.read(filename)
	return config

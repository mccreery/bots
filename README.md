# Discord Bots

Lots of Python bots for [Discord](https://discordapp.com/)

## [`wrapper.py`](wrapper.py)
The wrapper code provides some common functionality for the most common type of
bot which runs commands. It uses the following environment variables:

- `BOT_CONFIG` (default `"config.ini"`): The config file for looking up secrets
- `BOT_PREFIX` (default `"!"`): The command prefix
- `BOT_TOKEN`: Overrides the first argument to `wrapper.run`

`wrapper.run` finds the appropriate token and runs the bot. Before running, it
will try to use the token as a key in the config file section `Tokens`. For
example, if the config file looks like:
```ini
[Tokens]
    my_bot=XXXXXXXXXXXXXXXXXXXXXXXX.XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXX
```
Then the following are all equivalent:
```bash
BOT_TOKEN=XX...X python -c 'import wrapper; wrapper.run()' # Token in env
BOT_TOKEN=my_bot python -c 'import wrapper; wrapper.run()' # Key in env
python -c 'import wrapper; wrapper.run("XX...X")'          # Token in run()
python -c 'import wrapper; wrapper.run("my_bot")'          # Key in run()
```
You can verify this by seeing your bot come online.

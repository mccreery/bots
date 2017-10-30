#!/usr/bin/env python3

import ctypes, discord, asyncio, re, msvcrt, config
from ctypes import wintypes
from concurrent.futures import ProcessPoolExecutor

EVENT_OBJECT_NAMECHANGE = 0x800C
WINEVENT_OUTOFCONTEXT   = 0x0000
PM_REMOVE               = 0x0001

now_playing = None

client = discord.Client()

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32
ole32.CoInitialize(0)

WinEventProcType = ctypes.WINFUNCTYPE(
	None,
	ctypes.wintypes.HANDLE,
	ctypes.wintypes.DWORD,
	ctypes.wintypes.HWND,
	ctypes.wintypes.LONG,
	ctypes.wintypes.LONG,
	ctypes.wintypes.DWORD,
	ctypes.wintypes.DWORD
)

spotify_hwnd = user32.FindWindowA("SpotifyMainWindow".encode("ascii"), 0)
spotify_id = wintypes.DWORD()
user32.GetWindowThreadProcessId(spotify_hwnd, ctypes.byref(spotify_id))
print(spotify_hwnd, spotify_id)

def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
	if hwnd == spotify_hwnd:
		length = user32.GetWindowTextLengthA(hwnd)
		buff = ctypes.create_string_buffer(length + 1)
		user32.GetWindowTextA(hwnd, buff, length + 1)

		global now_playing
		now_playing = buff.value.decode("ascii")
		if not now_playing in ("Find Out More", "Spotify", "Listen Now"):
			print(now_playing)
			asyncio.ensure_future(client.change_presence(game=discord.Game(name=now_playing)))

WinEventProc = WinEventProcType(callback)
user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
hook = user32.SetWinEventHook(
	EVENT_OBJECT_NAMECHANGE,
	EVENT_OBJECT_NAMECHANGE,
	0,
	WinEventProc,
	spotify_id,
	0,
	WINEVENT_OUTOFCONTEXT
)
if hook == 0:
	print("SetWinEventHook failed")
	sys.exit(1)

async def win_loop():
	msg = ctypes.wintypes.MSG()
	while True:
		if user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, PM_REMOVE) != 0:
			user32.TranslateMessageW(msg)
			user32.DispatchMessageW(msg)
		await manual()
		await asyncio.sleep(0)

current_manual = ""

async def manual():
	global current_manual, now_playing

	if msvcrt.kbhit():
		char = msvcrt.getche()
		if char == b"\r": # Enter
			print("\nCustom playing changed to \"" + current_manual + "\"")
			if current_manual:
				now_playing = current_manual
				await client.change_presence(game=discord.Game(name=now_playing))
			current_manual = ""
		else:
			current_manual += char.decode("ascii")

@client.event
async def on_ready():
	print("ready")
	await win_loop()

cmd = re.compile(r"^what'?s playin['g]?,? sam(my)?/?|!now$", re.I)
@client.event
async def on_message(message):
	if not cmd.match(message.content) is None:
		if now_playing and not " - " in now_playing:
			reply = ":musical_note: Currently playing: **{}**".format(now_playing)
		else:
			if now_playing is None:
				artist = "Nobody"
				track = "Nothing"
			else:
				artist = now_playing[:now_playing.index(" - ")]
				track = now_playing[len(artist)+3:]

			reply = ":musical_note: Currently playing: :cd: **{}** by :microphone: **{}**".format(track, artist)
		await client.send_message(message.channel, reply)

client.run(config.config()["Tokens"]["user"], bot=False)

user32.UnhookWinEvent(hook)
ole32.CoUninitialize()

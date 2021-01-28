import asyncio
import time
from nio import AsyncClient, MatrixRoom, RoomMessageText

URI = "XXXX"
USERNAME = "@ts_bot:XXX"
PW = "XXXX"
ROOM = "!XXXXXX:XXXXX"

class MatrixClient:
	def __init__(self, bot_funcs):
		self.bot_funcs = bot_funcs
		self.client = AsyncClient(URI, USERNAME)
		self.last_sent = 0
		print("init finished")

	async def message_callback(self, room: MatrixRoom, event: RoomMessageText):
		for f in self.bot_funcs:
			if event.body.startswith(f["trigger"]):
				ts = time.time()
				if ts - self.last_sent < 2:
					continue
				self.last_sent = time.time()
				res = f["ret_func"](event.body, event.sender)
				if res is None:
					continue
				await self.client.room_send(
					room_id=ROOM,
					message_type="m.room.message",
					content = {
						"msgtype": "m.text",
						"body": res
					}
				)

	async def exec_client(self):
		self.client.add_event_callback(self.message_callback, RoomMessageText)
		print(await self.client.login(PW))
		await self.client.sync_forever(timeout=30000) # milliseconds

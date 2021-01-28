import asyncio
import systemd.daemon
from tsd import TsData
from mc import MatrixClient
from pprint import pprint

loop = asyncio.get_event_loop()

ts_data = TsData()
loop.create_task(ts_data.keep_alive())
loop.add_reader(ts_data.fileno(), ts_data.event_handler)

def get_ts_channel_tree(msg, sender):
	return ts_data.get_channel_tree()
def get_last_msgs(msg, sender):
	mp = msg.split(' ')
	n = 20
	if len(mp) > 1:
		n = int(mp[1])
	return ts_data.get_links(n)
def poke_user(msg, sender):
	mp = msg.split('\"')
	if len(mp) != 5:
		return None
	return ts_data.poke_user(mp[1], mp[3])
def post_msg(msg, sender):
	mp = msg.split('\"')
	if len(mp) < 2:
		return None
	return ts_data.post_channel_msg(sender, mp[1])

matrix_bot_funcs = [
	{"trigger": "!status", "ret_func": get_ts_channel_tree},
	{"trigger": "!last", "ret_func": get_last_msgs},
	{"trigger": "!poke", "ret_func": poke_user},
	{"trigger": "!post", "ret_func": post_msg},
]

matrix_client = MatrixClient(matrix_bot_funcs)

systemd.daemon.notify('READY=1')
loop.run_until_complete(matrix_client.exec_client())

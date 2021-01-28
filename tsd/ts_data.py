import ts3
import asyncio
from .channel_tree import ChannelTreeNode
from .link_list import LinkList
from pprint import pprint
import subprocess


URI = "ssh://bot:XXXXXX@localhost:10022"
SID = 1

OBSERVER_CHANNEL = "81" # floris reich

class TsData:
	def __init__(self):
		self.link_list = LinkList()

		self.conn = ts3.query.TS3ServerConnection(URI)
		self.conn.exec_("use", sid=1)

		clid = self.conn.query("whoami").first()["client_id"]
		self.conn.exec_("clientmove", clid=clid, cid=OBSERVER_CHANNEL)
		self.conn.exec_("servernotifyregister", event="textchannel")


	async def keep_alive(self):
		while True:
			self.conn.send_keepalive()
			await asyncio.sleep(4*60)

	def fileno(self):
		return self.conn.fileno()

	def get_channel_tree(self):
		tree = ChannelTreeNode.build_tree(self.conn, SID)
		return tree.to_string()

	def update_ytdl(self):
		output = subprocess.check_output("sudo -u sinusbot /opt/sinusbot/youtube-dl -U --restrict-filenames", shell=True)
		return output.decode("utf-8")

	def event_handler(self):
		try:
			ev = self.conn.wait_for_event(timeout=2)
		except ts3.query.TS3TimeoutError:
			print("timeout ev")
			pass
		else:
			if ev.event == "notifytextmessage":
				if ev.parsed[0]["msg"].startswith("!update"):
					res = self.update_ytdl()
					self.post_channel_msg("ytdl", res)
					return
				sender = ev.parsed[0]["invokername"]
				msg = ev.parsed[0]["msg"].replace('[URL]','').replace('[/URL]', '')
				self.link_list.check_and_add(sender, msg)

	def poke_user(self, nick, msg):
		clients = self.conn.query("clientfind", pattern=nick).all()
		clients = [client["clid"] for client in clients]
		for clid in clients:
			print("poking " + clid + " msg " + msg)
			self.conn.exec_("clientpoke", msg=msg, clid=clid)


	def post_channel_msg(self, nick, msg):
		self.link_list.check_and_add(nick, msg)
		self.conn.exec_("sendtextmessage", msg="[" + nick + "] " + msg, targetmode="2", target=OBSERVER_CHANNEL)
		return None

	def get_links(self, last=20):
		return self.link_list.get_links(last)

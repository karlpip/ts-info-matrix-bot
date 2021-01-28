import time
from datetime import datetime

target_marker = [
	"youtube",
	"reddit",
	"redd.it",
	"imgur",
	"giphy",
]

LIST_FILE = "links.txt"

class LinkList:
	def __init__(self):
		self.links = []
		self.saved = 0
		self.read_in()

	def read_in(self):
		f = open(LIST_FILE, 'r')
		lines = f.readlines()

		for l in lines:
			if len(l.strip()) < 1:
				continue
			parts = l.split(' ')
			if len(parts) >= 3:
				self._add(parts[1], parts[2], float(parts[0]))

		print("read in " + str(len(lines)) + " links")


	def backup(self):
		f = open(LIST_FILE, "a")
		last3 = self.links[-3:]
		for l in last3:
			f.write(str(l["ts"]) + " " + l["sender"] + " " + l["link"] + "\n")
		f.close()

	def _add(self, sender, link, ts=None):
		for l in self.links:
			if l["link"] == link:
				return
		if ts is None:
			ts = time.time()
			self.saved = self.saved + 1
		self.links.append({"sender": sender, "link": link, "ts": int(ts)})
		if self.saved == 3:
			self.backup()
			self.saved = 0


	def check_and_add(self, sender, msg):
		if sender.startswith("matrix"):
			return
		if sender.startswith("ytdl"):
			return
		if msg.startswith("!"):
			return
		for t in target_marker:
			if t in msg:
				self._add(sender.replace(' ', ''), msg.strip().replace(' ', ''))
				return

	def _link_to_string(self, link):
		d = datetime.fromtimestamp(link["ts"])
		return str(d) + " | " + link["sender"] + ": " + link["link"]

	def get_links(self, last=20):
		if len(self.links) == 0:
			return "no links yet"
		if len(self.links) <= last:
			n = len(self.links)
		else:
			n = last

		res = "last " + str(n) + " links:\n\n"

		ls = self.links[-n:]
		ls.reverse()
		for l in ls:
			res = res + self._link_to_string(l) + "\n"

		return res

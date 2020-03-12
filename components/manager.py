from typing import List
from shared.mail_server import MailServer
from shared.proxy import Proxy
from shared.sender import Sender


class Manager:

	proxies: List[Proxy]
	servers: List[MailServer]
	senders: List[Sender]
	p_index: int = 0
	s_index: int = 0
	s2_index: int = 0

	def __init__(self, proxies: List[Proxy], servers: List[MailServer], senders: List[Sender]):
		self.proxies = proxies
		self.servers = servers
		self.senders = senders

	def proxy(self):
		proxy = self.proxies[self.p_index]
		if self.p_index + 1 == len(self.proxies):
			self.p_index = 0
		else:
			self.p_index += 1

		return proxy

	def sender(self):
		sender = self.senders[self.s2_index]
		if self.s2_index + 1 == len(self.senders):
			self.s2_index = 0
		else:
			self.s2_index += 1

		return sender

	def server(self, calls: int = 0):

		assert calls != len(self.servers), "[!] No working servers"

		server = self.servers[self.s_index]
		if self.s_index + 1 == len(self.servers):
			self.s_index = 0
		else:
			self.s_index += 1

		if not server.is_ok():
			return self.server(calls+1)

		server.increment_usage()
		return server
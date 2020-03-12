from typing import List

from shared.config import Config
from shared.mail_server import MailServer
from shared.message import Message
from shared.proxy import Proxy
from shared.recipient import Recipient
from shared.sender import Sender
import yaml

# Folders
BUCKET_FOLDER = "../bucket"
ATTACHMENTS_FOLDER = "../bucket/attachments"

# Mail server file config
MAIL_SERVERS_FILE_NAME = "mail_servers.txt"
MAIL_SERVERS_HOST_INDEX = 0
MAIL_SERVERS_USERNAME_INDEX = 1
MAIL_SERVERS_PASSWORD_INDEX = 2
MAIL_SERVERS_PORT_INDEX = 3
MAIL_SERVERS_LIMIT_INDEX = 4

# Senders file config
SENDERS_FILE_NAME = "senders.txt"
SENDER_MAIL_INDEX = 0
SENDER_NAME_INDEX = 1

# Proxy file config
PROXIES_FILE_NAME = "proxies.txt"
PROXIES_GATEWAY_INDEX = 0
PROXIES_PORT_INDEX = 1

# Recipients file config
RECIPIENT_FILE_NAME = "recipients.txt"
RECIPIENT_EMAIL_INDEX = 0

# Other file names
CONFIGS_FILE_NAME = "configs.yml"
HTML_FILE_NAME = "mail.html"

# Errors
INVALID_LINE = "[!] Invalid line:"


class Reader:
	mail_servers: List[MailServer] = []
	senders: List[Sender] = []
	proxies: List[Proxy] = []
	recipients: List[Recipient] = []
	config = Config()
	message = Message(ATTACHMENTS_FOLDER)

	@staticmethod
	def __create_mail_server(line: str):
		# Split and validate
		parts = line.split(":")
		parts_len = len(parts)
		assert parts_len == 4 or parts_len == 5, "%s: %s" % (INVALID_LINE, line)

		# Create new server object
		server = MailServer()
		server.host = parts[MAIL_SERVERS_HOST_INDEX]
		server.username = parts[MAIL_SERVERS_USERNAME_INDEX]
		server.password = parts[MAIL_SERVERS_PASSWORD_INDEX]
		server.port = int(parts[MAIL_SERVERS_PORT_INDEX])

		if parts_len == 5:
			server.limit = int(parts[MAIL_SERVERS_LIMIT_INDEX])

		return server

	@staticmethod
	def __create_sender(line: str):
		# Split and validate
		parts = line.split(":")
		parts_len = len(parts)
		assert parts_len == 2, "%s: %s" % (INVALID_LINE, line)

		# Create new sender object
		sender = Sender()
		sender.email = parts[SENDER_MAIL_INDEX]
		sender.name = parts[SENDER_NAME_INDEX]

		return sender

	@staticmethod
	def __create_proxy(line: str):
		# Split and validate
		parts = line.split(":")
		parts_len = len(parts)
		assert parts_len == 2, "%s: %s" % (INVALID_LINE, line)

		# Create new sender object
		proxy = Proxy()
		proxy.gateway = parts[PROXIES_GATEWAY_INDEX]
		proxy.port = int(parts[PROXIES_PORT_INDEX])

		return proxy

	@staticmethod
	def __create_recipient(line: str):
		# Split and validate
		parts = line.split(":")
		parts_len = len(parts)
		assert parts_len == 1, "%s: %s" % (INVALID_LINE, line)

		# Create new sender object
		recipient = Recipient()
		recipient.email = parts[RECIPIENT_EMAIL_INDEX]

		return recipient

	@staticmethod
	def __should_ignore(line: str):
		# Ignore comments and empty lines
		return False if line is "\n" or line.startswith("#") else True

	def __init__(self):

		print("[ ] Loading files")

		try:
			print("\t- %s" % MAIL_SERVERS_FILE_NAME)
			for line in open("%s/%s" % (BUCKET_FOLDER, MAIL_SERVERS_FILE_NAME), 'r'):
				if not self.__should_ignore(line):
					continue
				else:
					server = self.__create_mail_server(line.rstrip("\n"))
					self.mail_servers.append(server)

			print("\t- %s" % SENDERS_FILE_NAME)
			for line in open("%s/%s" % (BUCKET_FOLDER, SENDERS_FILE_NAME), 'r'):
				if not self.__should_ignore(line):
					continue
				else:
					sender = self.__create_sender(line.rstrip("\n"))
					self.senders.append(sender)

			print("\t- %s" % PROXIES_FILE_NAME)
			for line in open("%s/%s" % (BUCKET_FOLDER, PROXIES_FILE_NAME), 'r'):
				if not self.__should_ignore(line):
					continue
				else:
					proxy = self.__create_proxy(line.rstrip("\n"))
					self.proxies.append(proxy)

			print("\t- %s" % RECIPIENT_FILE_NAME)
			for line in open("%s/%s" % (BUCKET_FOLDER, RECIPIENT_FILE_NAME), 'r'):
				if not self.__should_ignore(line):
					continue
				else:
					recipient = self.__create_recipient(line.rstrip("\n"))
					self.recipients.append(recipient)

			print("\t- %s" % CONFIGS_FILE_NAME)
			with open("%s/%s" % (BUCKET_FOLDER, CONFIGS_FILE_NAME), 'r') as stream:
				settings = yaml.safe_load(stream)
				self.config.treads = int(settings.get("treads", self.config.treads))
				self.config.mails_per_second = int(settings.get("mails_per_second", self.config.mails_per_second))
				self.message.subject = settings.get("subject", self.message.subject)

			print("\t- %s" % HTML_FILE_NAME)
			with open("%s/%s" % (BUCKET_FOLDER, HTML_FILE_NAME), 'r') as stream:
				self.message.html = stream.read()

		except AssertionError as e:
			print('\n[!] %s ' % e)
			exit(1)

		except Exception as e:
			print("\n[!] %s => %s" % e)
			exit(1)

		print("\n[✓] loaded all files")

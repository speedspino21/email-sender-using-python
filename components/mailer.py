import ssl
import smtplib
import socks
from components.manager import Manager
from shared.mail_server import MailServer
from shared.message import Message
from shared.recipient import Recipient


class Mailer:

	manager: Manager
	message: Message

	def __init__(self, manager: Manager, message: Message):
		self.manager = manager
		self.message = message

	@staticmethod
	def get_connection(proxy, host, port, username, password):

		socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, proxy.gateway, proxy.port)
		socks.wrapmodule(smtplib)

		if port == 465:
			connection = smtplib.SMTP_SSL(host, port, timeout=5)
		else:
			connection = smtplib.SMTP(host, port, timeout=5)

		connection.ehlo()

		if port == 587:
			context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
			connection.starttls(context=context)

		connection.login(username, password)
		return connection

	def check_server(self, server: MailServer):
		proxy = self.manager.proxy()
		try:
			connection = self.get_connection(proxy, server.host, server.port, server.username, server.password)
			connection.close()
			print("\t✓ %s at %s through %s => ok" % (server.username, server.host, proxy.gateway))
			return True
		except smtplib.SMTPConnectError as e:
			print("\t† %s at %s through %s => %s" % (server.username, server.host, proxy.gateway, e))
			return self.check_server(server)
		except smtplib.SMTPAuthenticationError:
			print("\t† %s at %s through %s => invalid credentials" % (server.username, server.host, proxy.gateway))
			return False
		except Exception as e:
			print("\t† %s at %s through %s => %s" % (server.username, server.host, proxy.gateway, e))
			return False

	def send_mail(self, server: MailServer, recipient: Recipient):
		proxy = self.manager.proxy()

		try:
			sender = self.manager.sender()
			mail = self.get_connection(proxy, server.host, server.port, server.username, server.password)
			message = self.message.build(sender, recipient)
			mail.send_message(message, server.username, [recipient.email])
			mail.quit()
			print("\t✓ %s => ok" % recipient.email)
			return True
		except smtplib.SMTPConnectError as e:
			print("\t† %s at %s through %s => %s" % (server.username, server.host, proxy.gateway, e))
			return self.send_mail(server, recipient)
		except smtplib.SMTPSenderRefused:
			print("\t† %s at %s through %s => sender refused" % (server.username, server.host, proxy.gateway))
			return False
		except smtplib.SMTPRecipientsRefused:
			print("\t† %s at %s through %s => recipient refused" % (server.username, server.host, proxy.gateway))
			return False
		except Exception as e:
			print("\t† %s at %s through %s => %s" % (server.username, server.host, proxy.gateway, e))
			return False
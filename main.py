import threading
import time

from components.mailer import Mailer
from components.manager import Manager
from components.reader import Reader
from shared.mail_server import MailServer
from shared.recipient import Recipient

reader = Reader()
manager = Manager(reader.proxies, reader.mail_servers, reader.senders)
mailer = Mailer(manager, reader.message)
limiter = threading.BoundedSemaphore(reader.config.treads)
time_limiter: threading.BoundedSemaphore
mails_per_sec = reader.config.mails_per_second

active = 0
finish = False


def acquire():
	global active
	limiter.acquire()
	if mails_per_sec > 0:
		time_limiter.acquire()
		active += 1


def release():
	global active
	while not finish:
		if active > 0:
			active -= 1
			time_limiter.release()
		time.sleep(1)


def send(recipient: Recipient):
	acquire()
	try:
		server: MailServer = manager.server()
		mailer.send_mail(server, recipient)
	except AssertionError as e:
		print('\n[!] %s ' % e)
		exit(1)
	finally:
		limiter.release()


def check(server: MailServer):
	acquire()
	try:
		if not mailer.check_server(server):
			server.disable()
	finally:
		limiter.release()


def main():
	# Set up time limiter tread
	global time_limiter, finish
	if mails_per_sec > 0:
		time_limiter = threading.BoundedSemaphore(mails_per_sec)
		thread = threading.Thread(target=release, args=[])
		thread.start()

	# Check if server are ok
	print("\n[ ] Scanning servers")
	tasks = []
	for server in manager.servers:
		thread = threading.Thread(target=check, args=[server])
		thread.start()
		tasks.append(thread)

	while len(tasks) > 0:
		tasks.pop().join()

	print("\n[✓] server list scan finished")

	# Send emails
	print("\n[ ] Sending emails")
	for recipient in reader.recipients:
		thread = threading.Thread(target=send, args=[recipient])
		thread.start()
		tasks.append(thread)

	while len(tasks) > 0:
		tasks.pop().join()

	finish = True
	print("\n[✓] mail delivery finished")


main()

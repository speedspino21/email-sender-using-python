import mimetypes
import os
from email.headerregistry import Address
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from bs4 import BeautifulSoup


class Message:
	subject: str = ""
	html: str = ""
	__text: str = None
	__attachments_folder: str

	def __init__(self, attachments_folder: str):
		self.__attachments_folder = attachments_folder

	def get_text(self):
		# get text
		soup = BeautifulSoup(self.html, "html.parser")
		text = soup.get_text()

		# break into lines and remove leading and trailing space on each
		lines = (line.strip() for line in text.splitlines())
		# break multi-headlines into a line each
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		# drop blank lines
		return '\n'.join(chunk for chunk in chunks if chunk)

	def build(self, sender, recipient):
		msg = EmailMessage()
		parts = sender.email.split("@")
		parts2 = recipient.email.split("@")

		if self.__text is None:
			self.__text = self.get_text()

		msg['From'] = Address(sender.name, parts[0], parts[1])
		msg['To'] = Address(recipient.email, parts2[0], parts2[1])
		msg['Subject'] = self.subject
		msg['Date'] = formatdate()
		msg['Message-Id'] = make_msgid()

		msg.set_type('text/html')
		msg.set_content(self.__text)
		msg.add_alternative(self.html, subtype="html")

		for filename in os.listdir(self.__attachments_folder):
			path = os.path.join(self.__attachments_folder, filename)
			if not os.path.isfile(path):
				continue
			# Guess the content type based on the file's extension.  Encoding
			# will be ignored, although we should check for simple things like
			# gzip'd or compressed files.
			c_type, encoding = mimetypes.guess_type(path)
			if c_type is None or encoding is not None:
				# No guess could be made, or the file is encoded (compressed), so
				# use a generic bag-of-bits type.
				c_type = 'application/octet-stream'
			maintype, subtype = c_type.split('/', 1)
			with open(path, 'rb') as fp:
				msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=filename)

		return msg
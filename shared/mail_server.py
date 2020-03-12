class MailServer:

	host: str = ""
	port: int = 25
	username: str = ""
	password: str = ""
	limit: int = -1
	__usage: int = 0
	__disabled: bool = False

	def enable(self):
		self.__disabled = False

	def disable(self):
		self.__disabled = True

	def increment_usage(self):
		self.__usage += 1

	def is_limited(self):
		return self.limit != -1

	def is_limit_reached(self):
		return self.is_limited() and self.__usage >= self.limit

	def is_disabled(self):
		return self.__disabled

	def is_enabled(self):
		return not self.__disabled

	def is_ok(self):
		return self.is_enabled() and not self.is_limit_reached()
import sys


class Command:

	def InputSize(self, size):
		if size < 1:
			raise Exception("Specify at least 1 input")

	OutputSize = 0
	MultiThreadable = False
	ShareResources = False

	def __init__(self, name=None):
		self.name = name
		self.data = []

	def routine(self, instream):
		self.data = instream
		return ()

	def hook_prompt(self, lock, statement):
		if statement[0] != "watch":
			return
		if len(statement) == 1 or self.name in statement[1:]:
			with lock:
				print("Watch name: %s" % self.name)
				if not self.data:
					print(" (Empty)")
				for i, d in enumerate(self.data):
					print(" %d: Type=%s, Value=%s" % (i, str(type(d)), str(d)))

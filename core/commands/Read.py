import threading

class Command:

	InputSize = 0
	OutputSize = 1
	MultiThreadable = False
	ShareResources = True

	def __init__(self, file):
		self.fp = open(file, "r")

	def routine(self, instream):
		line = self.fp.readline()
		if not line:
			self.fp.close()
			return None
		return (line,)

import threading

class Command:

	InputSize = 1
	OutputSize = 0
	MultiThreadable = False
	ShareResources = True

	def __init__(self, file):
		self.fp = open(file, "w")

	def routine(self, instream):
		self.fp.write(instream[0])
		return ()

	def __del__(self):
		self.fp.close()

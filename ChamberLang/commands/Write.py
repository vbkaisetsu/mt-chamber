import threading

class Command:

	InputSize = 1
	OutputSize = 0
	MultiThreadable = False

	def __init__(self, file, buff=-1):
		self.fp = open(file, "w", buffering=buff)

	def routine(self, instream):
		self.fp.write(instream[0])
		return ()

	def __del__(self):
		self.fp.close()

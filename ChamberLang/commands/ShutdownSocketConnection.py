import socket


class Command:

	InputSize = 1
	OutputSize = 0
	MultiThreadable = True
	ShareResources = True

	def __init__(self, threads, how):
		if "r" in how and "w" in how:
			self.how = socket.SHUT_RDWR
		if "r" in how:
			self.how = socket.SHUT_RD
		if "w" in how:
			self.how = socket.SHUT_WR
		else:
			raise Exception("Option \"how\" should have \"r\", \"w\" or both characters")


	def routine(self, instream):
		conn = instream[0]
		conn.shutdown(self.how)
		return ()

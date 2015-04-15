class Command:

	InputSize = 1
	OutputSize = 2
	MultiThreadable = True
	ShareResources = True

	def __init__(self, length=1024, decode=None):
		self.length = int(length)
		self.decode = decode

	def routine(self, instream):
		conn = instream[0]
		data = conn.recv(self.length)
		if self.decode:
			data = data.decode(self.decode)
		return (conn, data)

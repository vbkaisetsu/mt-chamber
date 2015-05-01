class Command:

	InputSize = 1
	OutputSize = 2
	MultiThreadable = True
	ShareResources = True

	def __init__(self, threads, size=1024, decode=None):
		self.size = int(size)
		self.decode = decode

	def routine(self, thread_id, instream):
		conn = instream[0]
		data = conn.recv(self.size)
		if self.decode:
			data = data.decode(self.decode)
		return (conn, data)

class Command:

	InputSize = 1
	OutputSize = 0
	MultiThreadable = True
	ShareResources = True

	def __init__(self, threads):
		pass

	def routine(self, thread_id, instream):
		conn = instream[0]
		conn.close()
		return ()

class Command:

	InputSize = 1
	OutputSize = 0
	MultiThreadable = True
	ShareResources = True

	def routine(self, instream):
		conn = instream[0]
		conn.close()
		return ()

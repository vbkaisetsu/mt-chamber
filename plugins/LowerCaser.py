class Command:

	InputSize = 1
	OutputSize = 1
	MultiThreadable = True
	ThreadIndependent = False

	def __init__(self):
		return

	def routine(self, instream):
		return (instream[0].lower(),)

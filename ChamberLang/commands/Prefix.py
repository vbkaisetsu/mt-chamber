class Command:

	InputSize = 1
	OutputSize = 1
	MultiThreadable = True
	ShareResources = False

	def __init__(self, string=""):
		self.prefix = string

	def routine(self, instream):
		return (self.suffix + instream[0],)

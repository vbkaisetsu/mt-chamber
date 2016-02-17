class Command:

	InputSize = 1
	OutputSize = 1
	MultiThreadable = True
	ShareResources = False

	def __init__(self, string=""):
		self.suffix = string

	def routine(self, instream):
		return (instream[0] + self.suffix,)

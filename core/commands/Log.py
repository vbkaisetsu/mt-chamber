class Command:

	def InputSize(self, size):
		if size != len(self.tags):
			raise Exception("Different number of input and tags")

	OutputSize = 0
	MultiThreadable = False

	def __init__(self, file, tags):
		self.fp = open(file, "a", buffering=1)
		self.tags = tags.split(";")

	def routine(self, instream):
		for tag, data in zip(self.tags, instream):
			print("%s: " % tag, end="", file=self.fp)
			print(data, file=self.fp)
		return ()

	def __del__(self):
		self.fp.close()

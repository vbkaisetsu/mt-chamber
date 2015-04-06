class Command:

	InputSize = 2
	OutputSize = 2
	MultiThreadable = True
	ThreadIndependent = False

	def __init__(self, maxlen1=100, maxlen2=100, maxratio=8):
		self.maxlen1 = maxlen1
		self.maxlen2 = maxlen2
		self.maxratio = maxratio

	def routine(self, instream):
		len1 = len(instream[0].split())
		len2 = len(instream[1].split())
		if len1 == 0 or len2 == 0 or len1 > self.maxlen1 or len2 > self.maxlen2 or len1 / len2 > self.maxratio or len2 / len1 > self.maxratio:
			return ("", "")
		return instream

import random


class Command:

	def InputSize(self, size):
		if self.count < 0:
			if size > 1:
				raise Exception("Too many input are given")
		elif size != 0:
			raise Exception("You can not specify any input if `count' is set")

	OutputSize = 1
	MultiThreadable = False
	ShareResources = False

	def __init__(self, count=-1, scale=1):
		self.count = int(count)
		self.scale = scale
		self.counter = 0

	def routine(self, instream):
		c = self.counter
		if c == self.count:
			return None
		self.counter += 1
		return (random.random() * self.scale,)

import subprocess


class Command:

	InputSize = 1
	OutputSize = 1
	MultiThreadable = True
	ShareResources = True

	def __init__(self):
		return

	def routine(self, instream):
		wordconcat = " ".join(instream[0].split())
		return (wordconcat + "\n",)

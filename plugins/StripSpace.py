import subprocess


class Command:

	InputSize = 1
	OutputSize = 1
	MultiThreadable = True
	ShareResources = False

	def __init__(self):
		return

	def routine(self, instream):
		wordconcat = " ".join(instream[0].split())
		return (wordconcat + "\n",)

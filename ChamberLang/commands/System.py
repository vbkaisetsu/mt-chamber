import subprocess

import shlex


class Command:

	InputSize = 1
	OutputSize = 1
	MultiThreadable = True
	ShareResources = False

	def __init__(self, command, showerr=False):
		self.command = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None if showerr else subprocess.PIPE, universal_newlines=True)

	def routine(self, instream):
		if instream[0] == "":
			return ("",)
		self.command.stdin.write(instream[0])
		self.command.stdin.flush()
		outstream = self.command.stdout.readline()
		return (outstream,)

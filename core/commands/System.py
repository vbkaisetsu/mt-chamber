import subprocess


class Command:

	InputSize = 1
	OutputSize = 1
	MultiThreadable = True
	ThreadIndependent = True

	def __init__(self, command, showerr=False):
		self.command = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None if showerr else subprocess.PIPE, universal_newlines=True, shell=True)

	def routine(self, instream):
		self.command.stdin.write(instream[0])
		self.command.stdin.flush()
		outstream = self.command.stdout.readline()
		return (outstream,)

import socket


class Command:

	InputSize = 0
	OutputSize = 1
	MultiThreadable = False

	def __init__(self, ipaddr, port, backlog=1):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((ipaddr, int(port)))
		self.socket.listen(backlog)
		self.socket.settimeout(0.5)
		self.stop_request = False

	def routine(self, instream):
		while True:
			if not self.stop_request:
				try:
					conn, addr = self.socket.accept()
					return (conn,)
				except socket.timeout:
					pass
			else:
				return None

	def kill(self):
		self.stop_request = True

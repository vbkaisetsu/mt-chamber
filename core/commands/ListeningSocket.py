import socket


class Command:

	InputSize = 0
	OutputSize = 1
	MultiThreadable = False

	def __init__(self, ipaddr, port, backlog=1):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((ipaddr, int(port)))
		self.socket.listen(backlog)

	def routine(self, instream):
		conn, addr = self.socket.accept()
		return (conn,)

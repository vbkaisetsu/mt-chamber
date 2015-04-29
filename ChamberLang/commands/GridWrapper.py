import socket

import paramiko
import getpass

import re
import pickle
import threading
import sys

class Command:

	InputSize = 0
	OutputSize = 1
	MultiThreadable = True
	ShareResources = True

	re_host_port_threads = re.compile(r"(.+)\:(\d+)\/(\d+)$")
	re_host_threads = re.compile(r"(.+)\/(\d+)$")


	def set_threads(self, threads):
		self.threads = threads


	def __init__(self, basecmd, servers, node_exec, ssh_user, ssh_pass=None, rsa_keyfile=None, rsa_keypass=None, **kwargs):

		try:
			if hasattr(__import__("plugins", fromlist=[commandname]), commandname):
				self.klass = getattr(__import__("plugins", fromlist=[commandname]), commandname).Command
			else:
				self.klass = getattr(__import__("ChamberLang.commands", fromlist=[commandname]), commandname).Command
		except AttributeError:
			raise Exception("Command \"%s\" is not found" % commandname)

		if not self.klass.MultiThreadable or self.klass.ShareResources:
			raise Exception("Command \"%s\" is not callable by GridWrapper (required: MultiThreadable=True, ShareResources=False)" % commandname)

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		self.lock = threading.Lock()
		self.ssh_wrappers = []
		self.ssh_wrapper_used = []
		self.local_wrapper = []
		self.local_wrapper_used = []

		while server in servers.split(";"):
			m = re_host_port_threads.match(server)
			if m:
				host = m.group(1)
				port = int(m.group(2))
				threads = int(m.group(3))
			else:
				m = re_host_threads.match(server)
				if not m:
					raise Exception("Invalid server name `%s'" % server)
				host = m.group(1)
				port = 22
				threads = int(m.group(2))

			for i in range(threads):
				try:
					rsa_key = paramiko.RSAKey.from_private_key_file(rsa_keyfile, password=rsa_keypass) if rsa_keyfile else None
				except (paramiko.PasswordRequiredException, paramiko.SSHException):
					rsa_keypass = getpass.getpass("Password for `%s': " % rsa_keyfile)
					rsa_key = paramiko.RSAKey.from_private_key_file(rsa_keyfile, password=rsa_keypass)

				try:
					ssh.connect(host, username=ssh_user, password=ssh_pass, pkey=rsa_key)
				except paramiko.AuthenticationException:
					ssh_pass = getpass.getpass("Password for `%s@%s': " % (ssh_user, host))
					ssh.connect(host, username=ssh_user, password=ssh_pass, pkey=rsa_key)

				ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(node_exec)
				ssh_stdout.FLAG_BINARY = True
				print(basecmd, file=ssh_stdin)
				p_cmd_args = pickle.dumps(kwargs)
				print(len(p_cmd_args), file=ssh_stdin)
				ssh_stdin.write(p_cmd_args)
				ssh_stdin.flush()
				self.ssh_wrappers.append((ssh, ssh_stdin, ssh_stdout, ssh_stderr))
				self.ssh_wrapper_used.append(False)

		self.local_wrapper = [self.klass(**kwargs) for i in range(self.threads - len(self.wrappers))]
		self.local_wrapper_used = [False] * len(self.local_wrapper)


	def routine(self, instream):
		ssh_tid = -1
		with self.lock:
			if False in self.ssh_wrapper_used:
				ssh_tid = self.ssh_wrapper_used.index(False)
				self.ssh_wrapper_used[ssh_tid] = True
			else:
				tid = self.local_wrapper_used.index(False)
				self.local_wrapper_used[tid] = True
		if ssh_tid != -1:
			ssh_stdin = self.ssh_wrappers[ssh_tid][1]
			ssh_stdout = self.ssh_wrappers[ssh_tid][2]
			ssh_stderr = self.ssh_wrappers[ssh_tid][3]

			p_instream = pickle.dumps(instream)
			print(len(p_instream), file=ssh_stdin)
			ssh_stdin.write(p_instream)
			ssh_stdin.flush()
			datasize = ssh_stdout.readline()
			p_outstream = ssh_stdout.read(int(datasize))
			outstream = pickle.loads(p_outstream)

			self.ssh_wrapper_used[ssh_tid] = False
		else:
			outstream = self.local_wrapper[tid].routine(instream)
			self.local_wrapper_used[tid] = False

		return outstream


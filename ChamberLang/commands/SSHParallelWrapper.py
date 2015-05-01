import socket

import paramiko
import getpass

import re
import pickle
import threading
import sys
import os

from ChamberLang.core import MessageException


def GetDecriptedKey(filename, password):
	supported_keys = [paramiko.DSSKey, paramiko.ECDSAKey, paramiko.RSAKey]
	saved_exception = None
	for loader in supported_keys:
		try:
			key = loader.from_private_key_file(filename, password=password)
		except paramiko.SSHException as e:
			saved_exception = e
			continue
		return key
	raise saved_exception


class Command:

	KeyData = {None: None}

	def InputSize(self, size):
		if callable(self.klass.InputSize):
			if self.local_wrapper:
				self.local_wrapper[0].InputSize(size)
		else:
			if size != self.klass.InputSize:
				raise Exception("Input size mismatch (required %d, given %d)" % (self.klass.InputSize, size))

	def OutputSize(self, size):
		if callable(self.klass.OutputSize):
			if self.local_wrapper:
				self.local_wrapper[0].OutputSize(size)
		else:
			if size != self.klass.OutputSize:
				raise Exception("Output size mismatch (required %d, given %d)" % (self.klass.OutputSize, size))

	MultiThreadable = True
	ShareResources = True

	re_host_port_threads = re.compile(r"(.+)\:(\d+)\/(\d+)$")
	re_host_threads = re.compile(r"(.+)\/(\d+)$")


	def __init__(self, threads, basecmd, nodes, ssh_user, node_exec=None, ssh_pass=None, keyfile=None, keypass=None, **kwargs):

		try:
			if hasattr(__import__("plugins", fromlist=[basecmd]), basecmd):
				self.klass = getattr(__import__("plugins", fromlist=[basecmd]), basecmd).Command
			else:
				self.klass = getattr(__import__("ChamberLang.commands", fromlist=[basecmd]), basecmd).Command
		except AttributeError:
			raise Exception("Command \"%s\" is not found" % basecmd)
		if not self.klass.MultiThreadable or self.klass.ShareResources:
			raise Exception("Command \"%s\" is not callable by GridWrapper (required: MultiThreadable=True, ShareResources=False)" % commandname)

		self.lock = threading.Lock()
		self.ssh_wrappers = []
		self.local_wrapper = []

		for node in nodes.split(";"):
			m = Command.re_host_port_threads.match(node)
			if m:
				host = m.group(1)
				port = int(m.group(2))
				node_threads = int(m.group(3))
			else:
				m = Command.re_host_threads.match(node)
				if not m:
					raise Exception("Invalid server name `%s'" % server)
				host = m.group(1)
				port = 22
				node_threads = int(m.group(2))

			for i in range(node_threads):
				try:
					if keyfile and keyfile not in Command.KeyData:
						Command.KeyData[keyfile] = GetDecriptedKey(keyfile, password=keypass)
				except (paramiko.PasswordRequiredException, paramiko.SSHException):
					keypass = getpass.getpass("Password for `%s': " % keyfile)
					try:
						Command.KeyData[keyfile] = GetDecriptedKey(keyfile, password=keypass)
					except:
						raise MessageException("Key type or password is wrong (supported: DSA, ECDSA, and RSA)")

				ssh = paramiko.SSHClient()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				try:
					ssh.connect(host, username=ssh_user, password=ssh_pass, pkey=Command.KeyData[keyfile])
				except paramiko.AuthenticationException:
					ssh_pass = getpass.getpass("Password for `%s@%s': " % (ssh_user, host))
					ssh.connect(host, username=ssh_user, password=ssh_pass, pkey=Command.KeyData[keyfile])
				if not node_exec:
					node_exec = os.path.join(os.path.dirname(__file__), "../../ssh-parallel-node.py")
				ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(node_exec)
				ssh_stdout.FLAG_BINARY = True
				print(basecmd, file=ssh_stdin)
				p_cmd_args = pickle.dumps(kwargs)
				print(len(p_cmd_args), file=ssh_stdin)
				ssh_stdin.write(p_cmd_args)
				ssh_stdin.flush()
				self.ssh_wrappers.append((ssh, ssh_stdin, ssh_stdout, ssh_stderr))

		self.local_wrapper = [self.klass(**kwargs) for i in range(threads - len(self.ssh_wrappers))]


	def routine(self, thread_id, instream):
		if thread_id < len(self.ssh_wrappers):
			ssh_stdin = self.ssh_wrappers[thread_id][1]
			ssh_stdout = self.ssh_wrappers[thread_id][2]
			ssh_stderr = self.ssh_wrappers[thread_id][3]

			p_instream = pickle.dumps(instream)
			print(len(p_instream), file=ssh_stdin)
			ssh_stdin.write(p_instream)
			ssh_stdin.flush()
			datasize = ssh_stdout.readline()
			p_outstream = ssh_stdout.read(int(datasize))
			outstream = pickle.loads(p_outstream)

		else:
			tid = thread_id - len(self.ssh_wrappers)
			outstream = self.local_wrapper[tid].routine(instream)

		return outstream


import re
import queue
import threading
import shlex
import sys
import readline
import errno
from collections import defaultdict
import traceback


class Killed(Exception):
	pass


class ChamberInitialError(Exception):
	def __init__(self, value, linenumber, trace=None):
		self.value = value
		self.linenumber = linenumber
		self.trace = trace
	def __str__(self):
		return repr(self.value)


class ChamberRuntimeError(Exception):
	def __init__(self, value, trace):
		self.value = value
		self.trace = trace
	def __str__(self):
		return repr(self.value)


class DistributorVariable:
	def __init__(self):
		self.target = set()

	def add_target(self, proc, i):
		self.target.add((proc, i))

	def push_stop_request(self, order):
		for proc, i in self.target:
			proc.put_stop_request(order)

	def push(self, data, order):
		for proc, i in self.target:
			if not proc.put_data(i, data, order):
				return False
		return True


class Processor:
	def __init__(self, commandname, argdict, insize, outsize, threads=1, unsrt_limit=100):
		try:
			if hasattr(__import__("plugins", fromlist=[commandname]), commandname):
				self.klass = getattr(__import__("plugins", fromlist=[commandname]), commandname).Command
			else:
				self.klass = getattr(__import__("core.commands", fromlist=[commandname]), commandname).Command
		except AttributeError:
			raise Exception("Command \"%s\" is not found" % commandname)

		self.command = [self.klass(**argdict) for i in range(1 if not self.klass.MultiThreadable or self.klass.ShareResources else threads)]
		self.inputqueue = queue.Queue()
		self.outputvariable = [DistributorVariable() for i in range(outsize)]
		self.lock = threading.Lock()
		self.ackput_condition = threading.Condition()
		self.seqorder = 0
		self.unsrt_limit = unsrt_limit
		self.temp_input = defaultdict(lambda : [None] * insize)
		self.unsrt_memory = [False] * (self.unsrt_limit + 1)
		self.unsrt_top = 0
		self.stop_at = -1
		self.process_cnt = 0
		self.singlethread_order = 0
		self.threads = threads
		self.InputSize = insize
		self.OutputSize = outsize
		self.killing = False
		self.done = False

	def put_stop_request(self, order):
		self.stop_at = order
		for i in range(self.threads):
			self.inputqueue.put((order, None))

	def put_data(self, i, data, order):
		with self.ackput_condition:
			while order >= self.unsrt_top + self.unsrt_limit and not self.killing:
				self.ackput_condition.wait()
		if self.done:
			return False
		if self.killing:
			raise Killed("killing is set")
		self.temp_input[order][i] = data
		if self.klass.MultiThreadable:
			if None not in self.temp_input[order]:
				self.inputqueue.put((order, self.temp_input.pop(order)))
		else:
			while self.singlethread_order in self.temp_input:
				if None in self.temp_input[self.singlethread_order]:
					break
				self.inputqueue.put((self.singlethread_order, self.temp_input.pop(self.singlethread_order)))
				self.singlethread_order += 1
		return True

	def run_routine(self, thread_id_orig):
		thread_id = thread_id_orig
		if not self.klass.MultiThreadable or self.klass.ShareResources:
			thread_id = 0
		if self.InputSize != 0:
			order, instream = self.inputqueue.get()
			if self.killing:
				raise Killed("killing is set")
		else:
			with self.lock:
				order = self.seqorder
				self.seqorder += 1
			instream = ()
		try:
			outstream = self.command[thread_id].routine(instream) if instream is not None else None
		except Exception as e:
			tr = traceback.format_exc()
			raise ChamberRuntimeError("Runtime error", tr)
		if self.InputSize != 0:
			with self.ackput_condition:
				self.unsrt_memory[order - self.unsrt_top] = True
				if False not in self.unsrt_memory:
					unsrt_mem_shiftsize = self.unsrt_limit
				else:
					unsrt_mem_shiftsize = self.unsrt_memory.index(False)
				if unsrt_mem_shiftsize != 0:
					self.unsrt_memory[:unsrt_mem_shiftsize] = []
					self.unsrt_memory.extend([False] * unsrt_mem_shiftsize)
					self.unsrt_top += unsrt_mem_shiftsize
				self.ackput_condition.notify_all()
		if outstream is not None:
			if len(outstream) != self.OutputSize:
				raise ChamberRuntimeError("Returned tuple size mismatch (required %d, returned %d)" % (self.OutputSize, len(outstream)), "")
			for i, v in enumerate(outstream):
				if not self.outputvariable[i].push(v, order):
					self.done = True
					with self.ackput_condition:
						self.ackput_condition.notify_all()
					return False
		self.lock.acquire()
		cnt = self.process_cnt + 1 if instream is not None and outstream is not None else self.process_cnt
		if cnt == self.stop_at or outstream is None and instream is not None:
			if instream is not None and outstream is not None:
				self.process_cnt += 1
			self.lock.release()
			for ov in self.outputvariable:
				ov.push_stop_request(cnt)
			self.inputqueue.put((cnt, None))
			self.done = True
			with self.ackput_condition:
				self.ackput_condition.notify_all()
			return False
		if instream is not None:
			self.process_cnt += 1
		self.lock.release()
		return True


class ScriptRunner:
	availablename_matcher = re.compile("[A-Za-z_]\w*$")
	esc_seq_matcher = re.compile(r"\\(.)")
	intfloat_matcher = re.compile(r"[+\-]?(\d*\.?\d+|\d+\.?\d*)$")

	def esc_replacer(m):
		esc_ch = m.group(1)
		if esc_ch == "n":
			return "\n"
		return esc_ch

	def __init__(self, lines, threads=1, unsrt_limit=100):
		variables = {}
		alias = {}
		self.procs = []
		prevline = ""
		self.threads = threads
		self.running = threading.Event()
		self.running.set()

		for n, line in enumerate(lines):
			line = line.strip()

			# skip comment line
			if not line or line[0] == "#":
				continue

			# Concatinate
			line = prevline + line
			if line[-1] == "\\":
				prevline = line[:-1] + " "
				continue
			prevline = ""

			shline = shlex.shlex(line)
			shline.whitespace_split = False
			shline.escapedquotes = "\"'"
			try:
				tokens = list(shline)
			except ValueError as e:
				raise ChamberInitialError(e, n+1)

			for i, w in enumerate(tokens):
				if w in alias:
					tokens[i:i+1] = alias[w]

			command = tokens[0]

			if command == "Alias":
				if len(tokens) < 3:
					raise ChamberInitialError("Syntax error", n+1)
				if not ScriptRunner.availablename_matcher.match(tokens[1]):
					raise ChamberInitialError("Syntax error", n+1)
				alias[tokens[1]] = tokens[2:]
				continue

			options = {}
			invar_name = []
			outvar_name = []
			commandthreads = -1

			opt_tokens = tokens[1:] + [""]
			while True:
				token = opt_tokens.pop(0)
				if token == "<":
					if not ScriptRunner.availablename_matcher.match(opt_tokens[0]):
						raise ChamberInitialError("Syntax error", n+1)
					while ScriptRunner.availablename_matcher.match(opt_tokens[0]):
						invar_name.append(opt_tokens.pop(0))
				elif token == ">":
					if not ScriptRunner.availablename_matcher.match(opt_tokens[0]):
						raise ChamberInitialError("Syntax error", n+1)
					while ScriptRunner.availablename_matcher.match(opt_tokens[0]):
						outvar_name.append(opt_tokens.pop(0))
				elif token == ":":
					if not ScriptRunner.availablename_matcher.match(opt_tokens[0]):
						raise ChamberInitialError("Syntax error", n+1)
					optname = opt_tokens.pop(0)
					if opt_tokens[0] == "=":
						opt_tokens.pop(0)
						optval = opt_tokens.pop(0)
						if optval == "True":
							options[optname] = True
						elif optval == "False":
							options[optname] = False
						elif len(optval) >= 2 and (optval[0] == optval[-1] == "\"" or optval[0] == optval[-1] == "'"):
							string = ScriptRunner.esc_seq_matcher.sub(ScriptRunner.esc_replacer, optval[1:-1])
							options[optname] = string
						elif ScriptRunner.intfloat_matcher.match(optval):
							options[optname] = float(optval)
						else:
							raise ChamberInitialError("Syntax error", n+1)
					else:
						options[optname] = True
				elif token == "*":
					if not opt_tokens[0].isdigit() or commandthreads != -1:
						raise ChamberInitialError("Syntax error", n+1)
					commandthreads = int(opt_tokens.pop(0))
				elif token == "":
					break
				else:
					raise ChamberInitialError("Syntax error", n+1)

			if commandthreads == -1:
				commandthreads = self.threads
			try:
				proc = Processor(command, options, len(invar_name), len(outvar_name), threads=commandthreads, unsrt_limit=unsrt_limit)
			except Exception as e:
				tr = traceback.format_exc()
				raise ChamberInitialError(e, n+1, tr)

			if callable(proc.klass.InputSize):
				try:
					proc.command[0].InputSize(len(invar_name))
				except Exception as e:
					tr = traceback.format_exc()
					raise ChamberInitialError(e, n+1, tr)
			elif len(invar_name) != proc.klass.InputSize:
				raise ChamberInitialError("Input size mismatch (required %d, given %d)" % (proc.klass.InputSize, len(invar_name)), n+1)

			if callable(proc.klass.OutputSize):
				try:
					proc.command[0].OutputSize(len(outvar_name))
				except:
					tr = traceback.format_exc()
					raise ChamberInitialError(e, n+1, tr)
			elif len(outvar_name) != proc.klass.OutputSize:
				raise ChamberInitialError("Output size mismatch (required %d, given %d)" % (proc.klass.OutputSize, len(outvar_name)), n+1)

			for i, varname in enumerate(invar_name):
				if varname not in variables:
					raise ChamberInitialError("Variable \"%s\" is not defined" % (varname), n+1)
				variables[varname].add_target(proc, i)

			for i, varname in enumerate(outvar_name):
				variables[varname] = proc.outputvariable[i]

			self.procs.append((n+1, proc, commandthreads))

	def killprocs(self):
		for lnum, proc, threads in self.procs:
			proc.killing = True
			if hasattr(proc.klass, "kill"):
				for c in proc.command:
					c.kill()
			for i in range(proc.threads):
				proc.inputqueue.put((0, None))
			with proc.ackput_condition:
				proc.ackput_condition.notify_all()

	def run(self, prompt=False):
		prompt_lock = threading.Lock()

		def subWorker(proc, thread_id, lnum):
			try:
				while not proc.killing:
					ret = proc.run_routine(thread_id)
					if not ret:
						return
					self.running.wait()
			except Killed:
				return
			except ChamberRuntimeError as e:
				self.killprocs()
				with prompt_lock:
					print("Runtime error at line %d:" % lnum, file=sys.stderr)
					if hasattr(e.value, "errno") and e.value.errno == errno.EPIPE:
						print("System command has been died", file=sys.stderr)
					print(e.trace, file=sys.stderr)

		ts = []
		for lnum, proc, threads in self.procs:
			if threads == -1:
				threads = self.threads
			for i in range(threads if proc.klass.MultiThreadable else 1):
				t = threading.Thread(target=subWorker, args=(proc, i, lnum))
				t.start()
				ts.append(t)

		try:
			if prompt:
				while True:
					try:
						statement_line = input(">>> ")
					except EOFError:
						print()
						statement_line = "exit"

					shline = shlex.shlex(statement_line, posix=True)
					shline.whitespace_split = True
					shline.escapedquotes = "\"'"
					try:
						statement = list(shline)
					except ValueError as e:
						print(e.value, file=sys.stderr)
						continue

					if not statement:
						continue

					if statement[0] == "start":
						if self.running.is_set():
							print("Status is already set to running")
							continue
						self.running.set()
						print("Restarting processes...")

					elif statement[0] == "pause":
						if not self.running.is_set():
							print("Status is already set to pausing")
							continue
						self.running.clear()
						print("Pausing processes...")

					elif statement[0] == "exit":
						working = False
						for t in ts:
							if t.is_alive():
								print("Some processes are working")
								working = True
								break
						if working:
							continue
						else:
							break

					elif statement[0] == "kill":
						print("Killing processes...")
						self.running.set()
						self.killprocs()
						break

					for lnum, proc, threads in self.procs:
						if hasattr(proc.klass, "hook_prompt"):
							for cmd in proc.command:
								cmd.hook_prompt(statement)

			for t in ts:
				t.join()

		except KeyboardInterrupt:
			print("Killing processes...")
			self.running.set()
			self.killprocs()

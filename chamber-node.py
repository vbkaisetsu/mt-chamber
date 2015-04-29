#!/usr/bin/python3

import sys
import pickle


def main():

	commandname = sys.stdin.buffer.readline().decode("utf-8").rstrip("\n")
	datasize = sys.stdin.buffer.readline()
	p_kwargs = sys.stdin.buffer.read(int(datasize))
	kwargs = pickle.loads(p_kwargs)

	try:
		if hasattr(__import__("plugins", fromlist=[commandname]), commandname):
			klass = getattr(__import__("plugins", fromlist=[commandname]), commandname).Command
		else:
			klass = getattr(__import__("ChamberLang.commands", fromlist=[commandname]), commandname).Command
	except AttributeError:
		raise Exception("Command \"%s\" is not found" % commandname)

	command = klass(**kwargs)

	while True:
		datasize = sys.stdin.buffer.readline()
		p_instream = sys.stdin.buffer.read(int(datasize))
		instream = pickle.loads(p_instream)
		outstream = command.routine(instream)
		p_outstream = pickle.dumps(outstream)
		print(len(p_outstream), file=sys.stdout)
		sys.stdout.flush()
		sys.stdout.buffer.write(p_outstream)
		sys.stdout.flush()
		if outstream is None:
			break


if __name__ == "__main__":
	main()

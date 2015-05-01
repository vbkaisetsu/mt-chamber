#!/usr/bin/python3

import sys
import pickle
import traceback


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
		outdata = {}
		try:
			outstream = command.routine(instream)
			outdata["status"] = "success"
			outdata["data"] = outstream
			if outstream is None:
				break
		except Exception:
			tr = traceback.format_exc()
			outdata["status"] = "failed"
			outdata["data"] = tr
			break
		finally:
			p_outdata = pickle.dumps(outdata)
			print(len(p_outdata), file=sys.stdout)
			sys.stdout.flush()
			sys.stdout.buffer.write(p_outdata)
			sys.stdout.flush()


if __name__ == "__main__":
	main()

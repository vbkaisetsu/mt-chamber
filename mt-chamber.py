#!/usr/bin/python3

import sys

from core.ChamberLang import ScriptRunner, ChamberInitialError
from argparse import ArgumentParser

def main():
	parser = ArgumentParser()
	parser.add_argument("-t", "--threads", type=int, default=1, help="number of threads (default: 1)")
	parser.add_argument("-b", "--buffersize", type=int, default=100, help="size of buffer (default: 100)")
	parser.add_argument("-p", "--prompt", action="store_true", help="run with prompt")
	parser.add_argument("FILE", nargs="?", default=None, help="Chamber script file (default: stdin)")
	args = parser.parse_args()

	if args.threads < 1:
		parser.error("--threads must be larger than 1")

	if args.buffersize <= args.threads:
		parser.error("--buffersize must be larger than --threads")

	if args.FILE is None:
		if not args.prompt:
			fstream = sys.stdin
		else:
			parser.error("the following arguments are required in prompt mode: FILE")
	else:
		try:
			fstream = open(args.FILE, "r")
		except IOError:
			print("Error: could not open `%s'" % args.FILE, file=sys.stderr)
			return

	try:
		script = ScriptRunner(fstream, threads=args.threads, buffersize=args.buffersize)
	except ChamberInitialError as e:
		print("At line %d: %s" % (e.linenumber, str(e.value)), file=sys.stderr)
		if e.trace:
			print(e.trace, file=sys.stderr)
		return
	script.run(prompt=args.prompt)

	if fstream:
		fstream.close()


if __name__ == "__main__":
	main()

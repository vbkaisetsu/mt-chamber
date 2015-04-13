#!/usr/bin/python3

import sys

from core.ChamberLang import ScriptRunner
from argparse import ArgumentParser

def main():
	parser = ArgumentParser()
	parser.add_argument("-t", "--threads", type=int, default=1, help="number of threads (default: 1)")
	parser.add_argument("-b", "--buffersize", type=int, default=100, help="size of buffer (default: 100)")
	parser.add_argument("FILE", nargs="?", default=None, help="Chamber script file (default: stdin)")
	args = parser.parse_args()

	if args.threads < 1:
		print("--threads must be larger than 1", file=sys.stderr)
		return

	if args.buffersize <= args.threads:
		print("--buffersize must be larger than --threads", file=sys.stderr)
		return

	if args.FILE is None:
		fstream = sys.stdin
	else:
		try:
			fstream = open(args.FILE, "r")
		except IOError:
			print("Error: could not open `%s'" % args.FILE, file=sys.stderr)
			return

	script = ScriptRunner(fstream, threads=args.threads, buffersize=args.buffersize)
	script.run()

	if fstream:
		fstream.close()


if __name__ == "__main__":
	main()

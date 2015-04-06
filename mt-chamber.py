#!/usr/bin/python3

import sys

from core.ChamberLang import ScriptRunner
from argparse import ArgumentParser

def main():
	parser = ArgumentParser()
	parser.add_argument("--threads", type=int, default=1, help="Number of threads")
	parser.add_argument("--buffersize", type=int, default=100, help="Size of buffer")
	args = parser.parse_args()

	if args.threads < 1:
		print("--threads must be larger than 1", file=sys.stderr)
		return
	if args.buffersize <= args.threads:
		print("--buffersize must be larger than --threads", file=sys.stderr)
		return

	script = ScriptRunner(sys.stdin, threads=args.threads, buffersize=args.buffersize)
	script.run()

if __name__ == "__main__":
	main()

#!/usr/bin/python3

import sys

from core.ChamberLang import ScriptRunner
from argparse import ArgumentParser

def main():
	parser = ArgumentParser()
	parser.add_argument("--threads", type=int, default=1, help="Number of threads")
	parser.add_argument("--queues", type=int, default=100, help="Number of queues")
	args = parser.parse_args()

	if args.threads < 1:
		print("--threads must be larger than 1", file=sys.stderr)
		return
	if args.queues < 1:
		print("--queues must be larger than 1", file=sys.stderr)
		return

	script = ScriptRunner(sys.stdin, threads=args.threads, queues=args.queues)
	script.run()

if __name__ == "__main__":
	main()

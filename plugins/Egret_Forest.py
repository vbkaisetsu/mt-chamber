import subprocess

import shlex


class Command:

    InputSize = 1
    OutputSize = 1
    MultiThreadable = True
    ShareResources = False

    def __init__(self, bin, grammer):
        self.egret = subprocess.Popen([bin, "-lapcfg", "-i=/dev/stdin", "-data=%s" % grammer, "-n=500", "-printForest"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    def routine(self, instream):
        token = instream[0]

        if not token.strip():
            return ("failed\nempty\n",)

        self.egret.stdin.write(token)
        self.egret.stdin.flush()
        egret_tree = ""
        while True:
            egret_tree_line = self.egret.stdout.readline()
            if not egret_tree_line.strip():
                egret_tree += "\n"
                break
            egret_tree += egret_tree_line

        egret_tree = egret_tree.lower()

        if len(egret_tree.rstrip("\n").split("\n")) <= 2:
            self.egret.stdout.readline()
            return ("failed\nparser",)

        return ("success\n" + egret_tree,)

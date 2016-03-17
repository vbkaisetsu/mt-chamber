import subprocess
import re


class Command:

    InputSize = 1
    OutputSize = 2
    MultiThreadable = True
    ShareResources = False

    def __init__(self, bin, config, showerr=False):
        self.travatar = subprocess.Popen([bin, "-config_file", config, "-trace_out", "STDOUT", "-in_format", "egret", "-buffer", "false"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None if showerr else subprocess.PIPE, universal_newlines=True)

        self.span_reg = re.compile(r"\[([0-9]+), ([0-9]+)\]")

    def routine(self, instream):
        egret_tree = instream[0]
        if not egret_tree.startswith("success\n"):
            return (egret_tree, "",)

        egret_tree = egret_tree[8:]
        self.travatar.stdin.write(egret_tree)
        self.travatar.stdin.flush()

        travatar_trace = self.travatar.stdout.readline()
        spltrace = travatar_trace.split(" ||| ")
        m = self.span_reg.match(spltrace[1])

        inputlen = int(m.group(2))

        while True:
            travatar_trace_line = self.travatar.stdout.readline()
            spltrace = travatar_trace_line.split(" ||| ")
            spltree = spltrace[2].split(" ")
            for x in spltree:
                if x and x[0] == x[-1] == "\"":
                    inputlen -= 1
            spltrace[4] = ".\n"
            travatar_trace += " ||| ".join(spltrace)
            if not inputlen:
                break
        
        travatar_output = self.travatar.stdout.readline().rstrip("\n")

        return ("success\n" + travatar_output + "\n" + travatar_trace, travatar_output,)

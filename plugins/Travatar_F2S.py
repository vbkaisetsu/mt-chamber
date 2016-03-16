import subprocess


class Command:

    InputSize = 1
    OutputSize = 2
    MultiThreadable = True
    ShareResources = False

    def __init__(self, bin, config):
        self.travatar = subprocess.Popen([bin, "-config_file", config, "-trace_out", "/dev/stdout", "-in_format", "egret", "-buffer", "false"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    def routine(self, instream):
        egret_tree = instream[0]
        if not egret_tree.startswith("success\n"):
            return (egret_tree, "",)

        egret_tree = egret_tree[8:]
        self.travatar.stdin.write(egret_tree)
        self.travatar.stdin.flush()

        travatar_trace = ""
        travatar_output = self.travatar.stdout.readline().rstrip("\n")
        translation_words = travatar_output.split(" ")
        while True:
            travatar_trace_line = self.travatar.stdout.readline()
            spltrace = travatar_trace_line.split(" ||| ")
            trace_words = spltrace[3].split(" ")
            for w in trace_words:
                if w and w[0] == w[-1] == "\"":
                    translation_words.remove(w[1:-1])
            spltrace[4] = ".\n"
            travatar_trace += " ||| ".join(spltrace)
            if not translation_words:
                break

        return ("success\n" + travatar_output + "\n" + travatar_trace, travatar_output,)

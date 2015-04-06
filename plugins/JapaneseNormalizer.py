import unicodedata
from plugins import zenhan
import re
import os


# カタカナ末尾 -er, -or, -ar の長音記号を正規化（付与）
class KatakanaPSM:

	def __init__(self, database):
		self.replRules = []
		dbfp = open(database, "r")
		for line in dbfp:
			if line[0] == "#":
				continue
			spl = line.rstrip("\n").split(",")
			regNonPSM = re.compile(spl[0])
			self.replRules.append((regNonPSM, spl[1]))

	def addPSM(self, s):
		for rule in self.replRules:
			s = rule[0].sub(rule[1], s)
		return s


class Command:

	KATAKANA_PSM_DB = os.path.join(os.dirname(__file__), "data/katakana_psm.db")

	InputSize = 1
	OutputSize = 1
	MultiThreadable = True
	ThreadIndependent = False

	def __init__(self, psmdb=KATAKANA_PSM_DB):
		self.kpsm = KatakanaPSM(psmdb)

	def routine(self, instream):
		normalline = unicodedata.normalize("NFKC", instream[0])
		normalline = zenhan.h2z(" ".join(normalline.split()))
		normalline = self.kpsm.addPSM(normalline)
		return (normalline,)

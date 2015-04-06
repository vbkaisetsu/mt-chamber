import re


# Replace email address to prevent output personal information
class EmailReplacer:
	def __init__(self):
		self.email_reg = re.compile(r"([A-Za-z0-9!#\$%&'\*\+\-/=\?\^_`\{\|\}~\.]+@\w+(?:\.\w+)+)")

	def replace(self, s):
		return self.email_reg.sub("mail@example.com", s)


# Tags will become garbage of translation models
# <a href="xyz">something happened</a>
# Please click <url http://exmaple.com>here</url>
# icon <img src="xxx">
class TagBracketReplacer:
	def __init__(self):
		self.tag_reg = re.compile("<.+?>")
		self.email_reg = re.compile(r"<([A-Za-z0-9!#\$%&'\*\+\-/=\?\^_`\{\|\}~\.]+@\w+(?:\.\w+)+)>")

	def removeTags(self, s1, s2):
		tagset1 = set()
		tagset2 = set()
		s1_tmp = s1
		s2_tmp = s2
		while True:
			m = self.tag_reg.search(s1_tmp)
			if not m:
				break
			s, e = m.span()
			s1_tmp = s1_tmp[e:]
			tagstr = m.group(0)
			if not self.email_reg.match(tagstr):
				tagset1.add(tagstr)
		while True:
			m = self.tag_reg.search(s2_tmp)
			if not m:
				break
			s, e = m.span()
			s2_tmp = s2_tmp[e:]
			tagstr = m.group(0)
			if not self.email_reg.match(tagstr):
				tagset2.add(m.group(0))
		inter = tagset1.intersection(tagset2)
		for rep in inter:
			s1 = s1.replace(rep, " ")
			s2 = s2.replace(rep, " ")
		return (s1, s2)


class Command:

	InputSize = 2
	OutputSize = 2
	MultiThreadable = True
	ThreadIndependent = False

	def __init__(self):
		self.emailrepl = EmailReplacer()
		self.tagrepl = TagBracketReplacer()

	def routine(self, instream):
		line1 = self.emailrepl.replace(instream[0])
		line2 = self.emailrepl.replace(instream[1])
		return self.tagrepl.removeTags(line1, line2)

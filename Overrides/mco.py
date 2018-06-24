import re

re_mco_baseclass = re.compile('BaseGameClass=\"(.+?)\",?')
re_mco_modclass = re.compile('ModClass=\"(.+?)\"')


class ModClassOverride(object):
	def __init__(self, base_class, mod_class, source_file):
		self.base_class = base_class
		self.mod_class = mod_class
		self.source_file = source_file

	@classmethod
	def from_raw_line(cls, raw_line, source_file):
		print("== Parsing Override: %s -- File: %s" % (raw_line, source_file))
		base_class = re.search(re_mco_baseclass, raw_line).groups(0)[0]
		mod_class = re.search(re_mco_modclass, raw_line).groups(0)[0]
		return cls(base_class, mod_class, source_file)

	def __repr__(self):
		return "ModClassOverrides=(" + "BaseGameClass=\"%s\", ModClass=\"%s\")" % (self.base_class, self.mod_class)

	def __eq__(self, other):
		if not isinstance(other, ModClassOverride):
			return False
		if self.base_class != other.base_class or self.mod_class != other.mod_class:
			return False
		return True

	def __hash__(self):
		return hash(str(self))
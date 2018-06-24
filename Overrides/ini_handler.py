import platform
import re

from Overrides.constants import re_mco_add
from Overrides.mco import ModClassOverride


class BaseIniHandler(object):
	def __init__(self, file_path=None):
		self.file_path = file_path

	def get_text(self):
		with open(self.file_path, "r") as input_file:
			return input_file.read()

	def get_lines(self):
		with open(self.file_path, "r") as input_file:
			return input_file.readlines()

	def write_xce_text(self, new_text):
		with open(self.file_path, "w") as output_file:
			return output_file.write(new_text)

	@classmethod
	def get_platform_specific_config_path(cls, wotc=True):
		xcom_vfs_dir_name = "XCOM2 War of the Chosen" if wotc else "XCOM2"

		if platform.system() == "Windows":
			path = "\Documents\my games\%s\XComGame\Config\\" % xcom_vfs_dir_name

		elif platform.system() == "Darwin":
			# TODO: Uncertain about these paths
			xcom_product_dir_name = "XCOM 2"
			if wotc:
				xcom_product_dir_name = "XCOM 2 WotC"

			path = "/Library/Application Support/Feral Interactive/%s/VFS/Local/my games/%s/XCOMGame/Config/" % (
				xcom_product_dir_name, xcom_vfs_dir_name
			)

		elif platform.system() == "Linux":
			# TODO: Uncertain about these paths
			xcom_product_dir_name = "XCOM 2"
			if wotc:
				xcom_product_dir_name = "XCOM 2 WotC"

			path = ".local/share/feral-interactive/%s/VFS/Local/my games/%s/XComGame/Config/" % (
				xcom_product_dir_name, xcom_vfs_dir_name
			)
		else:
			raise NotImplementedError("Unrecognized system OS/Platform")
		return path


class XComModOptionsIniHandler(BaseIniHandler):
	active_mods = []

	def __init__(self, file_path=None):
		super(XComModOptionsIniHandler, self).__init__(file_path=file_path)
		self._parse_active_mods()

	def _parse_active_mods(self):
		lines = self.get_lines()
		print("XComModOptionsInitHandler._parse_active_mods()", len(lines))
		if not lines[0].strip().startswith("[Engine.XComModOptions]"):
			raise ValueError(
				"Invalid XComModOptions.ini! %s\n" 
				"Expected %s, got: %s" % (self.file_path, "[Engine.XComModOptions]", lines[0])
			)

		line_counter = 0
		for line in lines:
			line_counter += 1
			if line_counter < 2:  # Skip section head
				continue
			line = line.strip()
			if not line.startswith("ActiveMods="):  # Skip blanks etc
				continue
			parts = line.split("=")
			if len(parts) < 2:
				raise ValueError("Invalid XComModOptions.ini! Problem on line %s : %s" % (line_counter, line))
			self.active_mods.append(parts[1])


class XComEngineIniHandler(BaseIniHandler):
	@classmethod
	def get_overrides_from_file(cls, file_path):
		# print("==== Getting overrides from file: %s" % file_path)
		ini_file = XComEngineIniHandler(file_path)
		ini_lines = ini_file.get_lines()

		overrides = []
		for line in ini_lines:
			if not line or line.startswith(';'):  # Ignore blanks and commented lines
				continue
			match = re.search(re_mco_add, line)
			if match:
				if len(match.groups()) > 1:
					raise Exception("Multiple matches for a single line - Badly formatted ini file: %s" % file_path)
				overrides.append(ModClassOverride.from_raw_line(line.rstrip(), source_file=file_path))
		return overrides

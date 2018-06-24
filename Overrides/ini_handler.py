import platform
import re

from Overrides.constants import re_mco_add
from Overrides.mco import ModClassOverride


class XComEngineIniHandler(object):

	def __init__(self, xce_path=None):
		self.xce_path = xce_path

	def get_text(self):
		with open(self.xce_path, "r") as input_file:
			return input_file.read()

	def get_lines(self):
		with open(self.xce_path, "r") as input_file:
			return input_file.readlines()

	def write_xce_text(self, new_text):
		with open(self.xce_path, "w") as output_file:
			return output_file.write(new_text)

	@classmethod
	def get_platform_specific_xce_path(cls, wotc=True):
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

import os

from Overrides import cfg
from Overrides.constants import XCE_FILE_NAME, XCMO_FILE_NAME
from Overrides.ini_handler import XComEngineIniHandler, XComModOptionsIniHandler
from Overrides.text_processor import IniTextProcessor

XCOM2_CONF_PATH = XComEngineIniHandler.get_platform_specific_config_path()
XCE_FILE_PATH = os.path.expanduser('~') + XCOM2_CONF_PATH + XCE_FILE_NAME
XCMO_FILE_PATH = os.path.expanduser('~') + XCOM2_CONF_PATH + XCMO_FILE_NAME

# TODO Move this
print("Debug: XComEngine.ini absolute path: '%s'" % XCE_FILE_PATH)
print("Configuration: ")
print(":: WOTC: %s " % cfg.WOTC)
print(":: DryRun: %s " % cfg.DryRun)
print(":: Path_XCOM2Mods: %s " % cfg.mod_paths['XCOM2Mods'])
print(":: Path_WOTCMods: %s " % cfg.mod_paths['WOTCMods'])
print(":: Path_SteamMods: %s " % cfg.mod_paths['SteamMods'])

print(":: ModClassOverrides settings:")
print(":: :: CleanOverrides: %s" % cfg.CleanOverrides)
print(":: :: IncludeOverrides: %s" % cfg.IncludeOverrides)
print(":: :: ExcludeOverrides: %s" % cfg.ExcludeOverrides)
print(":: :: PromptForEach: %s" % cfg.PromptForEach)

print(":: XComModOptions settings:")
print(":: :: CleanActiveMods: %s " % cfg.CleanActiveMods)
print(":: :: CleanDefaultModOptions: %s " % cfg.CleanDefaultModOptions)
print(":: :: CleanXComModOptions: %s " % cfg.CleanXComModOptions)


class OverridesManager(object):
	xce = XComEngineIniHandler(XCE_FILE_PATH)
	xcmo = XComModOptionsIniHandler(XCMO_FILE_PATH)
	overrides_dict = {}
	found_overrides = []
	previous_overrides = []

	def __init__(self):
		self._find_overrides_in_mods_paths()
		self._check_for_duplicate_overrides()
		print("Found and Parsed ModClassOverrides: %s" % len(self.found_overrides))
		self._get_existing_overrides()

	@classmethod
	def find_inis_in_mods_path(cls, mods_path):
		engine_ini_paths = []
		if not mods_path:
			return []
		for root, dirs, files in os.walk(mods_path):
			for file_name in files:
				if file_name == "XComEngine.ini":
					file_path = os.path.join(root, file_name)
					engine_ini_paths.append(file_path)

		print("%s 'XComEngine.ini' files found in mods path: '%s'" % (len(engine_ini_paths), mods_path))
		for p in engine_ini_paths:
			print("Path: %s" % p)
		return engine_ini_paths

	def _get_existing_overrides(self):
		print(
			"Retrieving existing overrides from 'XComEngine.ini' in user config folder ('%s') for comparison."
			% XCE_FILE_PATH
		)
		self.previous_overrides = self.xce.get_overrides_from_file(self.xce.file_path)
		print("Previous Overrides in XComEngine.ini: %s" % len(self.previous_overrides))

	def _find_overrides_in_mods_paths(self):
		# Get file paths to all XComEngine.ini files in known mod paths (XCOM2, WotC, Steam, + Additionals)
		for mod_path, path in cfg.mod_paths.items():
			for ini_path in self.find_inis_in_mods_path(path):

				# Get ModClassOverride lines in found files
				overs = XComEngineIniHandler.get_overrides_from_file(ini_path)
				for found_override in overs:
					source_mod_name = found_override.source_mod_name
					if source_mod_name is not None and source_mod_name in self.xcmo.active_mods:
						self.found_overrides.append(found_override)
					else:
						print("Ignoring override from inactive Mod: %s" % source_mod_name)

	def _check_for_duplicate_overrides(self):
		# Parse the ModClassOverride lines so we can warn about duplicates
		for override in self.found_overrides:
			if override.base_class in self.overrides_dict:
				existing = self.overrides_dict[override.base_class]
				if override.mod_class == existing.mod_class:
					print(
						"\n\nWARNING: Duplicate ModClassOverride lines found! "
						"Possible mod conflict or maybe just a typo in one mod if both source files are the same.\n"
						"Lines:\n"
						"1: '%s' - Source File: '%s'\n"
						"2: '%s' - Source File: '%s'\n" % (
						existing, existing.source_file, override, override.source_file)
					)
				else:
					print(
						"\n\nWARNING: Multiple ModClassOverrides for the same BaseGameClass with different ModClasses! "
						"Probable mod conflict!\n"
						"Lines:\n"
						"1: '%s' - Source File: '%s'\n"
						"2: '%s' - Source File: '%s'\n" % (
						existing, existing.source_file, override, override.source_file)
					)
			self.overrides_dict[override.base_class] = override
		# TODO: Halt on duplicates?

	def _determine_overrides_to_add(self):
		new_overrides = self.found_overrides.copy()
		if self.previous_overrides:
			new_overrides = list(set(self.found_overrides) - set(self.previous_overrides))
		return new_overrides

	def _determine_overrides_to_remove(self):
		removed_overrides = []
		if self.previous_overrides:
			removed_overrides = list(set(self.previous_overrides) - set(self.found_overrides))
		return removed_overrides

	def _determine_if_changes_needed(self):
		change_needed = False
		new_overrides = self._determine_overrides_to_add()
		for new_override in new_overrides:
			print("Will add: %s - Source File: %s" % (new_override, new_override.source_file))

		removed_overrides = self._determine_overrides_to_remove()
		for removed_override in removed_overrides:
			print("Will remove: %s - Source File: %s" % (removed_override, removed_override.source_file))

		if new_overrides or removed_overrides:
			change_needed = True

		return change_needed

	def process_overrides_and_write_config(self):
		if not cfg.CleanOverrides:
			print("== Skipping cleanup of ModClassOverrides due to configuration (CleanOverrides is False)")
			return

		if self._determine_if_changes_needed():
			print("==== Changes needed - Proceeding")

			print("== Updating overrides in 'XComEngine.ini' in user config folder ('%s')" % XCE_FILE_PATH)
			text = self.xce.get_text()
			if self.found_overrides:
				clean_text = IniTextProcessor.replace_old_overrides(text, self.found_overrides)
			else:
				# No new overrides to add, just clean up instead
				clean_text = IniTextProcessor.clean_out_all_overrides(text)

			print("== Doing cleanup of 'XComEngine.ini' in user config folder ('%s')" % XCE_FILE_PATH)
			clean_text = IniTextProcessor.repair_config_text(clean_text)

			self.xce.write_text(clean_text)

		else:
			print("==== No Changes needed - Not modifying XComEngine.ini!")

	def process_mod_options(self):
		if cfg.CleanActiveMods:
			print("== Doing cleanup of 'XComModOptions.ini' in user config folder ('%s')" % XCE_FILE_PATH)
			self.xcmo.repair_active_mods()

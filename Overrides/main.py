import os
import re
import shutil

from Overrides import ModClassOverride
from Overrides.constants import CFG_SECTION, re_mco_add, re_mco_ml, re_xce_engine, re_mco, re_mco_nonl
from Overrides.utils import get_platform_specific_xce_path, setup_logging, load_manager_config


setup_logging()
manager_config = load_manager_config()

IS_WOTC = manager_config.getboolean(CFG_SECTION, "WOTC")
XCE_FILE_NAME = "XComEngine.ini"
XCE_FILE_NAME_BAK = XCE_FILE_NAME+".bak"
XCOM2_CONF_PATH = get_platform_specific_xce_path(wotc=IS_WOTC)
XCE_FILE_PATH = os.path.expanduser('~') + XCOM2_CONF_PATH + XCE_FILE_NAME
XCE_FILE_PATH_BAK = os.path.expanduser('~') + XCOM2_CONF_PATH + XCE_FILE_NAME_BAK

XCE_FILE_PATH = XCE_FILE_NAME
XCE_FILE_PATH_BAK = XCE_FILE_NAME_BAK

print("Debug: XComEngine.ini absolute path: '%s'" % XCE_FILE_PATH)

# TODO: Read these paths from XCE?
"""
[Engine.DownloadableContentEnumerator]
ModRootDirs=W:\Games\Steam\steamapps\common\XCOM 2\XComGame\Mods\
ModRootDirs=W:\Games\Steam\steamapps\common\XCOM 2\XCom2-WarOfTheChosen\XComGame\Mods\
ModRootDirs=W:\Games\Steam\steamapps\workshop\content\268500\
"""
Path_XCOM2Mods = manager_config[CFG_SECTION]["XCOM2Mods"]  # "W:\Games\Steam\steamapps\common\XCOM 2\XComGame\Mods"
Path_WOTCMods = manager_config[CFG_SECTION]["WOTCMods"]  # "W:\Games\Steam\steamapps\common\XCOM 2\XCom2-WarOfTheChosen\XComGame\Mods"
Path_SteamMods = manager_config[CFG_SECTION]["SteamMods"]  # "W:\Games\Steam\steamapps\workshop\content\268500"
# AdditionalModsPath1
# AdditionalModsPath2
# AdditionalModsPath3
# AdditionalModsPath4

MOD_PATHS = [
	Path_XCOM2Mods, Path_SteamMods,
	# AdditionalModsPath1, AdditionalModsPath2, AdditionalModsPath2, AdditionalModsPath3, AdditionalModsPath4
]
if IS_WOTC:
	MOD_PATHS.append(Path_WOTCMods)


def get_overrides_from_file(file_path):
	# print("==== Getting overrides from file: %s" % file_path)
	overrides = []
	with open(file_path, "r") as file:
		lines = file.readlines()
		for line in lines:
			if not line or line.startswith(';'):  # Ignore blanks and commented lines
				continue
			match = re.search(re_mco_add, line)
			if match:
				if len(match.groups()) > 1:
					raise Exception("Multiple matches for a single line - Badly formatted ini file: %s" % file_path)
				overrides.append(ModClassOverride.from_raw_line(line.rstrip(), source_file=file_path))
	return overrides


def find_inis_in_mods_path(mods_path):
	engine_ini_paths = []
	if not mods_path:
		return []
	for root, dirs, files in os.walk(mods_path):
		for file_name in files:
			if file_name == "XComEngine.ini":
				file_path = os.path.join(root, file_name)
				engine_ini_paths.append(file_path)

	print("%s 'XComEngine.ini' files found in mods path: '%s'" % (len(engine_ini_paths), mod_path))
	for p in engine_ini_paths:
		print("Path: %s" % p)
	return engine_ini_paths


def get_xce_text():
	with open(XCE_FILE_PATH, "r") as input_file:
		return input_file.read()


def write_xce_text(new_text):
	with open(XCE_FILE_PATH, "w") as output_file:
		return output_file.write(new_text)


def get_existing_overrides(config_text):
	match = re.search(re_mco_ml, config_text)
	if match:
		return '\n'.join(match.groups())


def clean_out_all_overrides(config_text):
	any_mco = re.search(re_mco, config_text)
	if not any_mco:
		return config_text
	return re.sub(re_mco_ml, "\n\[", config_text)


def repair_config_text(config_text):
	# Cleanups
	# Multiple blank lines
	# config_text = re.sub('\n\n', '\n', config_text)

	text_lines = config_text.split('\n')
	repaired_lines = []
	for line in text_lines:

		# Find lines where a ModClassOverrides entry got appended to the end of a previous line instead of after a newline
		if "ModClassOverrides" in line:
			splits = line.split("ModClassOverrides")
			if splits[0] == '' or splits[0] == '+':  # Line started with ModClassOverrides, no repair needed
				repaired_lines.append(line)
				continue
			print("Found ModClassOverrides line that didn't begin on its own line. Repairing: ", line)
			line = splits[0] + "\n" + "ModClassOverrides" + splits[1]

		repaired_lines.append(line)

	return '\n'.join(repaired_lines)


def replace_old_overrides(config_text, overrides_list):
	# overrides_text = '\n' + '\n'.join([str(o) for o in overrides_list])
	overrides_text = '\n'.join([str(o) for o in overrides_list])

	any_mco = re.search(re_mco, config_text)
	if any_mco:
		return re.sub(re_mco_ml, overrides_text + "\n\n[", config_text)
	return re.sub(re_xce_engine, r'\1' + overrides_text + "\n" + r'\2\3', text)


overrides_dict = {}
found_overrides = []

# Get file paths to all XComEngine.ini files in known mod paths (XCOM2, WotC, Steam, + Additionals)
for mod_path in MOD_PATHS:
	for ini_path in find_inis_in_mods_path(mod_path):
		# Get ModClassOverride lines in found files
		overs = get_overrides_from_file(ini_path)
		if overs:
			found_overrides.extend(overs)

# Parse the ModClassOverride lines so we can warn about duplicates
for override in found_overrides:
	if override.base_class in overrides_dict:
		existing = overrides_dict[override.base_class]
		if override.mod_class == existing.mod_class:
			print(
				"\n\nWARNING: Duplicate ModClassOverride lines found! " 
				"Possible mod conflict or maybe just a typo in one mod if both source files are the same.\n"
				"Lines:\n" 
				"1: '%s' - Source File: '%s'\n"
				"2: '%s' - Source File: '%s'\n" % (existing, existing.source_file, override, override.source_file)
			)
		else:
			print(
				"\n\nWARNING: Multiple ModClassOverrides for the same BaseGameClass with different ModClasses! " 
				"Probable mod conflict!\n"
				"Lines:\n"
				"1: '%s' - Source File: '%s'\n"
				"2: '%s' - Source File: '%s'\n" % (existing, existing.source_file, override, override.source_file)
			)
	overrides_dict[override.base_class] = override
	# TODO: Halt on duplicates?

print("Retrieving existing overrides from 'XComEngine.ini' in user config folder ('%s') for comparison." % XCE_FILE_PATH)
previous_overrides = get_overrides_from_file(XCE_FILE_PATH)

new_overrides = None
removed_overrides = None

print("Found and Parsed ModClassOverrides: %s" % len(found_overrides))
if found_overrides:
	new_overrides = found_overrides.copy()
	if previous_overrides:
		print("Previous Overrides in XComEngine.ini: %s" % len(previous_overrides))
		new_overrides = list(set(found_overrides) - set(previous_overrides))
		removed_overrides = list(set(previous_overrides) - set(found_overrides))

		print("Net-new Overrides to be added: %s" % len(new_overrides))
		print("Missing overrides to be removed: %s" % len(removed_overrides))

		for removed_override in removed_overrides:
			print("Will remove: %s - Source File: %s" % (removed_override, removed_override.source_file))

	for new_override in new_overrides:
		print("Will add: %s - Source File: %s" % (new_override, new_override.source_file))

# New ones to add -> Rebuild list, Replace
# Old ones to remove -> Rebuild list, Replace
# No current ones found, Previous ones found -> Rewrite XCE without MCO
# No current ones found, no previous found -> Do nothing

change_needed = False
if new_overrides or removed_overrides:
	change_needed = True

if change_needed:
	print("==== Changes needed - Proceeding")
	print("== Backing up existing '%s' to '%s'" % (XCE_FILE_NAME, XCE_FILE_PATH_BAK))
	shutil.copy(XCE_FILE_PATH, XCE_FILE_PATH_BAK)

	print("== Updating overrides in 'XComEngine.ini' in user config folder ('%s')" % XCE_FILE_PATH)
	text = get_xce_text()
	if found_overrides:
		clean_text = replace_old_overrides(text, found_overrides)
	else:
		# No new overrides to add, just clean up instead
		clean_text = clean_out_all_overrides(text)

	print("== Doing cleanup of 'XComEngine.ini' in user config folder ('%s')" % XCE_FILE_PATH)
	clean_text = repair_config_text(clean_text)

	print("== Writing changes to 'XComEngine.ini' in user config folder ('%s')" % XCE_FILE_PATH)
	write_xce_text(clean_text)
else:
	print("==== No Changes needed - Not modifying XComEngine.ini!")

input("\n\nFinished! Press Enter to close this window...\n")



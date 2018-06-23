import os
import re
import shutil

from Overrides import ModClassOverride
from Overrides.constants import DEFAULT_CFG_FILE_NAME, CFG_FILE_NAME, CFG_SECTION, re_mco_add, re_mco_ml
from Overrides.utils import get_platform_specific_xce_path, setup_logging, load_manager_config


setup_logging()
manager_config = load_manager_config()

IS_WOTC = manager_config.getboolean(CFG_SECTION, "WOTC")
XCE_FILE_NAME = "XComEngine.ini"
XCE_FILE_NAME_BAK = XCE_FILE_NAME+".bak"
XCOM2_CONF_PATH = get_platform_specific_xce_path(wotc=IS_WOTC)
XCE_FILE_PATH = os.path.expanduser('~') + XCOM2_CONF_PATH + XCE_FILE_NAME
XCE_FILE_PATH_BAK = os.path.expanduser('~') + XCOM2_CONF_PATH + XCE_FILE_NAME_BAK

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


def get_existing_overrides(text):
	match = re.search(re_mco_ml, text)
	if match:
		print("============ Match =======")
		# for g in match.groups(): print(g)
		return '\n'.join(match.groups())


def replace_old_overrides(text, repl=""):
	repl = repl + "\n\n[" if repl else "\n["
	return re.sub(re_mco_ml, repl, text)


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
print("Found %s ModClassOverrides: " % len(found_overrides))
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
new_overrides = list(set(found_overrides) - set(previous_overrides))
removed_overrides = list(set(previous_overrides) - set(found_overrides))
if new_overrides:
	print("\nNew overrides found:")
	for new_override in new_overrides:
		print("%s - Source File: %s" % (new_override, new_override.source_file))

if removed_overrides:
	print("\nMissing Overrides removed:")
	for removed_override in removed_overrides:
		print("%s - Source File: %s" % (removed_override, removed_override.source_file))

if (new_overrides or removed_overrides):
	print("==== Changes needed - Proceeding")
	print("== Backing up existing '%s' to '%s'" % (XCE_FILE_NAME, XCE_FILE_PATH_BAK))
	shutil.copy(XCE_FILE_PATH, XCE_FILE_PATH_BAK)

	print("== Cleaning & Updating overrides in 'XComEngine.ini' in user config folder ('%s')" % XCE_FILE_PATH)
	text = get_xce_text()
	clean_text = replace_old_overrides(text, repl='\n'.join([str(o) for o in found_overrides]))

	print("== Writing changes to 'XComEngine.ini' in user config folder ('%s')" % XCE_FILE_PATH)
	write_xce_text(clean_text)

input("\n\nFinished! Press Enter to close this window...\n")



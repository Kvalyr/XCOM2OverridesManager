import configparser
import platform
import os
import re


CFG_FILE_NAME = "config.ini"
CFG_SECTION = "XCOM2OverridesManager"

CFG_DEFAULT_UI = 'False'
CFG_DEFAULT_WOTC = 'True'
CFG_DEFAULT_DryRun = 'False'

CFG_DEFAULT_XCOM2Dir = 'C:\Program Files\Steam\steamapps\common\XCOM 2\\'
CFG_DEFAULT_XCOM2Mods = 'C:\Program Files\Steam\steamapps\common\XCOM 2\XComGame\Mods\\'
CFG_DEFAULT_WOTCMods = 'C:\Program Files\Steam\steamapps\common\XCOM 2\XCom2 - WarOfTheChosen\XComGame\Mods\\'
CFG_DEFAULT_SteamMods = 'C:\Program Files\Steam\steamapps\workshop\content\\268500\\'

Platform = platform.system()
IS_WINDOWS = Platform == "Windows"
IS_MACOS = Platform == "Darwin"
IS_LINUX = Platform == "Linux"


def _fix_path_ending(path):
    if not path:
        return
    path_ending = "\\" if IS_WINDOWS else "/"
    if not path.endswith(path_ending):
        return path + path_ending
    return path


def _parse_list_from_ini_string(string_from_ini):
    if not string_from_ini:
        return []
    return re.split("\,*\s*", string_from_ini)


def _parse_overrides_filter(string_from_ini):
    elems = dict()
    if not string_from_ini:
        return elems
    override_strings = _parse_list_from_ini_string(string_from_ini)
    for o in override_strings:
        override_parts = re.split("::+?", o)
        print("override_parts", override_parts)
        if len(override_parts) < 2:
            raise ValueError(
                "Badly formatted override filter. " 
                "Should be of form: 'BaseClass::ModClass', with multiple overrides separated by commas"
            )

        base_class = override_parts[0]
        mod_class = override_parts[1]
        base_class_list = elems.get(base_class, [])
        base_class_list.append(mod_class)
        elems[base_class] = base_class_list
    return elems


# Load config for this script
inicfg = configparser.ConfigParser()
inicfg[CFG_SECTION] = {}

if not inicfg.read(CFG_FILE_NAME):
    print("config.ini missing! Should be in same folder as this program. Current working dir: %s\n\n" % os.getcwd())

UseUI = inicfg.getboolean(CFG_SECTION, "UseUI", fallback=CFG_DEFAULT_WOTC)
WOTC = inicfg.getboolean(CFG_SECTION, "WOTC", fallback=CFG_DEFAULT_WOTC)
DryRun = inicfg.getboolean(CFG_SECTION, "DryRun", fallback=CFG_DEFAULT_DryRun)

XCOM2Dir = _fix_path_ending(inicfg.get(CFG_SECTION, "XCOM2Dir", fallback=CFG_DEFAULT_XCOM2Dir))
Path_XCOM2Mods = _fix_path_ending(inicfg.get(CFG_SECTION, "XCOM2Mods", fallback=CFG_DEFAULT_XCOM2Mods))
Path_WOTCMods = _fix_path_ending(inicfg.get(CFG_SECTION, "WOTCMods", fallback=CFG_DEFAULT_WOTCMods))
Path_SteamMods = _fix_path_ending(inicfg.get(CFG_SECTION, "SteamMods", fallback=CFG_DEFAULT_SteamMods))

FixModPaths = inicfg.getboolean(CFG_SECTION, "FixModPaths", fallback=True)
RemoveIniVersion = inicfg.getboolean(CFG_SECTION, "RemoveIniVersion", fallback=False)
RemoveIniVersionAllFiles = inicfg.getboolean(CFG_SECTION, "RemoveIniVersionAllFiles", fallback=False)


# TODO: Read these paths from XCE?
"""
    [Engine.DownloadableContentEnumerator]
    ModRootDirs=W:\Games\Steam\steamapps\common\XCOM 2\XComGame\Mods\
    ModRootDirs=W:\Games\Steam\steamapps\common\XCOM 2\XCom2-WarOfTheChosen\XComGame\Mods\
    ModRootDirs=W:\Games\Steam\steamapps\workshop\content\268500\
"""
mod_paths = dict(
    XCOM2Mods=Path_XCOM2Mods,
    SteamMods=Path_SteamMods,
    # AdditionalModsPath1, AdditionalModsPath2, AdditionalModsPath2, AdditionalModsPath3, AdditionalModsPath4
)
if WOTC:
    XCOM2Dir += "XCom2-WarOfTheChosen\\"
    mod_paths["WOTCMods"] = Path_WOTCMods


# Config for cleaning XComModOptions inis
# IncludeMods is probably a bad idea given the potential for messy interactions with the Launchers
# IncludeMods_str = inicfg.get("ModOptions", "IncludeMods", fallback=[])
# IncludeMods = _parse_list_from_ini_string(IncludeMods_str)
ExcludeMods_Str = inicfg.get("ModOptions", "ExcludeMods", fallback=[])
ExcludeMods = _parse_list_from_ini_string(ExcludeMods_Str)
CleanActiveMods = inicfg.getboolean("ModOptions", "CleanActiveMods", fallback=True)
CleanXComModOptions = inicfg.getboolean("ModOptions", "CleanXComModOptions", fallback=True)
CleanDefaultModOptions = inicfg.getboolean("ModOptions", "CleanDefaultModOptions", fallback=True)

# Config for cleaning XComEngine.ini / ModClassOverrides
CleanOverrides = inicfg.getboolean("Overrides", "CleanOverrides", fallback=True)
IncludeOverrides_str = inicfg.get("Overrides", "IncludeOverrides", fallback=[])
ExcludeOverrides_str = inicfg.get("Overrides", "ExcludeOverrides", fallback=[])
PromptForEach = inicfg.getboolean("Overrides", "PromptForEach", fallback=True)
IncludeOverrides = _parse_overrides_filter(IncludeOverrides_str)
ExcludeOverrides = _parse_overrides_filter(ExcludeOverrides_str)

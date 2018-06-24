import configparser
import os

CFG_FILE_NAME = "config.ini"
CFG_SECTION = "XCOM2OverridesManager"

CFG_DEFAULT_WOTC = 'True'
CFG_DEFAULT_DryRun = 'False'

CFG_DEFAULT_XCOM2Mods = 'C:\Program Files\Steam\steamapps\common\XCOM 2\XComGame\Mods'
CFG_DEFAULT_WOTCMods = 'C:\Program Files\Steam\steamapps\common\XCOM 2\XCom2 - WarOfTheChosen\XComGame\Mods'
CFG_DEFAULT_SteamMods = 'C:\Program Files\Steam\steamapps\workshop\content\\268500'

"""
CFG_DEFAULT_CleanOverrides = 'True'
CFG_DEFAULT_PromptForEachOverride = 'False'
CFG_DEFAULT_IncludeOverrides = ''
CFG_DEFAULT_ExcludeOverrides = ''

CFG_DEFAULT_CleanActive = 'True'
CFG_DEFAULT_CleanXComModOptions = 'True'
CFG_DEFAULT_CleanDefaultModOptions = 'True'
"""

# Load config for this script
inicfg = configparser.ConfigParser()
inicfg['DEFAULT'] = {
    'WOTC': CFG_DEFAULT_WOTC,
    'DryRun': CFG_DEFAULT_DryRun,
    'XCOM2Mods': CFG_DEFAULT_XCOM2Mods,
    'WOTCMods': CFG_DEFAULT_WOTCMods,
    'SteamMods': CFG_DEFAULT_SteamMods,
}
"""
# TODO Do we need to set DEFAULT at all? 'fallback' kwarg probably covers it.
'CleanOverrides': CFG_DEFAULT_CleanOverrides,
'PromptForEach': CFG_DEFAULT_PromptForEachOverride,
'IncludeOverrides': CFG_DEFAULT_IncludeOverrides,
'ExcludeOverrides': CFG_DEFAULT_ExcludeOverrides,

'CleanActiveMods': CFG_DEFAULT_CleanActive,
'XComModOptions': CFG_DEFAULT_CleanXComModOptions,
'DefaultModOptions': CFG_DEFAULT_CleanDefaultModOptions,
"""
inicfg[CFG_SECTION] = {}

if not inicfg.read(CFG_FILE_NAME):
    print("config.ini missing! Should be in same folder as this program. Current working dir: %s\n\n" % os.getcwd())

WOTC = inicfg.getboolean(CFG_SECTION, "WOTC", fallback=CFG_DEFAULT_WOTC)
DryRun = inicfg.getboolean(CFG_SECTION, "DryRun", fallback=CFG_DEFAULT_DryRun)

Path_XCOM2Mods = inicfg[CFG_SECTION]["XCOM2Mods"]
Path_WOTCMods = inicfg[CFG_SECTION]["WOTCMods"]
Path_SteamMods = inicfg[CFG_SECTION]["SteamMods"]

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
    mod_paths["WOTCMods"] = Path_WOTCMods

# Config for cleaning XComEngine.ini / ModClassOverrides
CleanOverrides = inicfg.getboolean("Overrides", "CleanOverrides", fallback=True)
IncludeOverrides = inicfg.get("Overrides", "IncludeOverrides", fallback=[])
ExcludeOverrides = inicfg.get("Overrides", "ExcludeOverrides", fallback=[])
PromptForEach = inicfg.getboolean("Overrides", "PromptForEach", fallback=True)

# Config for cleaning XComModOptions inis
CleanActiveMods = inicfg.getboolean("ModOptions", "CleanActiveMods", fallback=True)
CleanXComModOptions = inicfg.getboolean("ModOptions", "CleanXComModOptions", fallback=True)
CleanDefaultModOptions = inicfg.getboolean("ModOptions", "CleanDefaultModOptions", fallback=True)

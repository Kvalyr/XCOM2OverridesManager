import os

from Overrides import cfg
from Overrides.constants import XCE_FILE_NAME, XCMO_FILE_NAME
from Overrides.ini import XComEngineIniHandler, XComModOptionsIniHandler, DefaultModOptionsIniHandler
from Overrides.text_processor import IniTextProcessor
from Overrides.utils import get_input

XCOM2_GAME_PATH = cfg.XCOM2Dir
XCOM2_CONF_PATH = XComEngineIniHandler.get_platform_specific_config_path()
XCE_FILE_PATH = os.path.expanduser('~') + XCOM2_CONF_PATH + XCE_FILE_NAME
XCMO_FILE_PATH = os.path.expanduser('~') + XCOM2_CONF_PATH + XCMO_FILE_NAME

# TODO Move this
print("Debug: XComEngine.ini absolute path: '%s'" % XCE_FILE_PATH)
print("Configuration: ")
print(":: UseUI: %s " % cfg.UseUI)
print(":: WOTC: %s " % cfg.WOTC)
print(":: DryRun: %s " % cfg.DryRun)
print(":: FixModPaths: %s " % cfg.FixModPaths)
print(":: RemoveIniVersion: %s " % cfg.RemoveIniVersion)
print(":: XCom2Dir: %s " % cfg.XCOM2Dir)
print(":: Path_XCOM2Mods: %s " % cfg.mod_paths['XCOM2Mods'])
print(":: Path_WOTCMods: %s " % cfg.mod_paths['WOTCMods'])
print(":: Path_SteamMods: %s " % cfg.mod_paths['SteamMods'])

print(":: XComModOptions settings:")
# print(":: IncludeMods: %s " % cfg.IncludeMods)
print(":: ExcludeMods: %s " % cfg.ExcludeMods)
print(":: :: CleanActiveMods: %s " % cfg.CleanActiveMods)
print(":: :: CleanDefaultModOptions: %s " % cfg.CleanDefaultModOptions)
print(":: :: CleanXComModOptions: %s " % cfg.CleanXComModOptions)

print(":: ModClassOverrides settings:")
print(":: :: CleanOverrides: %s" % cfg.CleanOverrides)
print(":: :: IncludeOverrides: %s" % cfg.IncludeOverrides)
print(":: :: ExcludeOverrides: %s" % cfg.ExcludeOverrides)
print(":: :: PromptForEach: %s" % cfg.PromptForEach)


class OverridesManager(object):
    dmo = DefaultModOptionsIniHandler()
    xcmo = XComModOptionsIniHandler(XCMO_FILE_PATH)
    xce = XComEngineIniHandler(XCE_FILE_PATH)
    overrides_dict = {}
    found_overrides = []
    previous_overrides = []

    def __init__(self):
        if cfg.CleanOverrides:
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
        # for p in engine_ini_paths:
        #    print("Path: %s" % p)
        return engine_ini_paths

    def _get_existing_overrides(self):
        print(
            "Retrieving existing overrides from 'XComEngine.ini' in user config folder ('%s') for comparison."
            % XCE_FILE_PATH
        )
        self.previous_overrides = self.xce.get_overrides_from_file(self.xce.file_path)
        print("Previous Overrides in XComEngine.ini: %s" % len(self.previous_overrides))

    def _should_add_override(self, override):
        source_mod_name = override.source_mod_name

        print(self.xcmo.active_mods)

        # Check Include/Exclude Mods
        if source_mod_name is None or source_mod_name not in self.xcmo.active_mods:
            reason = "inactive" if source_mod_name not in cfg.ExcludeMods else "excluded"
            print("Ignoring override from %s Mod: %s : %s" % (reason, source_mod_name, override))
            return False

        # Check Include/Exclude Overrides
        if len(cfg.IncludeOverrides.keys()):  # If there are any IncludeOverrides, allow ONLY those overrides
            includes = cfg.IncludeOverrides.get(override.base_class)
            if not includes or override.mod_class not in includes:
                print("Override not in IncludeOverrides %s" % override)
                return False
        else:
            excludes = cfg.ExcludeOverrides.get(override.base_class)
            if excludes and override.mod_class in excludes:
                print("Excluding Override found in ExcludeOverrides %s" % override)
                return False

        if cfg.PromptForEach and not cfg.UseUI:
            p = get_input(
                "\nFound Override: %s : source_file=%s, mod_name=%s \n"
                "Do you want to add this override? Y/n   "
                "(Set 'PromptForEach' to False in config.ini to disable this prompt)  "
                % (override, override.source_file, override.source_mod_name)
            )
            if p.upper() in ("N", "NO"):
                print("Ignoring override due to answer (%s) at prompt: %s\n\n" % (p, override))
                return False
        return True

    def _add_override(self, override):
        if self._should_add_override(override):
            self.found_overrides.append(override)

    def _find_overrides_in_mods_paths(self):
        # Get file paths to all XComEngine.ini files in known mod paths (XCOM2, WotC, Steam, + Additionals)
        for mod_path, path in cfg.mod_paths.items():
            for ini_path in self.find_inis_in_mods_path(path):
                # Get ModClassOverride lines in found files
                overs = XComEngineIniHandler.get_overrides_from_file(ini_path)
                for found_override in overs:
                    self._add_override(found_override)

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
                        "2: '%s' - Source File: '%s'\n"
                        % (existing, existing.source_file, override, override.source_file)
                    )
                else:
                    print(
                        "\n\nWARNING: Multiple ModClassOverrides for the same BaseGameClass with different ModClasses! "
                        "Probable mod conflict!\n"
                        "Lines:\n"
                        "1: '%s' - Source File: '%s'\n"
                        "2: '%s' - Source File: '%s'\n"
                        % (existing, existing.source_file, override, override.source_file)
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

    def process_engine(self):
        # TODO: Clean up this function
        if self._determine_if_changes_needed():
            print("\n\n==== Changes needed - Proceeding")
            new_text = self.xce.get_text_from_file()
            if cfg.CleanOverrides:
                print("== Updating overrides in 'XComEngine.ini' in user config folder ('%s')" % self.xce.file_path)
                if self.found_overrides:
                    new_text = IniTextProcessor.replace_old_overrides(new_text, self.found_overrides)
                else:
                    # No new overrides to add, just clean up instead
                    new_text = IniTextProcessor.clean_out_all_overrides(new_text)

                self.xce.write_text(new_text, "ModClassOverrides")
            else:
                print("\n==== Skipping cleanup of ModClassOverrides due to configuration (CleanOverrides is False)")
        else:
            print("\n\n==== No ModClassOverrides Changes needed - Not modifying XComEngine.ini!")

        self.xce.repair_mod_paths()

        # TODO: This should probably be done to all files in Config, not just XCE / XCMO / DMO, etc
        self.xce.remove_ini_version()
        self.xce.repair()

    def process_mod_options(self):
        if cfg.CleanActiveMods:
            if cfg.CleanXComModOptions:
                print("\n==== Doing cleanup of 'XComModOptions.ini' in user config folder ('%s')" % self.xcmo.file_path)
                self.xcmo.repair_active_mods()
                self.xcmo.remove_ini_version()
                self.xcmo.repair()

            if cfg.CleanDefaultModOptions:
                print("\n==== Doing cleanup of 'DefaultModOptions.ini' in XCOM2 folder ('%s')" % self.dmo.file_path)
                self.dmo.repair_active_mods()
                self.dmo.remove_ini_version()
                self.dmo.repair()

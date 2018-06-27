from Overrides import cfg
from Overrides.text_processor import IniTextProcessor
from Overrides.utils import get_input, find_files_in_path


class OverridesManager(object):
    overrides_dict = {}
    found_overrides = []
    previous_overrides = []

    def __init__(self, xcmo, xce):
        self.xcmo = xcmo
        self.xce = xce
        if cfg.CleanOverrides:
            self._find_overrides_in_mods_paths()
            self._check_for_duplicate_overrides()
            print("Found and Parsed ModClassOverrides: %s" % len(self.found_overrides))
            self._get_existing_overrides()

    @classmethod
    def find_engine_inis_in_mods_path(cls, mods_path):
        engine_ini_paths = find_files_in_path(mods_path, specific_ini="XComEngine.ini")
        print("%s 'XComEngine.ini' files found in mods path: '%s'" % (len(engine_ini_paths), mods_path))
        return engine_ini_paths

    def _get_existing_overrides(self):
        print(
            "Retrieving existing overrides from 'XComEngine.ini' in user config folder ('%s') for comparison."
            % self.xce.file_path
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
        from Overrides.ini import XComEngineIniHandler
        # Get file paths to all XComEngine.ini files in known mod paths (XCOM2, WotC, Steam, + Additionals)
        for mod_path, path in cfg.mod_paths.items():
            for ini_path in self.find_engine_inis_in_mods_path(path):
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

    def do_processing(self):
        if not cfg.CleanOverrides:
            print("\n==== Skipping cleanup of ModClassOverrides due to configuration (CleanOverrides is False)")
            return

        # TODO: Clean up this function
        if not self._determine_if_changes_needed():
            print("\n\n==== No ModClassOverrides Changes needed!")
            return

        print("\n\n==== ModClassOverrides changes needed - Proceeding")
        new_text = self.xce.get_text_from_file()

        if self.found_overrides:
            print("== Updating overrides in 'XComEngine.ini' in user config folder ('%s')" % self.xce.file_path)
            new_text = IniTextProcessor.replace_old_overrides(new_text, self.found_overrides)
        else:
            print(
                "== No overrides found - Cleaning out all overrides in 'XComEngine.ini' in user config folder ('%s')"
                % self.xce.file_path
            )
            # No new overrides to add, just clean up instead
            new_text = IniTextProcessor.clean_out_all_overrides(new_text)

        self.xce.write_text(new_text, "ModClassOverrides")

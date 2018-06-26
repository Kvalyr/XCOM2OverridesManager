import re

from Overrides import cfg
from Overrides.constants import re_mco_add
from Overrides.mco import ModClassOverride
from Overrides.text_processor import IniTextProcessor

from .base import BaseIniHandler


class XComEngineIniHandler(BaseIniHandler):
    @classmethod
    def get_overrides_from_file(cls, file_path):
        # print("==== Getting overrides from file: %s" % file_path)
        ini_file = XComEngineIniHandler(file_path)
        ini_lines = ini_file.get_lines_from_file()

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

    def repair_mod_paths(self):
        if not cfg.FixModPaths:
            print(
                "\n==== Skipping cleanup of Mod paths in %s due to configuration (FixModPaths is False)"
                % self.file_path
            )
        # These regexes could probably be combined instead of doing fallback from one to another but Python logic is
        # more readable than inscrutable regex patterns
        text = self.get_text_from_file()
        section_name = "Engine\.DownloadableContentEnumerator"
        match_to_use = IniTextProcessor.get_regex_for_ini_section(section_name)
        section_match = re.search(match_to_use, text)

        after_dlce = ""
        if not section_match:
            # If there's no section after [Engine.DownloadableContentEnumerator] then just match to EOF
            match_to_use = IniTextProcessor.get_regex_for_ini_section(section_name, until_eof=True)
        else:
            after_dlce = section_match.groups()[1]  # Reattach the stuff that came after this section (2nd match group)

        repl = "[Engine.DownloadableContentEnumerator]\n"
        for path_name, path in cfg.mod_paths.items():
            if not path:
                continue
            repl += "ModRootDirs=%s\n" % path
        repl += "\n" + after_dlce

        # Lambda for repl so that re.sub doesn't try to parse the slashes in Windows paths as escapes in the string
        new_text = re.sub(match_to_use, lambda x: repl, text)
        self.write_text(new_text, reason="FixModPaths")

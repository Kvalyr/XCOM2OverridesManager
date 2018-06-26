import re

from Overrides import cfg
from Overrides.constants import re_mco_add
from Overrides.mco import ModClassOverride

from .base import BaseIniHandler


def _fix_path_ending(path):
    if not path:
        return
    path_ending = "\\" if cfg.IS_WINDOWS else "/"
    if not path.endswith(path_ending):
        return path + path_ending
    return path


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

    @staticmethod
    def repair_mod_paths(text):
        # These regexes could probably be combined instead of doing fallback from one to another but Python logic is
        # more readable than inscrutable regex patterns

        re_dlc_enum_until_section = re.compile(
            r'(\[Engine\.DownloadableContentEnumerator\][\s\S]+?)(\[.+?\])',  # 1:(DLCE section)2:(next section label)
            flags=re.MULTILINE
        )
        match_to_use = re_dlc_enum_until_section
        section_match = re.search(match_to_use, text)

        after_dlce = ""
        if not section_match:
            # If there's no section after [Engine.DownloadableContentEnumerator] then just match to EOF
            re_dlc_enum_until_EOF = re.compile(
                r'(\[Engine\.DownloadableContentEnumerator\][\s\S]*)$',
                flags=re.MULTILINE
            )
            match_to_use = re_dlc_enum_until_EOF
        else:
            after_dlce = section_match.groups()[1]  # Reattach the stuff that came after this section (2nd match group)

        repl = "[Engine.DownloadableContentEnumerator]\n"
        for path_name, path in cfg.mod_paths.items():
            if not path:
                continue
            path = _fix_path_ending(path)
            repl += "ModRootDirs=%s\n" % path
        repl += "\n" + after_dlce

        # Lambda for repl so that re.sub doesn't try to parse the slashes in Windows paths as escapes in the string
        new_text = re.sub(match_to_use, lambda x: repl, text)
        return new_text

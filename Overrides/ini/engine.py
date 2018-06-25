import re

from Overrides.constants import re_mco_add
from Overrides.mco import ModClassOverride

from .base import BaseIniHandler


class XComEngineIniHandler(BaseIniHandler):
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

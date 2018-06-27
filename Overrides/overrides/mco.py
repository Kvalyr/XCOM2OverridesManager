import os
import re

re_mco_baseclass = re.compile('BaseGameClass=\"(.+?)\",?')
re_mco_modclass = re.compile('ModClass=\"(.+?)\"')

XME_FILE_NAME = "XComEditor.ini"


def get_parent_dir(directory):
    return os.path.dirname(directory)


class ModClassOverride(object):
    source_mod_name = None

    def __init__(self, base_class, mod_class, source_file):
        self.base_class = base_class
        self.mod_class = mod_class
        self.source_file = source_file
        self._determine_source_mod()

    def _determine_source_mod(self):
        src_upper = self.source_file.upper()
        if "MODS" not in src_upper and "WORKSHOP" not in src_upper:  # Ignore previous mods coming from processing XCE
            # print("Mods not in self.source_file %s" % self.source_file)
            return None
        mod_config_dir = get_parent_dir(self.source_file)
        mod_base_dir = get_parent_dir(mod_config_dir)
        mod_dir_contents = os.listdir(mod_base_dir)
        for elem in mod_dir_contents:
            parts = re.split(r'\.XCoMMod', elem, flags=re.IGNORECASE)
            if len(parts) > 1:
                self.source_mod_name = parts[0]
                break

        print("MCO %s source mod determined as: %s" % (self, self.source_mod_name))

    @classmethod
    def from_raw_line(cls, raw_line, source_file):
        print("\n\n== Parsing Override: %s -- File: %s" % (raw_line, source_file))
        base_class = re.search(re_mco_baseclass, raw_line).groups(0)[0]
        mod_class = re.search(re_mco_modclass, raw_line).groups(0)[0]
        return cls(base_class, mod_class, source_file)

    def __repr__(self):
        return "ModClassOverrides=(" + "BaseGameClass=\"%s\", ModClass=\"%s\")" % (self.base_class, self.mod_class)

    def __eq__(self, other):
        if not isinstance(other, ModClassOverride):
            return False
        if self.base_class != other.base_class or self.mod_class != other.mod_class:
            return False
        return True

    def __hash__(self):
        return hash(str(self))

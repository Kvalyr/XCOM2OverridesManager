import platform
import re
import shutil

from Overrides import cfg
from Overrides.constants import re_mco_add
from Overrides.mco import ModClassOverride


class BaseIniHandler(object):
    def __init__(self, file_path=None):
        self.file_path = file_path

    def get_text(self):
        with open(self.file_path, "r") as input_file:
            return input_file.read()

    def get_lines(self):
        with open(self.file_path, "r") as input_file:
            return input_file.readlines()

    def write_text(self, new_text):
        self.backup()
        if cfg.DryRun:
            print(
                "== Would write changes but dry_run mode is enabled. "
                "Set DryRun = False in config.ini to allow writing changes."
                "\nFile: %s\n" % self.file_path
            )
        else:
            with open(self.file_path, "w") as output_file:
                print("== Writing changes to ini file in user config folder: '%s'" % self.file_path)
                return output_file.write(new_text)

    def backup(self):
        bak_path = self.file_path + ".bak"
        if cfg.DryRun:
            print(
                "== Would backup file but dry_run mode is enabled. "
                "Set DryRun = False in config.ini to allow writing changes."
                "\nFile: %s\n" % bak_path
            )
        else:
            print("== Backing up existing '%s' to '%s'" % (self.file_path, bak_path))
            shutil.copy(self.file_path, bak_path)

    @classmethod
    def get_platform_specific_config_path(cls):
        wotc = cfg.WOTC
        xcom_vfs_dir_name = "XCOM2 War of the Chosen" if wotc else "XCOM2"

        if platform.system() == "Windows":
            path = "\Documents\my games\%s\XComGame\Config\\" % xcom_vfs_dir_name

        elif platform.system() == "Darwin":
            # TODO: Uncertain about these paths
            xcom_product_dir_name = "XCOM 2"
            if wotc:
                xcom_product_dir_name = "XCOM 2 WotC"

            path = "/Library/Application Support/Feral Interactive/%s/VFS/Local/my games/%s/XCOMGame/Config/" % (
                xcom_product_dir_name, xcom_vfs_dir_name
            )

        elif platform.system() == "Linux":
            # TODO: Uncertain about these paths
            xcom_product_dir_name = "XCOM 2"
            if wotc:
                xcom_product_dir_name = "XCOM 2 WotC"

            path = ".local/share/feral-interactive/%s/VFS/Local/my games/%s/XComGame/Config/" % (
                xcom_product_dir_name, xcom_vfs_dir_name
            )
        else:
            raise NotImplementedError("Unrecognized system OS/Platform")
        return path


class XComModOptionsIniHandler(BaseIniHandler):
    active_mods = []

    def __init__(self, file_path=None):
        super(XComModOptionsIniHandler, self).__init__(file_path=file_path)
        self._parse_active_mods()

    def _parse_active_mods(self):
        lines = self.get_lines()
        print("XComModOptionsInitHandler._parse_active_mods()", len(lines))
        if not lines[0].strip().startswith("[Engine.XComModOptions]"):
            raise ValueError(
                "Invalid XComModOptions.ini! %s\n"
                "Expected %s, got: %s" % (self.file_path, "[Engine.XComModOptions]", lines[0])
            )

        line_counter = 0
        for line in lines:
            line_counter += 1
            if line_counter < 2:  # Skip section head
                continue
            line = line.strip()
            if not line.startswith("ActiveMods="):  # Skip blanks etc
                continue
            parts = line.split("=")
            if len(parts) < 2:
                raise ValueError("Invalid XComModOptions.ini! Problem on line %s : %s" % (line_counter, line))
            self.active_mods.append(parts[1])
        self.active_mods = list(set(self.active_mods))

    def repair_active_mods(self):
        re_xmo = re.compile(r'\[Engine.XComModOptions\][\s\S]*\[', flags=re.MULTILINE)
        config_text = self.get_text()
        mod_lines = []

        for mod in self.active_mods:
            mod_lines.append("ActiveMods=%s" % mod)

        mods_text = '\n'.join(mod_lines)
        repl = "[Engine.XComModOptions]\n" + mods_text + "\n\n["
        config_text = re.sub(re_xmo, repl, config_text)

        self.write_text(config_text)


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

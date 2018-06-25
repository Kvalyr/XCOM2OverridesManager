import platform
import os
import re

from Overrides import cfg
from Overrides.constants import DMO_FILE_NAME

from .base import BaseIniHandler


class XComModOptionsIniHandler(BaseIniHandler):
    active_mods = []
    ready = False

    def __init__(self, file_path=None):
        super(XComModOptionsIniHandler, self).__init__(file_path=file_path)
        self._parse_active_mods()
        self.ready = True

    @staticmethod
    def _should_add_mod(mod_name):
        """
        # IncludeMods is probably a bad idea given the potential for messy interactions with the Launchers
        includes = cfg.IncludeMods
        if includes and mod_name in includes:  # If there are ANY IncludeMods, ONLY include those ones
            print("Including mod due to IncludeMods in config: %s" % mod_name)
            return False
        """
        excludes = cfg.ExcludeMods
        if excludes and mod_name in excludes:
            print("Excluding mod due to ExcludeMods in config: %s" % mod_name)
            return False
        return True

    def _add_mod(self, mod_name):
        if self._should_add_mod(mod_name):
            self.active_mods.append(mod_name)

    def _parse_active_mods(self):
        lines = self.get_lines()
        num_mods_found = 0
        if not lines[0].strip().startswith("[Engine.XComModOptions]"):
            raise ValueError(
                "Invalid %s !\nExpected %s, got: %s" % (self.file_path, "[Engine.XComModOptions]", lines[0])
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

            num_mods_found += 1
            mod_name = parts[1].strip('\"')

            self._add_mod(mod_name)

        self.active_mods = list(set(self.active_mods))
        print("Found %s unique & active mods (%s total) in %s" % (len(self.active_mods), num_mods_found, self.file_path))

    def repair_active_mods(self):
        if not self.ready:
            return
        re_xmo = re.compile(r'\[Engine.XComModOptions\][\s\S]*', flags=re.MULTILINE)
        config_text = self.get_text()
        mod_lines = []

        for mod in self.active_mods:
            mod_lines.append("ActiveMods=\"%s\"" % mod)

        mods_text = '\n'.join(mod_lines)
        repl = "[Engine.XComModOptions]\n" + mods_text + "\n\n"
        config_text = re.sub(re_xmo, repl, config_text)

        self.write_text(config_text)


class DefaultModOptionsIniHandler(XComModOptionsIniHandler):
    def __init__(self):
        base_game_path = cfg.XCOM2Dir
        if self.verify_game_path(base_game_path):
            dmo_file_path = os.path.join(cfg.XCOM2Dir, "XComGame\Config\\" + DMO_FILE_NAME)  # GameDir, not VFS
            super(DefaultModOptionsIniHandler, self).__init__(file_path=dmo_file_path)

    @staticmethod
    def verify_game_path(file_path):
        game_exe_subpath = ""

        # TODO: Other platforms
        if platform.system() == "Windows":
            game_exe_subpath = "Binaries\Win64\XCOM2.exe"

        path = os.path.join(file_path, game_exe_subpath)
        if not os.path.exists(path) and platform.system() == "Windows":  # TODO Remove windows check from this line
            print("Error: Invalid XCOM2Dir: %s" % file_path)
            return False

        return True

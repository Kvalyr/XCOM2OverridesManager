import datetime
import os
import sys

from Overrides import cfg
from Overrides.constants import LOG_FILE_NAME, MAX_LOG_SIZE


def get_input(*args, **kwargs):
    if not cfg.UseUI:
        return input(*args)
    else:
        # TODO: Hook into UI here to raise a dialog or similar if needed
        print("Skipping prompt due to UI Enabled")
        print(*args, **kwargs)
        return ""


class SplitOut(object):

    def write(self, *args, **kwargs):
        self.out1.write(*args, **kwargs)
        self.out2.write(*args, **kwargs)

    def __init__(self, out1, out2):
        self.out1 = out1
        self.out2 = out2

    def flush(*args, **kwargs):
        pass


def find_files_in_path(path, specific_ini=None, extension=None):
    file_paths = []
    if not path:
        return []
    for root, dirs, files in os.walk(path):
        for file_name in files:
            if (specific_ini and file_name != specific_ini) or (extension and not file_name.endswith(extension)):
                continue
            file_path = os.path.join(root, file_name)
            file_paths.append(file_path)
    return file_paths


# ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====
# Logging init below
# ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====

# Don't let the log file grow. Some kind of FIFO or log-rotation would be good, but not worth the added complexity.
try:
    log_size = os.path.getsize(os.path.abspath(LOG_FILE_NAME))
except FileNotFoundError:
    log_size = 0

too_big = log_size > MAX_LOG_SIZE
file_mode = "a"  # Append
if too_big:
    file_mode = "w"  # Blank the log file and start a new one

log_file = open(LOG_FILE_NAME, file_mode)
sys.stdout = SplitOut(log_file, sys.stdout)
print("-- XCOM2OverridesManager -- %s" % datetime.datetime.now())
print("====================================================================================================")
print("Configuration: ")
print(":: DryRun: %s " % cfg.DryRun)
print(":: WOTC: %s " % cfg.WOTC)
print(":: UseUI: %s " % cfg.UseUI)
print(":: RemoveIniVersion: %s " % cfg.RemoveIniVersion)
print(":: RemoveIniVersionAllFiles: %s " % cfg.RemoveIniVersionAllFiles)
print("====================================================================================================")
print("Paths: ")
print(":: XCom2Dir: %s " % cfg.XCOM2Dir)
print(":: Path_XCOM2Mods: %s " % cfg.mod_paths['XCOM2Mods'])
print(":: Path_WOTCMods: %s " % cfg.mod_paths['WOTCMods'])
print(":: Path_SteamMods: %s " % cfg.mod_paths['SteamMods'])
print("====================================================================================================")

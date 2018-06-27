import os

from Overrides import cfg
from Overrides import utils
from Overrides.constants import XCE_FILE_NAME, XCMO_FILE_NAME
from Overrides.ini import BaseIniHandler, XComEngineIniHandler, XComModOptionsIniHandler, DefaultModOptionsIniHandler
from Overrides.overrides import OverridesManager


XCOM2_GAME_PATH = cfg.XCOM2Dir
XCOM2_BASE_VFS_PATH = os.path.expanduser('~')  # TODO: Don't assume VFS/Libraries are in user dir
XCOM2_VFS_PATH = XComEngineIniHandler.get_platform_specific_config_path(XCOM2_BASE_VFS_PATH)
XCE_FILE_PATH = XCOM2_VFS_PATH + XCE_FILE_NAME
XCMO_FILE_PATH = XCOM2_VFS_PATH + XCMO_FILE_NAME

# TODO Move this




class XCOM2Tool(object):
    def __init__(self):
        self.dmo = DefaultModOptionsIniHandler()
        self.xcmo = XComModOptionsIniHandler(XCMO_FILE_PATH)
        self.xce = XComEngineIniHandler(XCE_FILE_PATH)
        self.overrides_mgr = OverridesManager(self.xcmo, self.xce)
        print("====================================================================================================")
        print("Debug: XComEngine.ini absolute path: '%s'" % self.xce.file_path)
        print("Debug: XComModOptions.ini absolute path: '%s'" % self.xcmo.file_path)
        print("Debug: DefaultModOptions.ini absolute path: '%s'" % self.dmo.file_path)
        print("====================================================================================================")

    @classmethod
    def remove_ini_version_all_files(cls):
        if not cfg.RemoveIniVersionAllFiles:
            print(
                "\n==== Skipping Removal of IniVersion from all found inis due to configuration " 
                "(RemoveIniVersionAllFiles is False)"
            )
            return
        ini_paths = utils.find_files_in_path(XCOM2_VFS_PATH, extension=".ini")
        for path in ini_paths:
            h = BaseIniHandler(path)
            h.remove_ini_version()
            h.repair()

    def process_engine(self):
        print("====================================================================================================")
        print("==== Processing XCOMEngine.ini")
        print(":: ModClassOverrides settings:")
        print(":: :: PromptForEach: %s" % cfg.PromptForEach)
        print(":: :: FixModPaths: %s" % cfg.FixModPaths)
        print(":: :: CleanOverrides: %s" % cfg.CleanOverrides)
        print(":: :: IncludeOverrides: %s" % cfg.IncludeOverrides)
        print(":: :: ExcludeOverrides: %s" % cfg.ExcludeOverrides)
        print("====================================================================================================")
        self.overrides_mgr.do_processing()
        self.xce.repair_mod_paths()
        # TODO: This should probably be done to all files in Config, not just XCE / XCMO / DMO, etc
        self.xce.remove_ini_version()
        self.xce.repair()

    def process_mod_options(self):
        print("====================================================================================================")
        print("==== Processing ModOptions files.")
        print(":: XComModOptions settings:")
        # print(":: IncludeMods: %s " % cfg.IncludeMods)
        print(":: ExcludeMods: %s " % cfg.ExcludeMods)
        print(":: :: CleanActiveMods: %s " % cfg.CleanActiveMods)
        print(":: :: CleanDefaultModOptions: %s " % cfg.CleanDefaultModOptions)
        print(":: :: CleanXComModOptions: %s " % cfg.CleanXComModOptions)
        print("====================================================================================================")
        if cfg.CleanActiveMods:
            if cfg.CleanXComModOptions:
                print("\n==== Doing cleanup of 'XComModOptions.ini' in user config folder ('%s')" % self.xcmo.file_path)
                self.xcmo.repair_active_mods()
                if not cfg.RemoveIniVersionAllFiles:
                    self.xcmo.remove_ini_version()
                    self.xcmo.repair()

            if cfg.CleanDefaultModOptions:
                print("\n==== Doing cleanup of 'DefaultModOptions.ini' in XCOM2 folder ('%s')" % self.dmo.file_path)
                self.dmo.repair_active_mods()
                if not cfg.RemoveIniVersionAllFiles:
                    self.dmo.remove_ini_version()
                    self.dmo.repair()
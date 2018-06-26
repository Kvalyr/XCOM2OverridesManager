import re
import shutil

from Overrides import cfg
from Overrides.text_processor import IniTextProcessor


class BaseIniHandler(object):
    def __init__(self, file_path=None):
        self.file_path = file_path

    def get_text_from_file(self):
        with open(self.file_path, "r") as input_file:
            return input_file.read()

    def get_lines_from_file(self):
        with open(self.file_path, "r") as input_file:
            return input_file.readlines()

    def write_text(self, new_text, reason=""):
        self.backup(reason=reason)
        if cfg.DryRun:
            print(
                "== Would write changes but dry_run mode is enabled. "
                "Set DryRun = False in config.ini to allow writing changes."
                "\nFile: %s\n" % self.file_path
            )
            return

        with open(self.file_path, "w") as output_file:
            print("== Writing changes to ini file: '%s'" % self.file_path)
            return output_file.write(new_text)

    def backup(self, reason=""):
        if reason:
            bak_path = self.file_path + "_" + reason + ".bak"
        else:
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

        if cfg.IS_WINDOWS:
            path = "\Documents\my games\%s\XComGame\Config\\" % xcom_vfs_dir_name

        elif cfg.IS_MACOS:
            # TODO: Uncertain about these paths
            xcom_product_dir_name = "XCOM 2"
            if wotc:
                xcom_product_dir_name = "XCOM 2 WotC"

            path = "/Library/Application Support/Feral Interactive/%s/VFS/Local/my games/%s/XCOMGame/Config/" % (
                xcom_product_dir_name, xcom_vfs_dir_name
            )

        elif cfg.IS_LINUX:
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

    def remove_ini_version(self):
        if not cfg.RemoveIniVersion:
            print(
                "\n==== Skipping cleanup of [IniVersion] in %s due to configuration (RemoveIniVersion is False)"
                % self.file_path
            )
        print("\n==== Removing [IniVersion] section from '%s'" % self.file_path)
        new_text = self.get_text_from_file()
        new_text = IniTextProcessor.remove_ini_version(new_text)
        self.write_text(new_text, reason="IniVersion")

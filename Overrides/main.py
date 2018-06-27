from Overrides import cfg
from Overrides.manager import XCOM2Tool


if __name__ == "__main__":
    manager = XCOM2Tool()
    if cfg.UseUI:
        pass
        # from Overrides.gui.gui import go
        # go()
    else:
        manager.process_engine()
        manager.process_mod_options()
        manager.remove_ini_version_all_files()

        input(
            "\n\nFinished! Open XCOM2OM.log in a text editor to see detailed results of what was done.\n"
            "\nPress Enter to close this window...\n"
        )

from Overrides.manager import OverridesManager

manager = OverridesManager()
manager.process_mod_options()
manager.process_overrides_and_write_config()

input(
    "\n\nFinished! Open XCOM2OM.log in a text editor to see detailed results of what was done.\n"
    "\nPress Enter to close this window...\n"
)

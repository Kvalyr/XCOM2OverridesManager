
from Overrides.manager import OverridesManager
from Overrides.utils import setup_logging

setup_logging()
manager = OverridesManager()
manager.process_overrides_and_write_config()
manager.process_mod_options()

input(
    "\n\nFinished! Open XCOM2OM.log in a text editor to see detailed results of what was done.\n"
    "\nPress Enter to close this window...\n"
)

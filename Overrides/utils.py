import configparser
import datetime
import os
import sys

from Overrides.constants import CFG_FILE_NAME, LOG_FILE_NAME, MAX_LOG_SIZE

CFG_DEFAULT_WOTC = 'True'
CFG_DEFAULT_XCOM2Mods = 'C:\Program Files\Steam\steamapps\common\XCOM 2\XComGame\Mods'
CFG_DEFAULT_WOTCMods = 'C:\Program Files\Steam\steamapps\common\XCOM 2\XCom2 - WarOfTheChosen\XComGame\Mods'
CFG_DEFAULT_SteamMods = 'C:\Program Files\Steam\steamapps\workshop\content\\268500'


class SplitOut(object):

	def write(self, *args, **kwargs):
		self.out1.write(*args, **kwargs)
		self.out2.write(*args, **kwargs)

	def __init__(self, out1, out2):
		self.out1 = out1
		self.out2 = out2

	def flush(*args, **kwargs):
		pass


def setup_logging():
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


def load_manager_config():
	# Load config for this script
	manager_config = configparser.ConfigParser()
	manager_config['DEFAULT'] = {
		'WOTC': CFG_DEFAULT_WOTC,
		'XCOM2Mods': CFG_DEFAULT_XCOM2Mods,
		'WOTCMods': CFG_DEFAULT_WOTCMods,
		'SteamMods': CFG_DEFAULT_SteamMods,
	}

	if not manager_config.read(CFG_FILE_NAME):
		print("config.ini missing! Should be in same folder as this program. Current working dir: %s" % os.getcwd())

	return manager_config

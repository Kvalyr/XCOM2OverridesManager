import datetime
import os
import platform
import sys

from Overrides.constants import LOG_FILE_NAME, MAX_LOG_SIZE


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


def get_platform_specific_xce_path(wotc=True):
	if platform.system() == "Windows":
		path = "\Documents\my games\XCOM2\XComGame\Config\\"
		if wotc:
			path = "\Documents\my games\XCOM2 War of the Chosen\XComGame\Config\\"

	elif platform.system() == "Darwin":
		# TODO: Uncertain about these paths
		path = "/Library/Application Support/Feral Interactive/XCOM 2/VFS/Local/my games/XCOM2/XCOMGame/Config/"
		if wotc:
			path = "/Library/Application Support/Feral Interactive/XCOM 2 WotC/VFS/Local/my games/XCOM2 War of the Chosen/XCOMGame/Config/"

	elif platform.system() == "Linux":
		# TODO: Uncertain about these paths
		path = ".local/share/feral-interactive/XCOM2/VFS/Local/my games/XCOM2/XComGame/SaveData/"
		if wotc:
			path = ".local/share/feral-interactive/XCOM 2 WotC/VFS/Local/my games/XCOM2 War of the Chosen/XComGame/SaveData/"
	else:
		raise NotImplementedError("Unrecognized system OS/Platform")
	return path
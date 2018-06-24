import re

CFG_FILE_NAME = "config.ini"
CFG_SECTION = "XCOM2OverridesManager"
LOG_FILE_NAME = "XCOM2OM.log"

# ENGINE_SECTION_NAME = "XComGame.XComEngine"
# MCO = "ModClassOverrides"
MAX_LOG_SIZE = 500 * 1000  # Bytes

re_mco = re.compile('ModClassOverrides[\s\S]*')
re_mco_add = re.compile('^\+?ModClassOverrides[\s\S]*')
re_mco_ml = re.compile('(\+*ModClassOverrides[\s\S]+?)\[', re.MULTILINE)

re_xce_engine = re.compile('(\[XComGame\.XComEngine\][\s\S]+?)([\s\n])(\[.*\])', re.MULTILINE)

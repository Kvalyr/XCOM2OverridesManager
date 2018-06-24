import re

LOG_FILE_NAME = "XCOM2OM.log"

XCE_FILE_NAME = "XComEngine.ini"
XCMO_FILE_NAME = "XComModOptions.ini"

# ENGINE_SECTION_NAME = "XComGame.XComEngine"
# MCO = "ModClassOverrides"
MAX_LOG_SIZE = 500 * 1000  # Bytes

re_mco = re.compile('ModClassOverrides[\s\S]*')
re_mco_add = re.compile('^\+?ModClassOverrides[\s\S]*')
re_mco_ml = re.compile('(\+*ModClassOverrides[\s\S]+?)\[', re.MULTILINE)

re_xce_engine = re.compile('(\[XComGame\.XComEngine\][\s\S]+?)([\s\n])(\[.*\])', re.MULTILINE)

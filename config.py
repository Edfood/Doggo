import configparser
from utils.log_conf import confLogger
import os
import sys

CONFIG_FILE_PATH = os.environ['CONFIG_FILE_PATH']
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
logger = confLogger(__name__)

if not os.path.exists(CONFIG_FILE_PATH):
    logger.error('config.ini doesn\'t exist.')
    sys.exit(-1)

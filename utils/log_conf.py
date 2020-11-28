# This module is for confLogger that is a function 
# to make easy to set up logger.

from logging import getLogger, config
import json

# Read config file for logging.
with open('utils/log_config.json', 'r') as f:
    log_conf = json.load(f)

config.dictConfig(log_conf)


def confLogger(name):
    """return configured logger.
    Parameter
    name: module name (use __name__)
    """
    logger = getLogger(name)
    return logger

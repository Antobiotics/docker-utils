import logging
import coloredlogs
coloredlogs.install(level='DEBUG')

def setup():
    logger = logging.getLogger('DOCKER UTILS')
    logger.setLevel(logging.DEBUG)
    return logger

LOGGER = setup()
INFO = LOGGER.info
WARN = LOGGER.warn
ERROR = LOGGER.error

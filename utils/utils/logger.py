import logging
import coloredlogs
coloredlogs.install(level='DEBUG')

FORMAT = "%(asctime)s - %(module)s - %(levelname)s - %(message)s"

def setup():
    logger = logging.getLogger('DOCKER UTILS')

    formatter = logging.Formatter(FORMAT)

    _h = logging.StreamHandler()
    _h.setFormatter(formatter)
    logger.addHandler(_h)

    logger.setLevel(logging.DEBUG)
    return logger

LOGGER = setup()
INFO = LOGGER.info
WARN = LOGGER.warn
ERROR = LOGGER.error

from logging import getLogger
from common.aggie_logging import init_loggers_from_config,LoggingConfig

init_loggers_from_config()

test = LoggingConfig()
# print(test)
logger = getLogger("commands")
logger.info("Logger initialized from config")
logger.debug("This is a debug message")
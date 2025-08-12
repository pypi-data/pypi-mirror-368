from superset_loggers import __version__
from superset_loggers import Logger

Logger = Logger()
logger = Logger.get_logger(verbose=True)
logger.info(f"Test logger version {__version__}")
print(Logger.LOG_FILE)

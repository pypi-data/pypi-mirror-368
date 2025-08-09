from superset_loggers import __version__
from superset_loggers import Logger

logger = Logger().get_logger(log_file='', verbose=True)
logger.info(f"Test logger version {__version__}")

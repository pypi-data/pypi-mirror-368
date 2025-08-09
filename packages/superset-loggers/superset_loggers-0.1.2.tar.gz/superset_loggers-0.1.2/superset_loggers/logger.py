import inspect
import os
import sys
import datetime
import logging

class Logger(object):
    """Custom Logger with file and console output support"""

    def __init__(self, filename=None):
        self.filename = filename or os.path.splitext(os.path.basename(sys.argv[0]))[0]
        self.log_file_default = (
            f"{os.path.basename(self.filename).split('.')[0]}_"
            f"{datetime.datetime.now().strftime('%Y_%m_%dT%H_%M_%S')}.log"
        )
        self.LOG_FILE = ""

    def get_logger(self, *, log_file: str = None, verbose: bool = False):
        """Create and configure logger instance
        
        Args:
            log_file (str, optional): Path to log file. Defaults to auto-generated name.
            verbose (bool, optional): Enable verbose logging with extra debug info. Defaults to False.
            
        Returns:
            logging.Logger: Configured logger instance
        """
        LOG_NAME = __name__

        if log_file is None:
            log_file = self.log_file_default

        if log_file != "":
            self.LOG_FILE = f"logs/{log_file}"
            # Create logs directory if it doesn't exist
            os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)
        else:
            self.LOG_FILE = ""

        if verbose:
            LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s Debug: %(name)s %(funcName)s %(lineno)d'
        else:
            LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'

        logging.basicConfig(
            encoding='utf-8',
            level=logging.ERROR,
            filename=self.LOG_FILE,
            filemode='a',
            format=LOG_FORMAT
        )

        # custom logger
        logger = logging.getLogger(LOG_NAME)
        log_formatter = logging.Formatter(LOG_FORMAT)

        # console output
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        stream_handler.setLevel(logging.CRITICAL)
        
        if log_file != '':
            logger.addHandler(stream_handler)

        logger.setLevel(logging.INFO)

        return logger

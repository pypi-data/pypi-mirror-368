from .logger import Logger
from importlib.metadata import version

__version__ = version("superset_loggers")
__all__ = ['Logger']

Logger = Logger

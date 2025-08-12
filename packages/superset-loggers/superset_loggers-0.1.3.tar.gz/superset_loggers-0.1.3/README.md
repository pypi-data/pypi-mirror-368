# Custom Logger Package

A simple customizable logger with both file and console output support.

## Installation

```bash
pip install superset-loggers
```

## Usage

```
from superset_loggers import Logger

logger = Logger().get_logger(log_file="app.log", verbose=True)
logger.info("This is an info message")
logger.error("This is an error message")
```

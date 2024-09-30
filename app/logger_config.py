import os
import sys
from loguru import logger

# Ensure log directories exist
log_dirs = ["logs/console", "logs/errors"]
for directory in log_dirs:
    os.makedirs(directory, exist_ok=True)

# Add log handlers
logger.add("logs/console/console.log", level="INFO", rotation="10 MB")
logger.add("logs/errors/errors.log", level="ERROR", rotation="10 MB")

def handle_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.opt(exception=(exc_type, exc_value, exc_traceback)).error("Uncaught exception:")

sys.excepthook = handle_exceptions

__all__ = ["logger"]

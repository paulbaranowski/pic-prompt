import logging
import sys
from typing import Optional


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: The name of the logger (typically __name__ from the calling module)
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
              Defaults to INFO if not specified.
    """
    # Create logger
    logger = logging.getLogger(name)

    # Only add handler if the logger doesn't have any handlers
    # and the root logger doesn't have any handlers
    if not logger.handlers and not logging.getLogger().handlers:
        # Create console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

    return logger


def disable_logging():
    """Disable all logging output"""
    # Disable root logger
    root = logging.getLogger()
    root.handlers = []
    root.setLevel(logging.CRITICAL + 100)
    root.propagate = False

    # Disable pic_prompt logger and all its children
    base_logger = logging.getLogger("pic_prompt")
    base_logger.handlers = []
    base_logger.setLevel(logging.CRITICAL + 100)
    base_logger.propagate = False

    # Disable all existing loggers
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.setLevel(logging.CRITICAL + 100)
        logger.propagate = False

    # Disable all future logging
    logging.disable(logging.CRITICAL)

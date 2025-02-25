import logging
import sys
from typing import Optional


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: The name of the logger (typically __name__ from the calling module)
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
              Defaults to INFO if not specified
    """
    # Create logger
    logger = logging.getLogger(name)

    # Set level
    log_level = getattr(logging, (level or "INFO").upper())
    logger.setLevel(log_level)

    # Create console handler with formatting
    if not logger.handlers:  # Only add handler if none exists
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

    return logger

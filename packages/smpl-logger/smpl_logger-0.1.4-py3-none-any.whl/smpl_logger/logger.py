import os
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

LOG_CONFIG = {
    "LOG_DIR": Path(os.environ.get("LOG_DIR", "logs")),
    "LEVEL": os.environ.get("LOG_LEVEL", "INFO"),
    "FORMAT": "%(asctime)s | %(name)s | [%(levelname)s] | %(message)s",
    "DATE_FORMAT": "%Y-%m-%d %H:%M:%S",
    "ROTATION_SIZE": int(os.environ.get("LOG_ROTATION_SIZE", 5 * 1024 * 1024)),  # 5 mb
    "BACKUP_COUNT": int(os.environ.get("LOG_BACKUP_COUNT", 3)),
    "ENCODING": "utf-8",
}

LOG_CONFIG["LOG_DIR"].mkdir(parents=True, exist_ok=True)


class ColoredFormatter(logging.Formatter):
    """Formatter with colored output for console"""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        formatted = super().format(record)

        record.levelname = levelname
        return formatted


def get_logger(
    name: str,
    log_file: str = None,
    level: str = None,
    rotation_size: int = None,
    backup_count: int = None,
) -> logging.Logger:
    """Creates and configures a logger.

    Args:
        name: Logger name. Using "root" configures the root logger.
        log_file: Log file name. If None, logs are written only to the console.
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            By default, uses the value from LOG_CONFIG["LEVEL"].
        rotation_size: Maximum log file size in bytes before rotation.
            By default, uses the value from LOG_CONFIG["ROTATION_SIZE"].
        backup_count: Number of backup files to keep during rotation.
            By default, uses the value from LOG_CONFIG["BACKUP_COUNT"].

    Returns:
        Configured Logger object with handlers for console and file (if specified).

    Notes:
        - Checks for existing handlers and does not add duplicates.
        - Console output is formatted with color highlighting for log levels.
        - File output (if specified) is configured with size-based rotation.
        - Disables propagation to parent loggers.
    """
    logger = logging.getLogger(name)
    level = level or LOG_CONFIG["LEVEL"]
    logger.setLevel(getattr(logging, level.upper()))

    # Check for an existing file handler with the specified file name
    def has_file_handler(logger, log_file):
        for handler in logger.handlers:
            if isinstance(
                handler, RotatingFileHandler
            ) and handler.baseFilename.endswith(log_file):
                return True
        return False

    # Add console handler if not present
    if not any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler)
        for h in logger.handlers
    ):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            ColoredFormatter(
                fmt=LOG_CONFIG["FORMAT"], datefmt=LOG_CONFIG["DATE_FORMAT"]
            )
        )
        logger.addHandler(console_handler)

    # Add file handler if specified and not present
    if log_file and not has_file_handler(logger, log_file):
        log_path = LOG_CONFIG["LOG_DIR"] / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=rotation_size or LOG_CONFIG["ROTATION_SIZE"],
            backupCount=backup_count or LOG_CONFIG["BACKUP_COUNT"],
            encoding=LOG_CONFIG["ENCODING"],
        )
        file_handler.setFormatter(
            logging.Formatter(
                fmt=LOG_CONFIG["FORMAT"], datefmt=LOG_CONFIG["DATE_FORMAT"]
            )
        )
        logger.addHandler(file_handler)

    # Disable propagation to parent loggers
    logger.propagate = False

    return logger

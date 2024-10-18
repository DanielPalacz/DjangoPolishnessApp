from __future__ import annotations

import logging
from inspect import currentframe
from os import getenv
from os.path import dirname


def configure_logger(logger_name: str) -> logging.Logger:
    """Configures logger.

    Uses env variable LOG_LEVEL_NAME:
     - CRITICAL = 50
     - FATAL = 50
     - ERROR = 40
     - WARNING = 30
     - INFO = 20
     - DEBUG = 10

    Args:
        logger_name: Logger name.

    Returns:
        Logger object.
    """
    log_level_matrix = {"CRITICAL": 50, "FATAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20, "DEBUG": 10}

    log_level_name = getenv("LOG_LEVEL_NAME") or "DEBUG"
    log_level_value = log_level_matrix[log_level_name]

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger_handler = logging.FileHandler(f"logs/{logger_name}.log")
    logger_handler.setLevel(log_level_value)
    logger_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)

    return logger


def get_static_dir() -> str:
    """Provides absolute path for static directory.

    Returns:
        The absolute path for static directory.
    """
    return dirname(__file__) + "/static/"


def parent_function_name() -> str:
    """Provides name of parent function.

    Returns:
        The name of parent function.
    """
    frame = currentframe().f_back
    return frame.f_code.co_name

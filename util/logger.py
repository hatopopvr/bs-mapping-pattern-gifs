import os
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import configparser


def setup_logger(module_name, config_path="configs/logging_config.ini"):
    """
    Set up a logger with the specified module name.
    The logger will have file handlers for both individual module logs and combined logs,
    and a console handler for console output.
    Log configurations, such as log level, log path, and backup count, are read from the
    specified config file.

    Args:
        module_name (str): The name of the module for which the logger is being set up.
        config_path (str, optional): The path to the logging configuration file.
                                     Defaults to "logging_config.ini".

    Returns:
        logging.Logger: The configured logger instance.
    """
    # Load configuration
    config = configparser.ConfigParser()
    config.read(config_path)
    log_level = config.get("logging", "level", fallback="INFO")
    log_path = config.get("logging", "log_path", fallback="logs")
    backup_count = config.getint("logging", "backup_count", fallback=7)

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.getLevelName(log_level))

    # Check if logger already has handlers, if so, remove them to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s')

    # FileHandler for individual module logs
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_filename = os.path.join(log_path, f'{module_name}_%Y-%m-%d.log')
    file_handler = TimedRotatingFileHandler(filename=time.strftime(
        log_filename), when='midnight', backupCount=backup_count)
    file_handler.setLevel(logging.getLevelName(log_level))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # ConsoleHandler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.getLevelName(log_level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

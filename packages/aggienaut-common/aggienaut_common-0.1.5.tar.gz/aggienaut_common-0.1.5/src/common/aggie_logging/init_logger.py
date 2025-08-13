"""Module for initializing a logger."""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from common.utils import from_root


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to add colors to log messages in the console.
    """
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[31m',   # Dark Red
        'CRITICAL': '\033[1;91m', # Bold Red
        'RESET': '\033[0m'     # Reset
    }

    def format(self, record):
        # Save the original format
        format_orig = self._style._fmt  #pylint: disable=protected-access

        # Add color codes if the level name is in our color dictionary
        if record.levelname in self.COLORS:
            colored_levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
            # Replace the levelname with the colored version in the format string
            self._style._fmt = format_orig.replace('%(levelname)s', colored_levelname)  #pylint: disable=protected-access

        # Format the record
        result = logging.Formatter.format(self, record)

        # Restore the original format
        self._style._fmt = format_orig  #pylint: disable=protected-access

        return result


class ExceptionLogger(logging.Logger):
    """
    Custom logger class that automatically includes exception information
    for logs at ERROR level and above.
    """
    def error(self, msg, *args, **kwargs):
        if 'exc_info' not in kwargs:
            kwargs['exc_info'] = True
        super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if 'exc_info' not in kwargs:
            kwargs['exc_info'] = True
        super().critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        # exception already sets exc_info=True by default
        super().exception(msg, *args, **kwargs)


def _convert_log_level(level):
    """
    Convert string log level to logging level constant.

    Args:
        level (int or str): Log level as string or int

    Returns:
        int: Logging level constant
    """
    if isinstance(level, str):
        return getattr(logging, level.upper())
    return level


def _setup_console_handler(console_level, log_format, use_colors):
    """
    Create and configure a console handler.

    Args:
        console_level (int): Console logging level
        log_format (str): Log message format
        use_colors (bool): Whether to use colors in console output

    Returns:
        logging.Handler: Configured console handler
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)

    # Use colored formatter if colors are enabled
    if use_colors and sys.stdout.isatty():  # Only use colors when in a terminal
        console_formatter = ColoredFormatter(log_format)
    else:
        console_formatter = logging.Formatter(log_format)

    console_handler.setFormatter(console_formatter)
    return console_handler


def _setup_file_handler(log_dir, logger_name, file_level, log_format, max_file_size, backup_count):  #pylint: disable=too-many-arguments, too-many-positional-arguments
    """
    Create and configure a rotating file handler.

    Args:
        log_dir (str): Directory for log files
        logger_name (str): Logger name
        file_level (int): File logging level
        log_format (str): Log message format
        max_file_size (int): Maximum size of each log file in bytes
        backup_count (int): Number of backup files to keep

    Returns:
        logging.Handler: Configured file handler
    """
    # Create directory for log file if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Use logger name for the log file name (sanitize it for file system)
    safe_name = "".join(c if c.isalnum() else "_" for c in logger_name)
    log_file = os.path.join(log_dir, f"{safe_name}.log")

    # Create and configure the rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    return file_handler


def init_logger(name=None, console_level: int|str = logging.INFO, log_format=None,    #pylint: disable=too-many-arguments, too-many-positional-arguments
                log_dir=None, file_level=None, max_file_size=10*1024*1024,
                backup_count=5, use_colors=True):
    """
    Initialize and configure a logger with file logging and colored console output.

    Args:
        name (str, optional): Logger name. If None, returns the root logger.
                             When file logging is enabled, this name is used for the log file.
        console_level (int or str, optional): Console logging level. Can be a logging level constant
                                     or a string ('DEBUG', 'INFO', etc.). Defaults to logging.INFO.
        log_format (str, optional): Log message format. Defaults to a standard format.
        log_dir (str, optional): Directory for log files. Defaults to "logs".
        file_level (int or str, optional): File logging level. If None, uses the same level as console.
        max_file_size (int, optional): Maximum size of each log file in bytes. Defaults to 10MB.
        backup_count (int, optional): Number of backup files to keep. Defaults to 5.
        use_colors (bool, optional): Whether to use colors in console output. Defaults to True.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Register our custom logger class
    logging.setLoggerClass(ExceptionLogger)

    # Convert log levels
    console_level = _convert_log_level(console_level)
    if file_level is not None:
        file_level = _convert_log_level(file_level)
    else:
        file_level = console_level

    # Use a default name if none provided
    logger_name = name if name else "root"
    logger = logging.getLogger(logger_name)

    # Set logging level to the minimum of console and file levels
    logger.setLevel(min(console_level, file_level))

    # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Set default format if none provided
    if log_format is None:
        log_format = '[%(asctime)s] [%(name)s] [%(levelname)s] [%(threadName)s] - %(message)s'

    # Add console handler
    console_handler = _setup_console_handler(console_level, log_format, use_colors)
    logger.addHandler(console_handler)

    # Set default log directory if none provided
    if log_dir is None:
        log_dir = from_root('logs')

    # Add file handler
    file_handler = _setup_file_handler(log_dir, logger_name, file_level, log_format,
                                      max_file_size, backup_count)
    logger.addHandler(file_handler)

    # Reset logger class to default after we've created our logger
    logging.setLoggerClass(logging.Logger)

    return logger

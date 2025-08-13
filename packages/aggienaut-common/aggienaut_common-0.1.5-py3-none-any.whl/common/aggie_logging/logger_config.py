"""Module containing functions for configuring loggers."""
from pathlib import Path
from typing import Any, Optional, Set, Union

from common.aggie_logging.init_logger import init_logger
from .configs import LoggingConfig

# Track initialized loggers to prevent duplicates
_initialized_loggers: Set[str] = set()

def parse_file_size(size: Union[int, str]) -> int:
    """
    Parse a human-readable file size string (e.g., '10MB', '100KB') into bytes.
    Accepts int (bytes) or string.
    """
    if isinstance(size, int):
        return size
    if isinstance(size, str):
        size = size.strip().upper()
        units = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
        for unit, factor in units.items():
            if size.endswith(unit):
                try:
                    return int(float(size[:-len(unit)].strip()) * factor)
                except ValueError:
                    raise ValueError(f"Invalid file size value: {size}")
        # If no unit, try to parse as int (bytes)
        try:
            return int(size)
        except ValueError:
            raise ValueError(f"Invalid file size value: {size}")
    raise TypeError(f"max_file_size must be int or str, got {type(size)}")

def setup_logger_from_config(key: str, log_config: dict[str, Any], base_path: Optional[Path] = None) -> None:
    """
    Set up a single logger based on configuration.

    Args:
        key: Logger name
        log_config: Logging configuration dictionary for this logger
        base_path: Base path for log files, defaults to parent directory of current file
    """
    # Skip if logger already initialized
    if key in _initialized_loggers:
        return


    console_level = log_config.get('console_level', 'INFO')
    file_level = log_config.get('file_level', console_level)
    max_file_size_raw = log_config.get('max_file_size', 10*1024*1024)
    max_file_size = parse_file_size(max_file_size_raw)
    backup_count = log_config.get('backup_count', 5)

    if base_path is None:
        base_path = Path(__file__).parent.parent
        log_dir = None  # Let init_logger use its default
    else:
        log_dir = str(base_path / 'logs')  # Use our custom path

    logger = init_logger(
        name=key,
        console_level=console_level,
        file_level=file_level,
        max_file_size=max_file_size,
        backup_count=backup_count,
        log_dir=log_dir  # Pass the log directory
    )

    # Mark logger as initialized
    _initialized_loggers.add(key)

    log_init_message = (f"Init logger '{key}' with arguments: console_level={console_level}, "
                        f"file_level={file_level}, "
                        f"max_file_size={max_file_size}, backup_count={backup_count}")
    logger.debug(log_init_message)

def process_logging_config(logging_config: LoggingConfig) -> None:
    """
    Process the centralized logging configuration and set up all loggers.

    Args:
        logging_config: LoggingConfig instance
    """
    if not logging_config:
        print("No logging configuration found")
        return

    force_system_log_settings = logging_config.force_system_log_settings
    system_log_config = logging_config.system

    if force_system_log_settings and system_log_config:
        print(f"Forcing system log settings: {system_log_config}")

    # Iterate over all logger configs defined as attributes (skip private and force_system_log_settings)
    for logger_name in logging_config.__annotations__:
        if logger_name in ("force_system_log_settings", "config_filename"):
            continue
        logger_config = logging_config[logger_name]
        if not isinstance(logger_config, dict):
            continue
        if force_system_log_settings and system_log_config:
            setup_logger_from_config(logger_name, system_log_config)
        else:
            setup_logger_from_config(logger_name, logger_config)

def init_loggers_from_config() -> None:
    """
    Initialize loggers from the main aggienaut configuration file using LoggingConfig.
    """
    try:
        logging_config = LoggingConfig()
        if logging_config:
            process_logging_config(logging_config)
        else:
            print("No logging config found")
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error loading logging config: {e}")

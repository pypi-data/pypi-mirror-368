
from dataclasses import dataclass
from typing import Optional
from common.config_framework.base_config import BaseConfig


@dataclass
class LoggerConfig:
    console_level: str = "debug"
    file_level: Optional[str] = None  # If None, defaults to console_level
    max_file_size: str | int = "10MB"
    max_backup_files: int = 5

class LoggingConfig(BaseConfig):
    config_filename = 'logging'
    force_system_log_settings: bool
    system: LoggerConfig  # System level logging
    config: LoggerConfig
    comms: LoggerConfig
    radio: LoggerConfig
    navigation: LoggerConfig
    power: LoggerConfig
    power_switchboard: LoggerConfig
    sunsaver: LoggerConfig
    science: LoggerConfig
    mqtt: LoggerConfig
    commands: LoggerConfig
    garmin_gps: LoggerConfig
    usb_manager: LoggerConfig


from common.config_framework.base_config import BaseConfig


class RadioConfig(BaseConfig):
    config_filename = 'hardware'
    section = 'radio'
    data_filename: str
    listen_timeout: float|int  # Seconds
    baud_rate: int
    port: str
    serial_timeout: float|int
    max_retries: int
    retry_delay: float|int  # Seconds
    poll_interval: float|int  # Seconds

from common.config_framework.base_config import BaseConfig

class ThreadConfig(BaseConfig):
    """
    Configuration for thread handling, including thread timeouts and exit events.
    """
    config_filename = 'threading'
    thread_timeout: int  # Default timeout for threads in seconds
    max_threads: int  # Maximum number of threads to manage

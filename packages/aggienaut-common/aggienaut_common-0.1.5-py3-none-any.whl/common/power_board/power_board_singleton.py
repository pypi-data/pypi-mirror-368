"""
Thread-safe singleton module for power board access management.

Provides the PowerBoardSingleton class that ensures only one PowerBoard instance
exists across the application, with thread-safe initialization and access patterns.
Manages the lifecycle of the PowerBoard instance and provides safe concurrent
access for multiple threads requiring power board operations.
"""

import threading
import logging
from typing import Optional
from .power_board import PowerBoard

class PowerBoardSingleton:
    """
    Thread-safe singleton for accessing the PowerBoard across multiple threads.
    """
    _instance: Optional[PowerBoard] = None
    _lock = threading.RLock()  # Reentrant lock for thread safety
    _initialized = False

    @classmethod
    def get_instance(cls) -> PowerBoard:
        """
        Get the singleton instance of PowerBoard.
        Initializes the board if it hasn't been initialized yet.

        Returns:
            PowerBoard: The singleton instance
        """
        with cls._lock:
            if not cls._instance:
                logging.getLogger("power").info("Initializing PowerBoard singleton")
                cls._instance = PowerBoard()
                cls._initialized = True
            return cls._instance

    @classmethod
    def is_initialized(cls) -> bool:
        """
        Check if the PowerBoard singleton has been initialized.

        Returns:
            bool: True if initialized, False otherwise
        """
        with cls._lock:
            return cls._initialized

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton instance (mainly for testing purposes).
        """
        with cls._lock:
            cls._instance = None
            cls._initialized = False

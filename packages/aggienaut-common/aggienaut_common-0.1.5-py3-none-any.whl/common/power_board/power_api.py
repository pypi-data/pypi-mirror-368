"""
Simple API for accessing the power board from any thread.
"""
import time
import logging
import threading
from typing import Optional, Callable

from common.thread_handling import safe_sleep
from common.enums import PowerBoardFuseTripAmps

from .configs import PowerSwitchboardConfig
from .power_board_singleton import PowerBoardSingleton
from .power_switch import PowerSwitch


def _get_power_api_logger() -> logging.Logger:
    """Get or create the logger for power board operations."""
    return logging.getLogger("power")

class PowerAPI:
    """Main power API class with all power board operations."""

    @classmethod
    def get_switch_dict(cls) -> dict[int, PowerSwitch]:
        """
        Get a dictionary of all switch channels.

        Returns:
            dict: Dictionary mapping channel numbers (1-20) to PowerSwitch objects
        """
        board = PowerBoardSingleton.get_instance()
        return board.switches

    @classmethod
    def set_switch(cls, channel: int, state: bool) -> bool:
        """
        Set the state of a switch (on/off).
        Thread-safe function that can be called from any thread.

        Args:
            channel: Channel number (1-20)
            state: True to turn on, False to turn off

        Returns:
            bool: True if successful, False otherwise
        """
        _get_power_api_logger().debug("Setting switch %s to %s", channel, state)
        board = PowerBoardSingleton.get_instance()
        return board.set_switch(channel, state)

    @classmethod
    def get_switch_state(cls, channel: int) -> bool:
        """
        Get the current state of a switch (on/off).
        Thread-safe function that can be called from any thread.

        Args:
            channel: Channel number (1-20)

        Returns:
            bool: True if switch is on, False otherwise
        """
        board = PowerBoardSingleton.get_instance()
        return board.get_switch_state(channel)

    @classmethod
    def set_fuse_trip(cls, channel: int, amps: PowerBoardFuseTripAmps) -> bool:
        """
        Set the fuse trip current for a switch.
        Thread-safe function that can be called from any thread.

        Args:
            channel: Channel number (1-20)
            amps: Fuse trip current setting

        Returns:
            bool: True if successful, False otherwise
        """
        board = PowerBoardSingleton.get_instance()
        return board.set_fuse_trip(channel, amps)

    @classmethod
    def get_fuse_trip(cls, channel: int) -> PowerBoardFuseTripAmps:
        """
        Get the fuse trip current for a switch.
        Thread-safe function that can be called from any thread.

        Args:
            channel: Channel number (1-20)

        Returns:
            PowerBoardFuseTripAmps: Fuse trip current setting
        """
        board = PowerBoardSingleton.get_instance()
        return board.get_fuse_trip(channel)

    @classmethod
    def get_fuse_state(cls, channel: int) -> bool:
        """
        Check if the fuse for a switch is OK.
        Thread-safe function that can be called from any thread.

        Args:
            channel: Channel number (1-20)

        Returns:
            bool: True if fuse is OK, False if blown
        """
        board = PowerBoardSingleton.get_instance()
        return board.get_fuse_state(channel)

    @classmethod
    def get_switch_details(cls, channel: int) -> dict[str, str]:
        """
        Get detailed information about a switch.
        Thread-safe function that can be called from any thread.

        Args:
            channel: Channel number (1-20)

        Returns:
            dict: Dictionary with switch details
        """
        board = PowerBoardSingleton.get_instance()
        return board.get_switch_details(channel)

    @classmethod
    def get_all_switch_states(cls) -> dict[int, dict[str, str]]:
        """
        Get the states of all switches.
        Thread-safe function that can be called from any thread.

        Returns:
            dict: Dictionary mapping channel numbers to switch states
        """
        board = PowerBoardSingleton.get_instance()
        return board.get_all_switch_states()

    @classmethod
    def shutdown_all_switches(cls, force: bool = False) -> bool:
        """
        Turn off all switches specified in the shutdown_channels configuration.
        Thread-safe function that can be called during system shutdown.

        Args:
            force: If True, shutdown all channels 1-20. If False, only shutdown configured channels.

        Returns:
            bool: True if all switches were successfully turned off, False otherwise
        """
        board = PowerBoardSingleton.get_instance()
        config = PowerSwitchboardConfig()
        logger = _get_power_api_logger()

        if force:
            shutdown_channels = range(1, 21)
        else:
            shutdown_channels = config.shutdown_channels

        success = True
        for channel in shutdown_channels:
            try:
                # Always convert to channel number using to_channel_num
                channel_num = cls.to_channel_num(channel)
                if not board.set_switch(channel_num, False):
                    success = False
            except (ValueError, KeyError) as e:
                logger.error("Failed to shut down channel %s: %s", channel, e)
                success = False

        return success


    @classmethod
    def get_channel_name(cls, channel_num: int) -> str:
        """
        Get channel name from channel number.
        """
        config = PowerSwitchboardConfig()
        name = config.inverted_channel_map.get(channel_num)
        if name is not None:
            return name
        raise KeyError(f'Invalid channel number. You gave {channel_num}')


    @classmethod
    def get_channel_num(cls, channel_name: str) -> int:
        """
        Get channel number from channel name.
        """
        config = PowerSwitchboardConfig()
        num = config.channel_map.get(channel_name)
        if num is not None:
            return num
        raise KeyError(f'Invalid channel name. You gave {channel_name}')


    @classmethod
    def to_channel_num(cls, channel: int | str) -> int:
        """
        Convert a channel identifier (int or str) to a channel number.
        Accepts int, numeric string, or channel name.
        """
        if isinstance(channel, int):
            return channel
        try:
            return int(channel)
        except (ValueError, TypeError):
            return cls.get_channel_num(channel)


    @classmethod
    def get_channel_info(cls) -> dict[str, int | str | dict[int, str] | dict[str, int]]:
        """
        Get information about all configured channels.
        """
        config = PowerSwitchboardConfig()
        return {
            'channel_map': config.channel_map.copy(),
            'inverted_channel_map': config.inverted_channel_map.copy(),
            'total_channels': len(config.channel_map)
        }

    @classmethod
    def set_switch_by_name(cls, channel_name: str, state: bool) -> bool:
        """
        Set the state of a switch by channel name.

        Args:
            channel_name: Channel name (device name)
            state: True to turn on, False to turn off

        Returns:
            bool: True if successful, False otherwise

        Raises:
            KeyError: If channel name is invalid
        """
        channel_num = cls.get_channel_num(channel_name)
        return cls.set_switch(channel_num, state)

    @classmethod
    def get_switch_state_by_name(cls, channel_name: str) -> bool:
        """
        Get the state of a switch by channel name.

        Args:
            channel_name: Channel name (device name)

        Returns:
            bool: True if switch is on, False otherwise

        Raises:
            KeyError: If channel name is invalid
        """
        channel_num = cls.get_channel_num(channel_name)
        return cls.get_switch_state(channel_num)


    @classmethod
    def get_all_switch_states_by_name(cls) -> dict[str, dict[str, str]]:
        """
        Get the states of all switches mapped by channel name.
        """
        config = PowerSwitchboardConfig()
        channel_states = cls.get_all_switch_states()
        inv_map = config.inverted_channel_map
        return {
            inv_map.get(channel_num, f"channel_{channel_num}"): state
            for channel_num, state in channel_states.items()
        }

    @classmethod
    def initialize_power_board_async(
        cls,
        timeout: int = 30,
        callback: Optional[Callable[[bool], None]] = None
    ) -> threading.Thread:
        """
        Initialize the power board in a background thread and optionally wait for completion.

        Args:
            timeout: Maximum time to wait for initialization in seconds
            callback: Optional callback function that will be called with a boolean indicating
                     success (True) or failure (False) when initialization completes or times out

        Returns:
            threading.Thread: The initialization thread
        """
        logger = _get_power_api_logger()

        def init_worker():
            logger.info("Starting power board initialization in background thread")
            success = False
            start_time = time.time()

            try:
                # Initialize the power board with timeout check
                while not PowerBoardSingleton.is_initialized():
                    # Check if timeout has occurred
                    if time.time() - start_time > timeout:
                        logger.error("Timeout after %s seconds while initializing power board", timeout)
                        break

                    try:
                        # Try to initialize the power board
                        PowerBoardSingleton.get_instance()
                        logger.info("Power board initialization complete")
                        success = True
                        break
                    except Exception as e:  # pylint: disable=broad-except
                        # If initialization fails, log and retry after a short delay
                        logger.warning("Power board initialization attempt failed: %s. Retrying...", e)
                        safe_sleep(0.5)

                # If already initialized, mark as success
                if PowerBoardSingleton.is_initialized():
                    success = True

            except Exception as e:  # pylint: disable=broad-except
                logger.error("Power board initialization failed: %s", e)

            # Call the callback if provided
            if callback:
                try:
                    callback(success)
                except Exception as e:  # pylint: disable=broad-except
                    logger.error("Error in power board initialization callback: %s", e)

        # Create and start the initialization thread
        init_thread = threading.Thread(
            target=init_worker,
            name="PowerBoardInit",
            daemon=True  # Make it a daemon thread so it doesn't block system shutdown
        )
        init_thread.start()
        return init_thread

    @classmethod
    def initialize_power_board(cls, timeout: int = 30) -> bool:
        """
        Initialize the power board and wait for it to be ready.
        This is a blocking call that will wait up to the specified timeout.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if power board initialized successfully, False otherwise
        """
        logger = _get_power_api_logger()

        if PowerBoardSingleton.is_initialized():
            logger.info("Power board already initialized")
            return True

        # Use an event to signal completion
        init_complete = threading.Event()
        init_success = [False]  # Use a list to store success state (to make it mutable in the callback)

        def on_init_complete(success: bool):
            init_success[0] = success
            init_complete.set()

        # Start initialization in background
        cls.initialize_power_board_async(timeout, on_init_complete)

        # Wait for initialization to complete or timeout
        if init_complete.wait(timeout):
            return init_success[0]

        logger.error("Timeout waiting for power board initialization (%ss)", timeout)
        return False

    @classmethod
    def is_power_board_ready(cls) -> bool:
        """
        Check if the power board is initialized and ready.

        Returns:
            bool: True if power board is ready, False otherwise
        """
        return PowerBoardSingleton.is_initialized()

    @classmethod
    def wait_for_power_board_ready(cls, timeout: int = 30) -> bool:
        """
        Wait for the power board to be initialized and ready.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if power board is ready, False if timeout occurred
        """
        logger = _get_power_api_logger()

        start_time = time.time()
        while not PowerBoardSingleton.is_initialized():
            # Check if timeout has occurred
            if time.time() - start_time > timeout:
                logger.error("Timeout waiting for power board initialization (%ss)", timeout)
                return False

            # Wait a bit before checking again
            safe_sleep(0.5)

        return True

"""Module containing the PowerBoard class."""
import logging
import threading
from typing import Dict, Optional

from common.enums import PowerBoardFuseTripAmps

from .power_switch import PowerSwitch
from common.power_board.configs import PowerSwitchboardConfig
from common.thread_handling import safe_sleep


class PowerBoardError(Exception):
    """Base class for all power board-related exceptions."""
    pass  # pylint: disable=unnecessary-pass

class I2CBusError(PowerBoardError):
    """Raised when there is an I2C communication error."""
    pass  # pylint: disable=unnecessary-pass

class ConfigurationError(PowerBoardError):
    """Raised when there is an issue with configuration."""
    pass  # pylint: disable=unnecessary-pass

class PowerBoard:
    """
    Manages a power board with multiple switches via I2C.
    Provides methods to configure, control, and monitor switch states.
    Thread-safe implementation for cross-thread access.
    """

    # Amp mapping for trip current configuration
    AMP_MAPPING = {
        "2.0A": PowerBoardFuseTripAmps.TA_2P0A,
        "2.3A": PowerBoardFuseTripAmps.TA_2P3A,
        "5.0A": PowerBoardFuseTripAmps.TA_5P0A,
        "8.0A": PowerBoardFuseTripAmps.TA_8P0A
    }

    def __init__(self, config: Optional[PowerSwitchboardConfig] = None):
        """Initialize the PowerBoard with the given I2C configuration."""
        import smbus2
        self.config = config or PowerSwitchboardConfig()
        self.switches: Dict[int, PowerSwitch] = {}
        self.bus = smbus2.SMBus(self.config.i2c_bus_number)

        # Lock for thread safety
        self._lock = threading.RLock()

        # Set up logging
        self.logger = logging.getLogger("power_switchboard")
        self.logger.info("PowerBoard initialization started - I2C bus: %s", self.config.i2c_bus_number)

        # Initialize the board
        self.logger.debug("Starting board initialization...")
        self._initialize_board()
        self.logger.info("Board initialization completed - %s switches created", len(self.switches))

        # Configure trip amp settings
        self.logger.debug("Starting trip amp configuration...")
        self._configure_trip_amps()
        self.logger.info("PowerBoard initialization complete")

    def _initialize_board(self):
        """Initialize the board with 20 switches and configure I2C communication."""
        with self._lock:
            self.logger.debug("Creating 20 power switches with I2C addressing...")
            # Create 20 switches with proper I2C addressing
            for channel in range(1, 21):
                # Calculate pair index based on the old implementation's logic
                group_index = (channel - 1) // 4  # Which group of 4 channels
                in_group_index = (channel - 1) % 4  # Position within the group
                pair_index = group_index * 2 + (1 if in_group_index >= 2 else 0)

                # Calculate chip address (each chip handles 2 pairs)
                chip_address = 0x21 + (pair_index // 2)

                # Calculate register offset (second pair on each chip uses offset)
                register_offset = (pair_index % 2) == 1

                # First switch in each pair
                is_first_switch = (channel % 2) == 1

                # Create the switch
                self.switches[channel] = PowerSwitch(
                    channel=channel,
                    chip_address=chip_address,
                    register_offset=register_offset,
                    is_first_switch=is_first_switch
                )

                self.logger.debug("Created switch %s: chip_addr=%s, reg_offset=%s, first_switch=%s",
                                channel, hex(chip_address), register_offset, is_first_switch)

            # Configure all chips
            self.logger.debug("Configuring all I2C chips...")
            self._configure_all_chips()

    def _configure_all_chips(self):
        """Configure all I2C chips used by the power board."""
        # Track which chips have been configured
        configured_chips: set[tuple[int, bool]] = set()

        for switch in self.switches.values():
            chip_key = (switch.chip_address, switch.register_offset)
            if chip_key not in configured_chips:
                self.logger.debug("Configuring chip at address %s with offset %s",
                                hex(switch.chip_address), switch.register_offset)
                self._configure_chip(switch.chip_address, switch.register_offset)
                configured_chips.add(chip_key)

        self.logger.info("Configured %s unique I2C chips", len(configured_chips))

    def _configure_chip(self, address: int, offset: bool):
        """Configure a single I2C chip."""
        try:
            self.logger.debug("Configuring chip %s (offset=%s): turning off outputs...", hex(address), offset)
            # Turn everything off
            self._write_i2c(address, 0x02 + int(offset), 0x00)

            self.logger.debug("Configuring chip %s (offset=%s): setting direction...", hex(address), offset)
            # Set direction
            self._write_i2c(address, 0x04 + int(offset), 0x01)

            self.logger.debug("Configuring chip %s (offset=%s): enabling configuration...", hex(address), offset)
            # Enable configuration
            self._write_i2c(address, 0x06 + int(offset), 0x11)

            self.logger.debug("Successfully configured chip at address %s with offset %s", hex(address), offset)
        except Exception as e:
            self.logger.error("Failed to configure chip at %s: %s", hex(address), e)
            raise ConfigurationError(f"Failed to configure chip: {e}") from e

    def _configure_trip_amps(self):
        """Configure trip amperage settings for all channels."""
        self.logger.info("Configuring trip amp settings...")
        for channel_name, amp_value in self.config.default_trip_amps.items():
            try:
                channel_num = self.config.channel_map[channel_name]
                self.set_fuse_trip(channel_num, self.AMP_MAPPING[amp_value])
                self.logger.debug("Set channel %s trip amps to %s", channel_num, amp_value)
            except (ValueError, KeyError) as e:
                self.logger.error("Failed to set trip amps for %s: %s", channel_name, e)
        self.logger.info("Trip amp configuration complete")

    def _write_i2c(self, address: int, register: int, value: int):
        """Write a value to an I2C register with retry logic."""
        with self._lock:
            self.logger.debug("I2C write: addr=%s reg=%s val=%s", hex(address), hex(register), hex(value))
            for attempt in range(self.config.retry_attempts):
                try:
                    self.bus.write_byte_data(address, register, value)
                    if attempt > 0:
                        self.logger.debug("I2C write succeeded on attempt %s", attempt + 1)
                    return
                except OSError as e:
                    attempt_num = (attempt + 1)/self.config.retry_attempts
                    self.logger.warning("I2C write failed, attempt %s: %s", attempt_num, e)
                    if attempt == self.config.retry_attempts - 1:
                        raise I2CBusError("I2C write failed after %s attempts", self.config.retry_attempts) from e  #pylint: disable=raising-format-tuple
                    safe_sleep(self.config.retry_delay * (2 ** attempt))

    def _read_i2c(self, address: int, register: int) -> int:
        """Read a value from an I2C register with retry logic."""
        with self._lock:
            for attempt in range(self.config.retry_attempts):
                try:
                    value = self.bus.read_byte_data(address, register)
                    self.logger.debug("I2C read: addr=%s reg=%s val=%s", hex(address), hex(register), hex(value))
                    if attempt > 0:
                        self.logger.debug("I2C read succeeded on attempt %s", attempt + 1)
                    return value
                except OSError as e:
                    attempt_num = (attempt + 1)/self.config.retry_attempts
                    self.logger.warning("I2C read failed, attempt %s: %s", attempt_num, e)
                    if attempt == self.config.retry_attempts - 1:
                        raise I2CBusError(f"I2C read failed after {self.config.retry_attempts} attempts") from e
                    safe_sleep(self.config.retry_delay * (2 ** attempt))
            raise I2CBusError("Unexpected error in I2C read operation")


    def _update_switch_from_byte(self, switch: PowerSwitch, value: int):
        """Update switch state from a byte value read from hardware."""
        if switch.is_first_switch:
            switch.is_on = bool((value & 0x08) >> 3)
            switch.fuse_ok = not bool(value & 0x01)
            switch.trip_amps = PowerBoardFuseTripAmps((value & 6) >> 1)
        else:
            switch.is_on = bool((value & 0x80) >> 7)
            switch.fuse_ok = not bool((value >> 4) & 0x01)
            switch.trip_amps = PowerBoardFuseTripAmps((value & 60) >> 5)

    def _read_switch_state(self, channel: int):
        """Read the current state of a switch from hardware."""
        with self._lock:
            switch = self.switches.get(channel)
            if not switch:
                raise ValueError(f"Invalid channel: {channel}")

            try:
                register = 0x02 + int(switch.register_offset)
                value = self._read_i2c(switch.chip_address, register)
                self._update_switch_from_byte(switch, value)
            except Exception as e:  #pylint: disable=broad-except
                self.logger.error("Failed to read switch state for channel %s: %s", channel, e)

    def _write_switch_state(self, channel: int):
        """Write the current state of a switch to hardware."""
        with self._lock:
            switch = self.switches.get(channel)
            if not switch:
                raise ValueError(f"Invalid channel: {channel}")

            try:
                # First read the current value
                register = 0x02 + int(switch.register_offset)
                current_value = self._read_i2c(switch.chip_address, register)

                # Modify the value based on switch state
                if switch.is_first_switch:
                    # First switch in pair
                    if switch.is_on:
                        current_value |= (1 << 3)  # Set bit 3
                    else:
                        current_value &= ~(1 << 3)  # Clear bit 3

                    # Set trip amps (bits 1-2)
                    current_value = (current_value & (~(3 << 1))) | ((switch.trip_amps) << 1)
                else:
                    # Second switch in pair
                    if switch.is_on:
                        current_value |= (1 << 7)  # Set bit 7
                    else:
                        current_value &= ~(1 << 7)  # Clear bit 7

                    # Set trip amps (bits 5-6)
                    current_value = (current_value & (~(3 << 5))) | ((switch.trip_amps) << 5)

                # Write the modified value
                self._write_i2c(switch.chip_address, register, current_value)

                # Read back to verify and update state
                updated_value = self._read_i2c(switch.chip_address, register)
                self._update_switch_from_byte(switch, updated_value)

            except Exception as e:  #pylint: disable=broad-except
                self.logger.error("Failed to write switch state for channel %s: %e", channel, e)

    # Public API methods - all thread-safe

    def set_switch(self, channel: int, state: bool) -> bool:
        """Set the state of a switch (on/off)."""
        with self._lock:
            self.logger.debug("Setting switch %s to %s", channel, "ON" if state else "OFF")
            if channel not in self.switches:
                self.logger.error("Invalid channel: %s", channel)
                return False
            self._read_switch_state(channel)  # Update current state
            self.switches[channel].is_on = state
            self._write_switch_state(channel)
            self.logger.debug("Switch %s set to %s", channel, "ON" if state else "OFF")
            return True

    def get_switch_state(self, channel: int) -> bool:
        """Get the current state of a switch (on/off)."""
        with self._lock:
            self.logger.debug("Reading switch state for channel %s", channel)
            if channel not in self.switches:
                self.logger.error("Invalid channel: %s", channel)
                return False

            self._read_switch_state(channel)
            state = self.switches[channel].is_on
            self.logger.debug("Switch %s state: %s", channel, "ON" if state else "OFF")
            return state

    def set_fuse_trip(self, channel: int, amps: PowerBoardFuseTripAmps) -> bool:
        """Set the fuse trip current for a switch."""
        with self._lock:
            self.logger.debug("Setting fuse trip for channel %s to %s", channel, amps.name)
            if channel not in self.switches:
                self.logger.error("Invalid channel: %s", channel)
                return False

            self._read_switch_state(channel)  # Update current state
            self.switches[channel].trip_amps = amps
            self._write_switch_state(channel)
            self.logger.debug("Fuse trip for channel %s set to %s", channel, amps.name)
            return True

    def get_fuse_trip(self, channel: int) -> PowerBoardFuseTripAmps:
        """Get the fuse trip current for a switch."""
        with self._lock:
            if channel not in self.switches:
                return PowerBoardFuseTripAmps.TA_UNDEFINED

            self._read_switch_state(channel)
            return self.switches[channel].trip_amps

    def get_fuse_state(self, channel: int) -> bool:
        """Check if the fuse for a switch is OK."""
        with self._lock:
            if channel not in self.switches:
                return False

            self._read_switch_state(channel)
            return self.switches[channel].fuse_ok

    def get_switch_details(self, channel: int) -> dict[str,str]:
        """Get detailed information about a switch."""
        with self._lock:
            if channel not in self.switches:
                return {}

            self._read_switch_state(channel)
            return self.switches[channel].get_state()

    def get_all_switch_states(self) -> dict[int, dict[str, str]]:
        """Get the states of all switches."""
        with self._lock:
            self.logger.debug("Reading all switch states...")
            result: dict[int, dict[str, str]] = {}
            for channel, switch in self.switches.items():
                self._read_switch_state(channel)
                result[channel] = switch.get_state()
            self.logger.debug("Read states for %s switches", len(result))
            return result

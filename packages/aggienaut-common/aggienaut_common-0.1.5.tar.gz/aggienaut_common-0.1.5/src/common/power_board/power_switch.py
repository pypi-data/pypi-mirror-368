"""
Power switch module for power board control and monitoring.

Provides the PowerSwitch dataclass for representing individual power switches
with their state, configuration, and I2C addressing information. Each switch
corresponds to a channel on the power board with configurable fuse trip settings
and real-time monitoring of switch and fuse states.
"""

from dataclasses import dataclass
from common.enums import PowerBoardFuseTripAmps



@dataclass
class PowerSwitch:
    """Represents a single power switch with its state and configuration."""
    channel: int  # Channel number (1-20)
    is_on: bool = False  # Switch state
    fuse_ok: bool = True  # Fuse state
    trip_amps: PowerBoardFuseTripAmps = PowerBoardFuseTripAmps.TA_UNDEFINED

    # I2C addressing information
    chip_address: int = 0  # I2C address of the chip
    register_offset: bool = False  # Whether to use register offset
    is_first_switch: bool = False  # Whether this is the first switch in the pair

    def get_state(self) -> dict[str, str]:
        """Returns the current state of the switch as a dictionary."""
        return {
            'switch_on': str(self.is_on),
            'fuse_ok': str(self.fuse_ok),
            'trip_amps': str(self.trip_amps)
        }

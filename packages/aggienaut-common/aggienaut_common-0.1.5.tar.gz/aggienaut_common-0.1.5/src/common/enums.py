""" Module containing all enums used in the aggienaut. """

from enum import Enum, StrEnum, auto, IntEnum
from typing import Optional


class ThrusterState(Enum):
    """
    Enum for thruster state.
    """
    OFF = "off"
    FWD = "fwd"
    REV = "rev"

    @classmethod
    def from_str(cls, value: str) -> Optional["ThrusterState"]:
        """
        Convert a string to a ThrusterState enum value.
        """
        try:
            lower_value = value.lower()
        except (ValueError, AttributeError):
            return None
        return cls(lower_value)

    def __str__(self):
        """Return the value of the enum when converted to string"""
        return str(self.value)

    def __int__(self):
        """Return the value of the enum when converted to int"""
        value_map = {
        "off": 0,
        "fwd": 1,
        "rev": -1,
        }
        return value_map[self.value]

    def __mul__(self, other):
        """
        Multiply the thruster
        """
        value_map = {
            "off": 0,
            "fwd": 1,
            "rev": -1,
        }
        if isinstance(other, (int, float)):
            return value_map[self.value] * other
        return NotImplemented


class RudderState(Enum):
    """
    Enum for rudder state.
    """
    CENTER = 0
    LEFT = 45
    RIGHT = -45

    def __str__(self):
        """Return the value of the enum when converted to string"""
        return str(self.value)


    def __mul__(self, other):
        """
        Multiply the rudder state by a scalar.
        """
        if isinstance(other, (int, float)):
            return self.value * other
        return NotImplemented

    def __add__(self, other):
        """
        Add the rudder state to a scalar.
        """
        if isinstance(other, (int, float)):
            return self.value + other
        return NotImplemented


    @classmethod
    def from_str(cls, value: str) -> Optional["RudderState"] | int:
        """
        Convert a string to a RudderState enum value.
        """

        # If 'left', 'right', 'center' is in the string, convert it to the corresponding enum value
        if "left" in value:
            return cls.LEFT
        if "right" in value:
            return cls.RIGHT
        if "center" in value:
            return cls.CENTER
        # convert to numeric value if possible
        try:
            numeric_value = int(value)
            try:
                return cls(numeric_value)
            except (ValueError, TypeError):
                return numeric_value
        except (ValueError, TypeError):
            return None


class NavMode(StrEnum):
    """
    Enum for navigation mode.
    """
    MANUAL = "manual"
    AUTO = "auto"

    @staticmethod
    def from_str(str_value: str) -> "NavMode":
        """
        Convert a string to a NavMode enum value.
        """
        return NavMode(str_value.lower())


class BootMode(StrEnum):
    """
    Enum for boot mode.
    """
    NORMAL = auto()
    SAFE   = auto()

    def __str__(self) -> str:
        """Return a string representation of the boot mode."""
        return self.name.lower()

    def __repr__(self) -> str:
        """Return a detailed representation for debugging."""
        return f"BootMode.{self.name}"

    def to_str(self) -> str:
        """Return a BootMode object as a string."""
        return str(self)

    @classmethod
    def from_str(cls, string: str) -> 'BootMode':
        """Return a string as a BootMode object"""
        if string.lower() == 'safe':
            return cls.SAFE
        if string.lower() == 'normal':
            return cls.NORMAL

        raise ValueError(f'Invalid BootMode string. Got {string}')


class PowerControlMode(StrEnum):
    """
    Enum for power control mode
    """
    AUTO = "auto"
    MANUAL = "manual"

    @classmethod
    def from_str(cls, str_value: str) -> "PowerControlMode":
        """
        Convert a string to a PowerMode enum value.
        """
        try:
            # Normalize the input to lowercase
            normalized = str_value.lower()
            return cls(normalized)
        except ValueError as e:
            raise ValueError(f"Invalid Power Mode name. Got '{str_value}'. Must be one of: {', '.join([repr(m.value) for m in cls])}") from e




class PowerMode(StrEnum):
    """
    Enum for power mode.
    """
    NORMAL     = 'normal'  # Normal power mode
    LOW        = 'low'  # Low power mode
    CRITICAL   = 'critical'  # Critical power mode

    @classmethod
    def from_str(cls, str_value: str) -> "PowerMode":
        """
        Convert a string to a PowerMode enum value.
        """
        try:
            # Normalize the input to lowercase
            normalized = str_value.lower()
            return cls(normalized)
        except ValueError as e:
            raise ValueError(f"Invalid Power Mode name. Got '{str_value}'. Must be one of: {', '.join([repr(m.value) for m in cls])}") from e



class PowerBoardFuseTripAmps(IntEnum):
    """
    Enum for fuse trip current values.
    """
    TA_UNDEFINED = 0
    TA_2P0A = 1
    TA_2P3A = 2
    TA_5P0A = 3
    TA_8P0A = 4


    def __str__(self):
        """Return the value of the enum when converted to string"""
        trip_amp_mapping = {
            0:"UNDEFINED",
            1:"2.0A",
            2:"2.3A",
            3:"5.0A",
            4:"8.0A"
            }

        str_value = trip_amp_mapping.get(self.value)

        if str_value is not None:
            return str_value

        return "Unknown"

    def __repr__(self):
        """Return the value of the enum when converted to string"""
        return self.__str__()

    @classmethod
    def from_str(cls, value: str) -> "PowerBoardFuseTripAmps":
        """
        Convert a string to a PowerBoardFuseTripAmps enum value. Defaults to TA_UNDEFINED if not found.
        """
        if not isinstance(value, str):
            return cls.TA_UNDEFINED

        # Normalize input
        normalized = value.strip().upper()

        # Direct string mappings (case-insensitive)
        string_mappings = {
            "2.0A": cls.TA_2P0A,
            "2.3A": cls.TA_2P3A,
            "5.0A": cls.TA_5P0A,
            "8.0A": cls.TA_8P0A,
            "UNDEFINED": cls.TA_UNDEFINED,
        }

        if normalized in string_mappings:
            return string_mappings[normalized]

        # Try parsing as integer
        try:
            return cls(int(value))
        except (ValueError, TypeError):
            return cls.TA_UNDEFINED


    @classmethod
    def from_value(cls, value) -> "PowerBoardFuseTripAmps":
        """
        Convert a string or int to a PowerBoardFuseTripAmps enum value. Defaults to TA_UNDEFINED if not found.
        """
        if isinstance(value, str):
            return cls.from_str(value)
        if isinstance(value, int):
            try:
                return cls(value)
            except ValueError:
                return cls.TA_UNDEFINED
        return cls.TA_UNDEFINED

class SwitchState(StrEnum):
    """
    Enum for switch state.
    """
    ON = "on"
    OFF = "off"

    def to_bool(self) -> bool:
        """True if on False if off"""
        return self == self.ON

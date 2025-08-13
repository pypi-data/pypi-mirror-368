from common.config_framework.base_config import BaseConfig

class PowerSwitchboardConfig(BaseConfig):
    config_filename = 'power_system'
    section = 'power_switchboard'
    i2c_bus_number: int
    retry_attempts: int
    retry_delay: float
    channel_map: dict[str, int]
    shutdown_channels: list[str]
    default_trip_amps: dict[str, str]  # e.g., {"thruster": "2.0A", ...}

    @property
    def inverted_channel_map(self) -> dict[int, str]:
        """
        Returns a mapping from channel numbers to channel names.
        """
        return {v: k for k, v in self.channel_map.items()}

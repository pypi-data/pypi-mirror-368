from common.config_framework.base_config import BaseConfig

# --- Hardware Config Classes ---
class GeneralHardwareConfig(BaseConfig):
    config_filename = 'hardware'
    section = 'general'
    data_dir: str

class SunsaverConfig(BaseConfig):
    config_filename = 'hardware'
    section = 'sunsaver'
    poll_interval: float|int
    baud_rate: int
    serial_timeout: float|int
    unit_id: int
    port: str
    bytesize: int
    parity: str
    stopbits: int

class GarminGPSConfig(BaseConfig):
    config_filename = 'hardware'
    section = 'garmin_gps'
    base_filename = 'garmin_gps_data'
    data_filename: str
    baud_rate: int
    port: str
    error_wait_time: float|int
    poll_interval: float|int  # Seconds time between polls
    serial_timeout: float|int

class NavigationPicoConfig(BaseConfig):
    config_filename = 'hardware'
    section = 'navigation_pico'
    data_filename: str
    max_retries: int
    retry_delay: int  # Seconds
    baud_rate: int
    port: str
    serial_timeout: float|int
    reset_sleep: float|int
    reboot_sleep: float|int
    command_sleep: float|int
    read_size: int

class PicoRudderConfig(BaseConfig):
    config_filename = 'navigation'
    section = 'pico_rudder'
    max_left_pulse: int
    neutral_pulse: int
    max_right_pulse: int
    rudder_pin: int
    rudder_pwm_freq: int

    def to_dict(self):
        "Custom to_dict method to match the expected format. The Micro Controller expects a dict with specific keys."
        return {
            'max_left_pulse': self.max_left_pulse,
            'neutral_pulse': self.neutral_pulse,
            'max_right_pulse': self.max_right_pulse,
            'rudder_pin': self.rudder_pin,
            'rudder_pwm_freq': self.rudder_pwm_freq
        }

class PicoThrusterConfig(BaseConfig):
    config_filename = 'navigation'
    section = 'pico_thruster'
    max_pct: int
    off_pulse: int
    max_fwd_pulse: int
    max_rev_pulse: int
    thruster_pin: int
    thruster_pwm_freq: int
    thruster_deadzones: dict[str, int]

    def to_dict(self):
        "Custom to_dict method to match the expected format. The Micro Controller expects a dict with specific keys."
        return {
            'max_pct': self.max_pct,
            'off_pulse': self.off_pulse,
            'max_fwd_pulse': self.max_fwd_pulse,
            'max_rev_pulse': self.max_rev_pulse,
            'thruster_pin': self.thruster_pin,
            'thruster_pwm_freq': self.thruster_pwm_freq,
            'thruster_deadzones': self.thruster_deadzones
        }

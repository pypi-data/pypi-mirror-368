from common.config_framework.base_config import BaseConfig

class USBConfig(BaseConfig):
    config_filename = 'usb'
    hub_positions: dict[str, int]  # Maps hub names to their USB port positions
    device_map: dict[str, str]  # Maps device names to their USB device paths
    symlink_dir: str  # Directory for symlinks
    device_node_prefix: str  # Prefix for device nodes
    device_subsystem: str  # Subsystem for device search

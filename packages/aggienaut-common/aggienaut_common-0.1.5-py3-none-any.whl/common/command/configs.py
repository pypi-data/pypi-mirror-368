from common.config_framework.base_config import BaseConfig

class MQTTConfigTopicMappings(BaseConfig):
    config_filename = 'mqtt_topics'
    section = 'topic_mappings'
    garmin_gps:str
    iridium_gps:str
    radio_transmit:str
    power_alerts:str
    power_status:str
    sunsaver:str
    handle_cmd:str
    command_line_tool_receive:str
    set_boot_mode_cmd:str
    get_boot_mode_cmd:str
    enter_boot_mode_cmd:str
    execute_reboot_cmd:str
    execute_shutdown_cmd:str
    reload_configs_cmd:str
    set_config_cmd:str
    get_status_cmd:str
    set_power_switch_cmd:str
    set_power_fuse_cmd:str
    get_power_channel_cmd:str
    set_power_mode_cmd:str
    get_power_status_cmd:str
    get_sunsaver_cmd:str
    set_rudder_cmd:str
    get_rudder_cmd:str
    set_thruster_cmd:str
    get_thruster_cmd:str
    set_navigation_mode_cmd:str
    get_navigation_mode_cmd:str
    get_navigation_status_cmd:str
    get_gps_cmd:str
    add_waypoint_cmd:str
    set_waypoint_cmd:str
    remove_waypoint_cmd:str
    get_waypoints_cmd:str

class MQTTCommandMappings(BaseConfig):
    config_filename = 'command_mapping.toml'
    command_byte_topic_mapping: dict[str, str]  # Maps hex byte values to MQTT topics

class CommandMappingConfig(BaseConfig):
    """Configuration for command mappings."""
    config_filename = "command_mapping.toml"
    byte_command_mappings: dict[str, int]
    valid_states: dict[str, str]




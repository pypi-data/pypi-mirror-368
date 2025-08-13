"""Module containing logic for loading configs"""
from pathlib import Path
from typing import Any, Optional, List

from common.type_validation import (assert_type,assert_not_none,assert_mapping,assert_boolean,
                             assert_numeric,assert_string_like,assert_sequence,assert_path,assert_length)

from common.errors import TypeAssertionError

from common.config_framework.config_manager import ConfigManager

# Helper functions that provide simplified access to ConfigManager functionality
def get_nested_value(config: dict, key_path: str, default_value: Any = None) -> dict | None | Any:
    """
    Access a nested dictionary value using a dot-separated string path.

    This is a convenience wrapper around ConfigManager.get_nested_value().

    Args:
        config (dict): The dictionary to access
        key_path (str): Dot-separated path (e.g., "main.sys.logging")
        default_value: Value to return if path doesn't exist

    Returns:
        The value at the specified path or default_value if the path doesn't exist
    """
    return ConfigManager.get_nested_value(config, key_path, default_value)


def set_nested_value(config: dict, key_path: str, value) -> dict:
    """
    Set a value in a nested dictionary using a dot-separated string path.
    Creates intermediate dictionaries if they don't exist.

    This is a convenience wrapper around ConfigManager.set_nested_value().

    Args:
        config (dict): The dictionary to modify
        key_path (str): Dot-separated path (e.g., "main.sys.logging")
        value: The value to set at the specified path

    Returns:
        The modified dictionary
    """
    return ConfigManager.set_nested_value(config, key_path, value)


def load_config(config_name: str | Path, key_path: str | None = None) -> dict:
    """
    Load configuration from file or cache.

    This is a convenience wrapper around ConfigManager.load_config().

    Args:
        config_name (str|Path): name of config file or path to the file to read the config from
        key_path (str|None): key_path to select the data from in the format of "section.subsection.subsection"

    Returns:
        dict: Configuration data
    """
    return ConfigManager.load_config(config_name, key_path)


def archive_config(config_path: str | Path, compress: bool = True):
    """
    Archives config with timestamp appended to filename in a config_archive subdirectory.

    This is a convenience wrapper around ConfigManager.archive_config().

    Args:
        config_path: Path to the configuration file
        compress: Whether to compress the archived file (default: True)

    Returns:
        Path to the archived file
    """
    return ConfigManager.archive_config(config_path, compress)


def restore_config(config_path: str | Path, version: str | None = None, compress_backup: bool = False):
    """
    Restores a configuration file from archive.

    This is a convenience wrapper around ConfigManager.restore_config().

    Args:
        config_path: Path to the current configuration file
        version: Specific version timestamp (default: most recent)
        compress_backup: Whether to compress the pre-restore backup (default: False)

    Returns:
        True if restoration was successful, False otherwise
    """
    return ConfigManager.restore_config(config_path, version, compress_backup)


def list_archived_configs(config_path: str | Path) -> List[str]:
    """
    Lists all archived versions of a configuration file.

    This is a convenience wrapper around ConfigManager.list_archived_configs().

    Args:
        config_path: Path to the configuration file

    Returns:
        List of archived versions with timestamps
    """
    return ConfigManager.list_archived_configs(config_path)


def update_config(config_name: str, key_path: str, new_value: Any, archive: bool = True, compress: bool = False):
    """
    Updates a configuration file by changing the value at the specified key path. Also updates the config cache.

    This is a convenience wrapper around ConfigManager.update_config().

    Args:
        config_name: Name of the configuration file
        key_path: Dot-separated path to the key to update
        new_value: New value to set
        archive: Whether to archive the config before updating (default: True)
        compress: Whether to compress the archived file (default: False)

    Returns:
        True if update was successful, False otherwise
    """
    return ConfigManager.update_config(config_name, key_path, new_value, archive, compress)



def get_asserted_config(config_name: str, key_path: Optional[str] = None, assertion_type: str = 'mapping',
                       default_value: Any = None, **assertion_kwargs) -> Any:
    """
    Get a nested config value and assert its type in one step.

    Args:
        config_name (str): Name of the config file to load
        key_path (str): Dot-separated path to the config value (e.g., "navigation.speed.max")
        assertion_type (str): Type of assertion to perform. Options:
            - "type": Assert specific type(s) - requires 'expected_type' kwarg
            - "not_none": Assert value is not None
            - "numeric": Assert value is numeric (int/float) - supports 'min_val', 'max_val'
            - "string_like": Assert string-like (str/bytes) - supports 'min_len', 'max_len'
            - "sequence": Assert sequence (list/tuple) - supports 'min_len', 'max_len'
            - "mapping": Assert mapping (dict) - supports 'required_keys'
            - "path": Assert valid path - supports path validation options
            - "length": Assert length constraints - supports 'min_len', 'max_len'
            - "boolean": Assert value is a boolean
        default_value (Any): Default value if key_path doesn't exist
        **assertion_kwargs: Additional arguments passed to the assertion function

    Returns:
        The validated config value with proper typing

    Raises:
        TypeAssertionError: If the value doesn't pass the assertion
        KeyError: If key_path is not found and no default_value provided
        ValueError: If assertion_type is not recognized

    Examples:
        ### Get and assert a numeric speed limit
        max_speed = get_asserted_config("navigation", "speed.max", "numeric",
                                      min_val=0, max_val=100)

        ### Get and assert a string configuration path
        log_path = get_asserted_config("mission", "logging.path", "string_like",
                                     min_len=1)

        ### Get and assert length of any object with __len__
        api_keys = get_asserted_config("security", "api.keys", "length",
                                     min_len=1, max_len=10)

        ### Get and assert a specific type with fallback
        timeout = get_asserted_config("network", "timeout", "type",
                                    expected_type=int, default_value=30)

        ### Get and assert a boolean value
        debug_mode = get_asserted_config("mission", "debug", "boolean")
    """

    # Load the config and get the nested value
    config = load_config(config_name)

    if key_path is not None:
        value = get_nested_value(config, key_path, default_value)
    else:
        value = config

    # If we got the default value and it's None, handle appropriately
    if value is default_value and default_value is None and assertion_type != "not_none":
        raise KeyError(f"Config key '{key_path}' not found in '{config_name}' and no default provided")

    # Create a descriptive name for error messages
    config_context = f"config['{config_name}'].{key_path}"

    # Add custom message to assertion_kwargs if not already provided
    if 'msg' not in assertion_kwargs:
        assertion_kwargs['msg'] = None  # Will be filled by each assertion function

    # Define mapping of assertion types to assertion functions
    assertion_functions = {
        "type": assert_type,
        "not_none": assert_not_none,
        "numeric": assert_numeric,
        "string_like": assert_string_like,
        "sequence": assert_sequence,
        "mapping": assert_mapping,
        "path": assert_path,
        "length": assert_length,
        "boolean": assert_boolean
    }

    # Apply the appropriate assertion based on assertion_type
    try:
        # Check if assertion_type is valid
        if assertion_type not in assertion_functions:
            valid_types = list(assertion_functions.keys())
            raise ValueError(f"Unknown assertion_type '{assertion_type}'. Valid options: {valid_types}")

        # Special case for "type" assertion which requires expected_type
        if assertion_type == "type" and 'expected_type' not in assertion_kwargs:
            raise ValueError("assertion_type 'type' requires 'expected_type' argument")

        # Execute the appropriate assertion function
        return assertion_functions[assertion_type](value, **assertion_kwargs)

    except TypeAssertionError as e:
        # Replace 'value' with the config context in the error message
        error_msg = str(e).replace("'value'", f"'{config_context}'")
        raise TypeAssertionError(error_msg) from e


def get_asserted_nested_config(config: dict, key_path: str, assertion_type: str,
                             default_value: Any = None, **assertion_kwargs) -> Any:
    """
    Get a nested value from an already-loaded config dict and assert its type.
    This is useful when you already have a config dict and don't need to reload it.

    Args:
        config (dict): The config dictionary to search
        key_path (str): Dot-separated path to the config value
        assertion_type (str): Type of assertion to perform (same options as get_asserted_config)
        default_value (Any): Default value if key_path doesn't exist
        **assertion_kwargs: Additional arguments passed to the assertion function

    Returns:
        The validated config value with proper typing

    Examples:
        ### Load config once, then get multiple asserted values
        config = get_asserted_config("navigation")

        max_speed = get_asserted_nested_value(config, "speed.max", "numeric",
                                            min_val=0, max_val=100)
        min_speed = get_asserted_nested_value(config, "speed.min", "numeric",
                                            min_val=0)
        route_name = get_asserted_nested_value(config, "route.name", "string_like",
                                             min_len=1)

        ### Check length of any config value
        waypoints = get_asserted_nested_value(config, "route.waypoints", "length",
                                            min_len=2, max_len=50)

        ### Check boolean value
        debug_mode = get_asserted_nested_value(config, "mission.debug", "boolean")
    """

    # Get the nested value
    value = get_nested_value(config, key_path, default_value)

    # If we got the default value and it's None, handle appropriately
    if value is default_value and default_value is None and assertion_type != "not_none":
        raise KeyError(f"Config key '{key_path}' not found and no default provided")

    # Create a descriptive name for error messages
    config_context = f"config.{key_path}"

    # Define mapping of assertion types to assertion functions
    assertion_functions = {
        "type": assert_type,
        "not_none": assert_not_none,
        "numeric": assert_numeric,
        "string_like": assert_string_like,
        "sequence": assert_sequence,
        "mapping": assert_mapping,
        "path": assert_path,
        "length": assert_length,
        "boolean": assert_boolean
    }

    # Apply the appropriate assertion based on assertion_type
    try:
        # Check if assertion_type is valid
        if assertion_type not in assertion_functions:
            valid_types = list(assertion_functions.keys())
            raise ValueError(f"Unknown assertion_type '{assertion_type}'. Valid options: {valid_types}")

        # Special case for "type" assertion which requires expected_type
        if assertion_type == "type" and 'expected_type' not in assertion_kwargs:
            raise ValueError("assertion_type 'type' requires 'expected_type' argument")

        # Execute the appropriate assertion function
        return assertion_functions[assertion_type](value, **assertion_kwargs)

    except TypeAssertionError as e:
        # Replace 'value' with the config context in the error message
        error_msg = str(e).replace("'value'", f"'{config_context}'")
        raise TypeAssertionError(error_msg) from e

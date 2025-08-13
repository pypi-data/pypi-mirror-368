# Import sensor configs

import logging
from dataclasses import dataclass
from typing import get_type_hints

from common.aggie_mqtt import subscribe, log_and_publish

from common.config_framework.load_configs import load_config

@dataclass
class BaseConfig:
    # Singleton registry: {(cls, config_filename, section): instance}
    _instances = {}
    """
    Base configuration class for loading and updating config files.
    Automatically validates and assigns config values to attributes based on type hints.
    Uses class attribute 'section' and 'config_filename' if not provided in __init__.
    """
    def __new__(cls, config_filename=None, section=None, log_load_success=True, parent_chain=None):
        # Use class attribute 'config_filename' if not provided
        config_filename = config_filename if config_filename is not None else getattr(cls, 'config_filename', None)
        section = section if section is not None else getattr(cls, 'section', None)
        key = (cls, str(config_filename), str(section))
        if key in cls._instances:
            return cls._instances[key]
        instance = super().__new__(cls)
        cls._instances[key] = instance
        return instance

    def __init__(self, config_filename=None, section=None, log_load_success=True, parent_chain=None):
        # Prevent re-initialization of singleton
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        # Use class attribute 'config_filename' if not provided
        self.config_filename = config_filename if config_filename is not None else getattr(self.__class__, 'config_filename', None)
        # Use class attribute 'section' if not provided
        self.section = section if section is not None else getattr(self.__class__, 'section', None)
        self.logger = logging.getLogger("config")
        self.logger.debug("Initializing %s with config_filename='%s' and section='%s'",
                         self.__class__.__name__, self.config_filename, self.section)
        self.data = {}
        self.log_load_success = log_load_success
        self._parent_chain = parent_chain or []

        subscribe(topic="system/configs/reload/commands", callback=self._mqtt_reload)
        subscribe(topic="system/config/set/commands", callback=self._mqtt_set_config)
        self.load(parent_chain=self._parent_chain)  # Load config on initialization

    def __str__(self):
        """
        String representation of the config object showing all of its attributes.
        """
        return f"{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.to_dict().items())})"

    def _mqtt_reload(self, topic: str, data: str | dict):
        """
        Reload the configuration when the MQTT topic is triggered.
        """
        self.logger.info("[{}] Reloading config='{}' section='{}'",
                         self.__class__.__name__, self.config_filename, self.section)
        try:
            self.load(parent_chain=self._parent_chain)
            log_and_publish(topic, f"Configuration reloaded successfully by {self.__class__.__name__} (id={id(self)}).")
        except Exception as e:
            log_and_publish(topic, f"Error reloading configuration: {e}")
            self.logger.error("Error reloading %s configuration: %s", self.config_filename,e)

    def _mqtt_set_config(self, topic: str, data):
        """
        Handle MQTT set config command. No type coercion; value is passed as-is to set_and_update.
        """
        try:
            # If data is a string, split it
            if isinstance(data, str):
                parts = data.strip().split(" ", 1)
                if len(parts) != 2:
                    raise ValueError("Expected 'key_path new_value'")
                key_path, new_value = parts
            else:
                key_path, new_value = data
            # Get config name from key_path
            if '.' not in key_path:
                raise ValueError("Invalid key_path format. Expected 'config_name.key_path new_value'. Need at least one dot ('.').")

            parts = key_path.split('.')
            config_name = parts[0]
            rest = parts[1:]

            # Check if this config instance matches the config_name
            if str(self.config_filename) != config_name:
                return  # Not for this config

            # If section is set, check if it matches the next part
            if self.section:
                if not rest or rest[0] != str(self.section):
                    return  # Not for this section
                # Remove section from key_path
                key_path_for_update = '.'.join(rest[1:])
            else:
                key_path_for_update = '.'.join(rest)

            if not key_path_for_update:
                raise ValueError("No key specified after config and section.")

            self.logger.info("[{}] Setting config='{}' section='{}' key_path='{}' to='{}'",
                             self.__class__.__name__, config_name, self.section, key_path_for_update, new_value)

            if self.set_and_update(config_file=config_name, key_path=key_path_for_update, new_value=new_value, prepend_section=True, archive=False):
                log_and_publish(topic, f"Configuration '{key_path}' set to '{new_value}'.")
            else:
                log_and_publish(topic, "Failed to set configuration '{key_path}'.")

        except ValueError as e:
            msg = (
                f"Invalid command format in {self.__class__.__name__} "
                f"(config='{self.config_filename}', section='{self.section}'). "
                f"Use 'key_path new_value'. {e}"
            )
            self.logger.error(msg)
            log_and_publish(topic, msg)

    @classmethod
    def _cast_value_to_type(cls, attr: str, value):
        """
        Attempt to cast the value to the type hint for the given attribute.
        Returns the cast value if possible, otherwise raises ValueError.
        """
        from typing import get_origin, get_args, Union
        import tomllib
        hints = get_type_hints(cls)
        expected_type = hints.get(attr, None)
        if expected_type is None:
            return value  # No type hint, return as is
        origin = get_origin(expected_type)
        args = get_args(expected_type)
        # Handle Union types (PEP 604)
        try:
            from types import UnionType
        except ImportError:
            UnionType = None
        if origin is Union or (UnionType is not None and origin is UnionType):
            for typ in args:
                try:
                    return cls._cast_single_type(typ, value)
                except Exception:
                    continue
            raise ValueError(f"Cannot cast value '{value}' to any type in {expected_type}")
        return cls._cast_single_type(expected_type, value)

    @staticmethod
    def _cast_single_type(typ, value):
        import tomllib
        # Handle bool
        if typ is bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                if value.lower() in ("true", "1", "yes", "on"):
                    return True
                if value.lower() in ("false", "0", "no", "off"):
                    return False
            raise ValueError(f"Cannot cast '{value}' to bool")
        # Handle int
        if typ is int:
            return int(value)
        # Handle float
        if typ is float:
            return float(value)
        # Handle str
        if typ is str:
            return str(value)
        # Handle list/dict (parse as TOML if string)
        if typ in (list, dict) or str(typ).startswith('list') or str(typ).startswith('dict'):
            if isinstance(value, (list, dict)):
                return value
            if isinstance(value, str):
                parsed = tomllib.loads(f"val = {value}")
                return parsed['val']
            raise ValueError(f"Cannot cast '{value}' to {typ}")
        # Fallback: try direct construction
        return typ(value)

    def __contains__(self, key):
        """
        Allow use of 'in' operator to check if a config attribute exists.
        """
        return hasattr(self, key)

    def __getitem__(self, key):
        """
        Allow dict-like access to config attributes.
        """
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key} not found in {self.__class__.__name__}")

    def to_dict(self):
        """
        Convert the config object to a dictionary representation.
        """
        result = {}
        hints = get_type_hints(self.__class__)
        for key in hints:
            if key.startswith('_'):
                continue
            value = getattr(self, key, None)
            if isinstance(value, BaseConfig):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    def load(self, parent_chain=None):
        """
        Load the configuration from file and assign values to attributes. No type coercion is performed.
        """
        if self.config_filename is None:
            raise ValueError(f"config_filename must be set for {self.__class__.__name__}")
        self.logger.debug("Loading %s configuration.", self.config_filename)
        old_config = self.data.copy() if isinstance(self.data, dict) else {}
        config = self._load_config_file()
        self.data = config
        self._log_config_diff(old_config, config)
        self._assign_config_attributes(config, parent_chain)
        if self.log_load_success and self.config_filename is not None:
            self.logger.debug("%s configuration loaded successfully.", self.config_filename.capitalize())

    def _load_config_file(self):
        """Internal: Load the config file using load_config utility."""
        if self.config_filename is None:
            raise ValueError(f"config_filename must be set for {self.__class__.__name__}")
        return load_config(self.config_filename, key_path=self.section)

    def _assign_config_attributes(self, config, parent_chain=None):
        """Internal: Assign config values to attributes, handle defaults and nested configs."""
        hints = get_type_hints(self.__class__)
        for key, typ in hints.items():
            if key.startswith('_'):
                continue
            if self._handle_data_filename_default(key, config):
                continue
            if self._handle_port_autodetect(key, config):
                continue
            if key not in config:
                self._raise_missing_key(key, parent_chain)
            value = config[key]
            if self._is_nested_config(typ, value):
                obj = self._instantiate_nested_config(typ, value, key, parent_chain)
                setattr(self, key, obj)
            else:
                setattr(self, key, value)

    def _handle_data_filename_default(self, key, config):
        """Internal: Set default for data_filename if not present in config."""
        if key == 'data_filename' and key not in config:
            section = self.section or self.__class__.__name__.replace('Config', '').lower()
            default_filename = f"{section}_data"
            setattr(self, key, default_filename)
            return True
        return False

    def _handle_port_autodetect(self, key, config):
        """Internal: Auto-detect and set port if not present in config."""
        if key == 'port' and key not in config:
            device_name = getattr(self.__class__, 'usb_device_name', None) or self.section
            if device_name:
                try:
                    from common.usb_detect.usb_detect import USBManager
                    usb_manager = USBManager()
                    info = usb_manager.get_device_info(device_name)
                    if info and info.get('port'):
                        setattr(self, key, info['port'])
                        return True
                except Exception as e:
                    self.logger.warning("Could not auto-set port for %s: %s", device_name, e)
        return False

    def _raise_missing_key(self, key, parent_chain):
        chain = (parent_chain or []) + [key]
        chain_str = '.'.join(chain)
        raise TypeError(f"Missing key '{key}' in config for {self.__class__.__name__} (parent chain: {chain_str})")

    def _is_nested_config(self, typ, value):
        return (
            isinstance(typ, type)
            and issubclass(typ, BaseConfig)
            and isinstance(value, dict)
        )

    def _instantiate_nested_config(self, typ, value, key, parent_chain):
        config_filename = getattr(typ, 'config_filename', None)
        section = getattr(typ, 'section', None)
        obj = typ(
            config_filename=config_filename,
            section=section,
            log_load_success=False,
            parent_chain=(parent_chain or []) + [key]
        )
        for subkey, subval in value.items():
            setattr(obj, subkey, subval)
        return obj

    def _log_config_diff(self, old, new, prefix=""):
        """
        Log the differences between two config dicts.
        """
        added = set(new) - set(old)
        removed = set(old) - set(new)
        changed = {k for k in new if k in old and new[k] != old[k]}
        for k in added:
            self.logger.debug("Config added: %s = %r", prefix + k, new[k])
        for k in removed:
            self.logger.debug("Config removed: %s (was %r)", prefix + k, old[k])
        for k in changed:
            if isinstance(new[k], dict) and isinstance(old[k], dict):
                self._log_config_diff(old[k], new[k], prefix=prefix + k + ".")
            else:
                self.logger.debug("Config changed: %s: %r -> %r", prefix + k, old[k], new[k])

    def set_and_update(self, key_path, new_value, config_file:str|None=None, archive=True, compress=False, prepend_section=True) -> bool:
        """
        Update a specific key in the config file and reload the config object.

        Args:
            key_path (str): Dot-separated path to the key to update (relative to section, if set)
            new_value (Any): The new value to set
            archive (bool): Whether to archive the config before updating
            compress (bool): Whether to compress the archive

        Returns:
            bool: True if update was successful, False otherwise
        """
        from .load_configs import update_config
        # Use optional config_file if provided, otherwise use class attribute
        if config_file is None:
            config_file = self.config_filename
        if config_file is None:
            raise ValueError(f"config_filename must be set for {self.__class__.__name__}")
        # If section is set, prepend it to the key_path (unless told not to)
        if prepend_section and self.section:
            full_key_path = f"{self.section}.{key_path}"
        else:
            full_key_path = key_path

        # Try to cast the value to the correct type if possible
        attr = key_path.split('.')[-1]
        try:
            cast_value = self._cast_value_to_type(attr, new_value)
        except ValueError:
            from typing import get_type_hints
            self.logger.error("Failed to cast '%s' to type '%s' for '%s' in %s. Not updating config file.",
                              new_value, get_type_hints(self.__class__).get(attr, 'unknown'), key_path, self.__class__.__name__)
            return False  # If casting fails, do not update

        result = update_config(config_file, full_key_path, cast_value, archive=archive, compress=compress)
        self.load()  # Reload to reflect changes
        return result

    def update_config_file(self, archive=True, compress=False):
        """
        Update the config file so that all values match the current in-memory state.

        Args:
            archive (bool): Whether to archive the config before updating
            compress (bool): Whether to compress the archive

        Returns:
            None
        """
        from .load_configs import update_config
        if self.config_filename is None:
            raise ValueError("config_filename must be set for %s", self.__class__.__name__)
        hints = get_type_hints(self.__class__)
        for key in hints:
            if key.startswith('_'):
                continue
            value = getattr(self, key, None)
            # If section is set, prepend it to the key_path
            full_key_path = f"{self.section}.{key}" if self.section else key
            update_config(self.config_filename, full_key_path, value, archive=archive, compress=compress)
        self.logger.debug("%s configuration updated successfully.", self.config_filename.capitalize())

"""Module containing ConfigManager class"""
import tomllib
from pathlib import Path
from typing import Any, List
import datetime
import shutil
import re
import gzip
from logging import getLogger

from common.utils import from_root

class ConfigLoaderBase:
    """Base class for configuration loading with lazy-loaded configurations and logger."""

    _project_root = None
    _configs_dict = None
    _config_logger = None

    @classmethod
    def _get_project_root(cls):
        """Get project root, determining it if it doesn't exist."""
        if cls._project_root is None:
            cls._project_root = from_root(".")
        return cls._project_root

    @classmethod
    def _get_configs_dict(cls) -> dict:
        """Get configs dictionary, building it if it doesn't exist."""
        if cls._configs_dict is None:
            project_root = cls._get_project_root()
            cls._configs_dict = {}
            for path in project_root.rglob("*.toml"):
                cls._configs_dict[path.stem] = path
                cls._configs_dict[path.name] = path
        return cls._configs_dict


class ConfigManager(ConfigLoaderBase):
    """
    Stateless configuration manager class for direct file operations.
    """

    @classmethod
    def validate_toml_value(cls, key: str, value) -> tuple[bool, bool]:
        """
        Validate that a key/value pair can be represented as valid TOML.
        Returns (True, needs_quotes) if valid, raises ValueError if not.
        """
        import tomllib
        if isinstance(value, str):
            try:
                tomllib.loads(f"{key} = {value}")
                return True, False  # Valid unquoted
            except Exception:
                try:
                    tomllib.loads(f'{key} = "{value}"')
                    return True, True  # Valid only quoted
                except Exception as e:
                    raise ValueError(f"Invalid TOML value: {value!r} for key {key}: {e}")
        else:
            import toml
            snippet = toml.dumps({key: value})
            try:
                tomllib.loads(snippet)
                return True, False
            except Exception as e:
                raise ValueError(f"Invalid TOML value: {value!r} for key {key}: {e}")

    @classmethod
    def get_nested_value(cls, config: dict, key_path: str, default_value: Any = None) -> dict | None | Any:
        """
        Access a nested dictionary value using a dot-separated string path.

        Args:
            config (dict): The dictionary to access
            key_path (str): Dot-separated path (e.g., "main.sys.logging")
            default_value: Value to return if path doesn't exist

        Returns:
            The value at the specified path or default_value if the path doesn't exist
        """
        if not key_path:
            raise KeyError(f"key_path cannot be empty, got: '{key_path}'")

        keys = key_path.split('.')
        result = config

        for key in keys:
            if isinstance(result, dict) and key in result:
                result = result[key]
            else:
                return default_value

        return result

    @classmethod
    def set_nested_value(cls, config: dict, key_path: str, value) -> dict:
        """
        Set a value in a nested dictionary using a dot-separated string path.
        Creates intermediate dictionaries if they don't exist. Validates TOML value before setting.

        Args:
            config (dict): The dictionary to modify
            key_path (str): Dot-separated path (e.g., "main.sys.logging")
            value: The value to set at the specified path

        Returns:
            The modified dictionary
        """
        keys = key_path.split('.')
        cls.validate_toml_value(keys[-1], value)  # Only for validation; quoting is handled in update_config
        current = config
        for _, key in enumerate(keys[:-1]):
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        return config

    @classmethod
    def load_config(cls, config_name: str | Path, key_path: str | None = None) -> dict:
        """
        Load configuration from file (always from disk).

        Args:
            config_name (str|Path): name of config file or path to the file to read the config from
            key_path (str|None): key_path to select the data from in the format of "section.subsection.subsection"

        Returns:
            dict: Configuration data
        """
        configs_dict = cls._get_configs_dict()

        if isinstance(config_name, Path):
            config_name = str(config_name.stem)

        config_filename = configs_dict.get(config_name)
        if config_filename is None:
            raise FileNotFoundError(f"Configuration file '{config_name}' not found in {cls._get_project_root()}")
        with open(config_filename, "rb") as f:
            base_config = tomllib.load(f)

        if key_path is None:
            return base_config

        data = cls.get_nested_value(base_config, key_path=key_path)

        if isinstance(data, dict):
            # If the data is a dictionary, return it as is
            return data

        raise ValueError(f"Key path '{key_path}' does not point to a dictionary in the configuration file '{config_name}'.")


    @classmethod
    def archive_config(cls, config_path: str | Path, compress: bool = True) -> Path | None:
        """
        Archives config with timestamp appended to filename in a config_archive subdirectory.
        Optionally compresses the file to minimize size.

        Args:
            config_path: Path to the configuration file
            compress: Whether to compress the archived file (default: True)

        Returns:
            Path to the archived file or None if the path is invalid
        """

        if isinstance(config_path, str):
            config_path = Path(config_path)

        # Create config_archive directory if it doesn't exist
        archive_dir = config_path.parent.joinpath("config_archive")
        archive_dir.mkdir(exist_ok=True)

        # Generate timestamped filename
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        if compress:
            # Add .gz extension for compressed files
            new_config_name = f"{timestamp}_{config_path.name}.gz"
            new_config_path = archive_dir.joinpath(new_config_name)

            # Compress the file
            with open(config_path, 'rb') as f_in:
                with gzip.open(new_config_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            new_config_name = f"{timestamp}_{config_path.name}"
            new_config_path = archive_dir.joinpath(new_config_name)
            shutil.copy2(config_path, new_config_path)

        return new_config_path

    @classmethod
    def _validate_and_get_config_path(cls, config_path: str | Path) -> Path | None:
        """
        Validates and converts the config path to a Path object.

        Args:
            config_path: Path to the configuration file as string or Path

        Returns:
            Path object or None if validation fails
        """

        if isinstance(config_path, str):
            return Path(config_path)

        return config_path

    @classmethod
    def _find_archive_version(cls, archive_dir: Path, base_name: str, version: str | None = None) -> Path | None:
        """
        Finds the appropriate archived version to restore.

        Args:
            archive_dir: Directory containing archived configs
            base_name: Base name of the config file
            version: Specific version timestamp to restore

        Returns:
            Path to the archived file to restore or None if not found
        """
        # Find archived versions
        archived_files = list(archive_dir.glob(f"*_{base_name}*"))

        if not archived_files:
            return None

        # Sort by timestamp (newest first)
        archived_files.sort(reverse=True)

        # Select version to restore
        if version:
            for file in archived_files:
                if file.name.startswith(f"{version}_"):
                    return file
            return None

        return archived_files[0]

    @classmethod
    def _create_backup(cls, config_path: Path, archive_dir: Path, compress: bool = False) -> Path:
        """
        Creates a backup of the current config before restoring.

        Args:
            config_path: Path to the configuration file
            archive_dir: Directory to store the backup
            compress: Whether to compress the backup

        Returns:
            Path to the backup file
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = config_path.name

        if compress:
            # Compressed backup
            backup_path = archive_dir.joinpath(f"pre_restore_{timestamp}_{base_name}.gz")
            with open(config_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            # Simple copy backup
            backup_path = archive_dir.joinpath(f"pre_restore_{timestamp}_{base_name}")
            shutil.copy2(config_path, backup_path)

        return backup_path

    @classmethod
    def _restore_file(cls, source_path: Path, target_path: Path) -> None:
        """
        Restores a file from source to target, handling compression if needed.

        Args:
            source_path: Path to the source file
            target_path: Path where the file should be restored
        """
        if source_path.name.endswith('.gz'):
            with gzip.open(source_path, 'rb') as f_in:
                with open(target_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(source_path, target_path)

    @classmethod
    def restore_config(cls, config_path: str | Path, version: str | None = None, compress_backup: bool = False) -> bool:
        """
        Restores a configuration file from archive.

        Args:
            config_path: Path to the current configuration file
            version: Specific version timestamp (default: most recent)
            compress_backup: Whether to compress the pre-restore backup (default: False)

        Returns:
            True if restoration was successful, False otherwise
        """
        # Validate and convert path
        validated_path = cls._validate_and_get_config_path(config_path)
        if validated_path is None:
            return False

        # Check if archive directory exists
        archive_dir = validated_path.parent.joinpath("config_archive")
        if not archive_dir.exists():
            return False

        # Find the version to restore
        file_to_restore = cls._find_archive_version(
            archive_dir,
            validated_path.name,
            version
        )
        if file_to_restore is None:
            return False

        # Create backup before restoring
        cls._create_backup(validated_path, archive_dir, compress_backup)

        # Restore the file
        cls._restore_file(file_to_restore, validated_path)

        return True

    @classmethod
    def list_archived_configs(cls, config_path: str | Path) -> List[str]:
        """
        Lists all archived versions of a configuration file.

        Args:
            config_path: Path to the configuration file

        Returns:
            List of archived versions with timestamps
        """

        if isinstance(config_path, (str, Path)):
            if isinstance(config_path, str):
                config_path = Path(config_path)

            archive_dir = config_path.parent.joinpath("config_archive")

            if not archive_dir.exists():
                return []

            base_name = config_path.name

            # Find all archived versions of this file
            archived_files = []
            for ext in ['', '.gz']:
                pattern = f"*_{base_name}{ext}"
                archived_files.extend(list(archive_dir.glob(pattern)))

            # Sort by timestamp (newest first)
            archived_files.sort(reverse=True)

            # Format the results
            result = []
            for file in archived_files:
                parts = file.name.split('_')
                timestamp = "_".join(parts[:2])
                compressed = file.name.endswith('.gz')
                size = file.stat().st_size
                result.append({
                    'timestamp': timestamp,
                    'filename': file.name,
                    'compressed': compressed,
                    'size': size,
                    'path': str(file)
                })

            return result

        return []

    @classmethod
    def _find_config_file(cls, config_name: str) -> Path | None:
        """
        Finds the configuration file path for a given config name.

        Args:
            config_name: Name of the configuration file

        Returns:
            Path to the configuration file or None if not found
        """
        configs_dict = cls._get_configs_dict()
        config_path = configs_dict.get(config_name)
        if config_path is None:
            return None
        return config_path

    @classmethod
    def _find_key_line_number(cls, lines: list[str], key_path: str) -> tuple[int | None, str | None]:
        """
        Finds the line number in the file that contains the key to update, section-aware.

        Args:
            lines: List of lines from the configuration file
            key_path: Dot-separated path to the key to update (e.g., section.key)

        Returns:
            (line number, subkey) tuple or (None, None) if not found. subkey is None for top-level, or the nested key for inline tables.
        """
        # Always search for the top-level key, regardless of subkey
        rest = None
        if '.' in key_path:
            section, rest = key_path.split('.', 1)
            if '.' in rest:
                key, subkey = rest.split('.', 1)
            else:
                key, subkey = rest, None
        else:
            section, key, subkey = None, key_path, None

        # If section looks like a key (no section in TOML), treat as key
        if section and not any(line.strip().startswith(f'[{section}]') for line in lines):
            key = section
            subkey = rest
            section = None

        current_section = None
        section_pattern = re.compile(r'^\s*\[([\w_]+)\]')
        key_pattern = re.compile(r'^\s*([\w_]+)\s*=')

        for i, line in enumerate(lines):
            # Detect section headers
            section_match = section_pattern.match(line)
            if section_match:
                current_section = section_match.group(1)
                continue
            # Only look for the key if we're in the right section (or no section specified)
            if (section is None or current_section == section):
                key_match = key_pattern.match(line)
                if key_match and key_match.group(1) == key:
                    return (i, subkey)
        return (None, None)

    @classmethod
    def _update_value_in_line(cls, line: str, new_value: Any, subkey: str | None = None) -> str | None:
        """
        Updates the value in a line, preserving the quote style if present and any spaces before comments.
        Handles quoted strings, numbers, booleans, lists, and dicts. Preserves the original line ending.
        """
        import ast
        # Detect original line ending
        line_ending = ''
        if line.endswith('\r\n'):
            line_ending = '\r\n'
            line = line[:-2]
        elif line.endswith('\n'):
            line_ending = '\n'
            line = line[:-1]

        # If the new value is a list, format as TOML array
        def format_toml_list(val):
            # If already a string that looks like a TOML list, keep as is
            if isinstance(val, str):
                try:
                    parsed = ast.literal_eval(val)
                    if isinstance(parsed, list):
                        val = parsed
                except Exception:
                    pass
            if isinstance(val, list):
                def _toml_repr(x):
                    if isinstance(x, dict):
                        return format_toml_dict(x)
                    elif isinstance(x, str):
                        return '"' + x.replace('"', '\"') + '"'
                    elif isinstance(x, list):
                        return format_toml_list(x)
                    else:
                        return repr(x)
                return '[' + ', '.join(_toml_repr(x) for x in val) + ']'
            return val

        # If the new value is a dict, format as TOML inline table
        def format_toml_dict(val):
            if isinstance(val, str):
                try:
                    parsed = ast.literal_eval(val)
                    if isinstance(parsed, dict):
                        val = parsed
                except Exception:
                    pass
            if isinstance(val, dict):
                def _toml_kv(k, v):
                    if isinstance(v, str):
                        return f'{k} = "{v}"'
                    elif isinstance(v, bool):
                        return f'{k} = {str(v).lower()}'
                    elif isinstance(v, (int, float)):
                        return f'{k} = {v}'
                    elif isinstance(v, list):
                        return f'{k} = {format_toml_list(v)}'
                    elif isinstance(v, dict):
                        return f'{k} = {format_toml_dict(v)}'
                    else:
                        return f'{k} = "{str(v)}"'
                return '{' + ', '.join(_toml_kv(k, v) for k, v in val.items()) + '}'
            return val

        # If subkey is provided, update a value inside an inline table
        if subkey:
            # Match: key = { ... } [spaces][# comment]
            match = re.match(r'^(\s*[\w_]+\s*=\s*)({.*?})(\s*)(#.*)?$', line)
            if match:
                prefix, old_dict_str, spaces, comment = match.groups()
                comment = comment or ''
                dict_val = None
                # Try parsing as Python dict first
                try:
                    dict_val = ast.literal_eval(old_dict_str.replace('=', ':'))
                except Exception:
                    pass
                # If that fails, try parsing as TOML
                if dict_val is None:
                    try:
                        import tomllib
                        fake_toml = f"val = {old_dict_str}"
                        dict_val = tomllib.loads(fake_toml)['val']
                    except Exception:
                        return None
                # Update the subkey and write back as TOML inline table
                dict_val[subkey] = new_value
                # Pass raw value to formatter, let formatter handle quoting
                formatted_value = format_toml_dict(dict_val)
                return f"{prefix}{formatted_value}{spaces}{comment}" + line_ending
        # Try double quotes
        double_quote_match = re.search(r'"([^"]*)"', line)
        if double_quote_match and not isinstance(new_value, (list, dict)):
            old_value = double_quote_match.group(1)
            return line.replace(f'"{old_value}"', f'"{new_value}"') + line_ending
        # Try single quotes
        single_quote_match = re.search(r"'([^']*)'", line)
        if single_quote_match and not isinstance(new_value, (list, dict)):
            old_value = single_quote_match.group(1)
            return line.replace(f"'{old_value}'", f"'{new_value}'") + line_ending
        # Try unquoted value (number, boolean, list, dict, etc.)
        # Match: key = value [spaces][# comment]
        match = re.match(r'^(\s*[\w_]+\s*=\s*)([^#]+?)(\s*)(#.*)?$', line)
        if match:
            prefix, old_value, spaces, comment = match.groups()
            comment = comment or ''
            # If new_value is a list, format as TOML array
            if isinstance(new_value, list) or (isinstance(new_value, str) and new_value.strip().startswith('[') and new_value.strip().endswith(']')):
                formatted_value = format_toml_list(new_value)
            # If new_value is a dict, format as TOML inline table
            elif isinstance(new_value, dict) or (isinstance(new_value, str) and new_value.strip().startswith('{') and new_value.strip().endswith('}')):
                formatted_value = format_toml_dict(new_value)
            else:
                formatted_value = str(new_value)
            return f"{prefix}{formatted_value}{spaces}{comment}" + line_ending
        return None

    @classmethod
    def update_config(cls, config_name: str, key_path: str, new_value: Any, archive: bool = True, compress: bool = False) -> bool:  # pylint: disable=too-many-arguments, too-many-positional-arguments
        """
        Updates a configuration file by changing the value at the specified key path.
        Optionally archives the configuration before making changes.

        Args:
            config_name: Name of the configuration file
            key_path: Dot-separated path to the key to update
            new_value: New value to set
            archive: Whether to archive the config before updating (default: True)
            compress: Whether to compress the archived file (default: False)

        Returns:
            True if update was successful, False otherwise
        """
        logger = getLogger('config')
        logger.debug(f"[update_config] Called with config_name={config_name}, key_path={key_path}, new_value={new_value}, archive={archive}, compress={compress}")
        # Find the configuration file
        config_path = cls._find_config_file(config_name)
        logger.debug(f"[update_config] Resolved config_path: {config_path}")
        if config_path is None:
            logger.error(f"[update_config] Could not find config file for name: {config_name}")
            return False

        # Validate TOML value before updating and determine if quoting is needed
        # For inline table subkeys, validate the value for the subkey
        if '.' in key_path:
            top_key = key_path.split('.', 1)[0]
            subkey = key_path.split('.', 1)[1]
            key_for_toml = subkey.split('.')[-1]
        else:
            top_key = key_path
            subkey = None
            key_for_toml = key_path
        try:
            _, needs_quotes = cls.validate_toml_value(key_for_toml, new_value)
        except Exception as e:
            logger.error(f"[update_config] Refusing to write invalid TOML value: {new_value!r} for key {key_for_toml}: {e}")
            return False

        # Archive the configuration file before making changes
        if archive:
            archive_path = cls.archive_config(config_path, compress)
            logger.debug(f"[update_config] Archived config to: {archive_path}")

        # Read the file content
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            logger.debug(f"[update_config] Read {len(lines)} lines from config file.")
        except Exception as e:
            logger.error(f"[update_config] Failed to read config file: {e}")
            return False

        # Find the line containing the key
        line_num, subkey = cls._find_key_line_number(lines, key_path)
        logger.debug(f"[update_config] Line number for key_path '{key_path}': {line_num}, subkey: {subkey}")
        if line_num is None:
            logger.error(f"[update_config] Could not find line for key_path: {key_path}")
            return False

        # Update the value in the line, quoting if needed
        if subkey is not None:
            value_to_write = new_value  # never quote for subkey updates
        else:
            value_to_write = f'"{new_value}"' if needs_quotes and isinstance(new_value, str) else new_value
        new_line = cls._update_value_in_line(lines[line_num], value_to_write, subkey=subkey)
        logger.debug(f"[update_config] Old line: {lines[line_num].rstrip()}")
        logger.debug(f"[update_config] New line: {new_line.rstrip() if new_line else None}")
        if new_line is None:
            logger.error(f"[update_config] Could not update value in line for key_path: {key_path}")
            return False

        # Write the updated content back to the file
        lines[line_num] = new_line
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            logger.debug(f"[update_config] Successfully wrote updated config file.")
        except Exception as e:
            logger.error(f"[update_config] Failed to write updated config file: {e}")
            return False

        return True

    @classmethod
    def get_available_configs(cls) -> dict:
        """
        Get dictionary of available configuration files.

        Returns:
            dict: Dictionary mapping config names to file paths
        """
        return cls._get_configs_dict().copy()

    @classmethod
    def refresh_configs_dict(cls):
        """Force refresh of the configs dictionary (useful if new config files are added)."""
        cls._configs_dict = None
        cls._get_configs_dict()

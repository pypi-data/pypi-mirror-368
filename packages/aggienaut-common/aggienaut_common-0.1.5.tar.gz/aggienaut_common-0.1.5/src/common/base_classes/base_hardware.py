from abc import ABC, abstractmethod
import logging
import struct
from pathlib import Path

from .configs import BaseConfig, GeneralHardwareConfig
from typing import Generic, TypeVar
from common.utils import from_root

# --- New Abstract Base Classes ---
class BaseHardwareData(ABC):
    """Abstract base class for all hardware data objects."""
    FIELD_DEFS: list[tuple[str, str]]|None = None
    FIELDS: list[str]|None = None

    def __str__(self):
        if self.FIELD_DEFS is not None:
            field_str = ', '.join(f"{name}={getattr(self, name, None)}" for name, _ in self.FIELD_DEFS)
        else:
            field_str = ', '.join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({field_str})"

    def to_tuple(self) -> tuple:
        """
        Return data as tuple matching FIELD_DEFS order.
        Handles special cases for fixed-length strings (e.g., 'str:16').
        """
        if self.FIELD_DEFS is None:
            raise NotImplementedError(f"FIELD_DEFS must be defined in {self.__class__.__name__} for to_tuple() to work.")
        result = []
        for name, ftype in self.FIELD_DEFS:
            value = getattr(self, name)
            if ftype.startswith('str:'):
                strlen = int(ftype.split(':')[1])
                # Ensure value is bytes of length strlen
                if isinstance(value, str):
                    value = value.encode('utf-8')[:strlen].ljust(strlen, b'\x00')
                elif isinstance(value, bytes):
                    value = value[:strlen].ljust(strlen, b'\x00')
                else:
                    value = b'\x00' * strlen
                result.append(value)
            else:
                result.append(value)
        return tuple(result)

    @classmethod
    def get_field_defs(cls):
        return cls.FIELD_DEFS

    @classmethod
    def get_fields(cls):
        if cls.FIELDS is not None:
            return cls.FIELDS
        if cls.FIELD_DEFS is not None and isinstance(cls.FIELD_DEFS, (list, tuple)):
            return [name for name, _ in cls.FIELD_DEFS]
        return None

# Human-readable type to struct format mapping
TYPE_TO_STRUCT = {
    'int8': 'b', 'uint8': 'B',
    'int16': 'h', 'uint16': 'H',
    'int32': 'i', 'uint32': 'I',
    'int64': 'q', 'uint64': 'Q',
    'float32': 'f', 'float64': 'd',
    'double': 'd',  # alias
    'char': 'c',
    'bool': '?',
    # 'str' will be handled specially below
}

def generate_struct_format(field_defs, endianness='<'):
    """
    Generate a struct format string from a list of (name, type) tuples.
    Supports types like 'str:20' for fixed-length strings.
    Example: [('t', 'int64'), ('state', 'str:10'), ...]
    """
    fmt = endianness
    for _, ftype in field_defs:
        if ftype.startswith('str:'):
            strlen = int(ftype.split(':')[1])
            fmt += f'{strlen}s'
        else:
            fmt += TYPE_TO_STRUCT[ftype]
    return fmt


ConfigT = TypeVar('ConfigT', bound='BaseConfig')

class BaseHardware(ABC, Generic[ConfigT]):
    """Abstract base class for all hardware threads."""
    FIELD_DEFS = None  # List of (name, type) tuples
    FIELDS = None      # List of field names
    STRUCT_FORMAT = None
    logger: logging.Logger
    base_config: GeneralHardwareConfig
    data: BaseHardwareData
    config: ConfigT

    def __init__(self):
        self.base_config = GeneralHardwareConfig()
        self.base_config.load()
        # config will be set in child class

    @abstractmethod
    def collect(self) -> None:
        """Collect data from the sensor."""
        pass

    @abstractmethod
    def thread_work(self):
        """Main thread loop for the sensor."""
        pass

    def reload_config(self):
        self.config.update()

    def _save_binary_data(self, data_dir=None):
        field_defs = getattr(self.data, 'FIELD_DEFS', None)
        struct_format = getattr(self.data, 'STRUCT_FORMAT', None)
        fields = getattr(self, 'FIELDS', None)
        if field_defs is not None and (struct_format is None or fields is None):
            struct_format = generate_struct_format(field_defs)
            fields = [name for name, _ in field_defs]
        if struct_format is None or fields is None:
            raise NotImplementedError("STRUCT_FORMAT and FIELDS or FIELD_DEFS must be set in the child class.")
        if data_dir is None:
            # Try to get data_dir from config if available
            data_dir = self.base_config.data_dir
        data_dir = Path(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        # Try to get base filename from config if available
        base_filename = getattr(self, 'base_filename', self.__class__.__name__.lower())
        bin_file = data_dir / f'{base_filename}.bin'
        hdr_file = data_dir / f'{base_filename}.hdr'
        if not hdr_file.exists():
            with open(hdr_file, 'w') as f:
                f.write(f"sensor: {self.__class__.__name__.lower()}\nfields: {','.join(fields)}\nstruct: {struct_format}\n")
        packed = struct.pack(struct_format, *self.data.to_tuple())
        if self.logger is not None:
            self.logger.debug(f"Saving {self.__class__.__name__.lower()} data to {bin_file} with format {struct_format}")
        with open(bin_file, 'ab') as f:
            f.write(packed)

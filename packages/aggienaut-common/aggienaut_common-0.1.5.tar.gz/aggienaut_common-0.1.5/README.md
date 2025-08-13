# aggienaut-common

Repository containing the AggieNaut utilities - a collection of common modules and utilities for AggieNaut projects.

## Installation

### From Wheel (Recommended)

```bash
pip install aggienaut_common-0.1.0-py3-none-any.whl
```

### From Source

```bash
git clone https://github.com/Aggienaut-Apps/aggienaut-common.git
cd aggienaut-common
pip install .
```

### Development Installation

```bash
git clone https://github.com/Aggienaut-Apps/aggienaut-common.git
cd aggienaut-common
pip install -e .[dev]
```

## Building

To build the wheel package:

```bash
python -m build
```

This will create both a wheel (`.whl`) and source distribution (`.tar.gz`) in the `dist/` directory.

## Features

This package includes the following modules:

- **aggie_logging**: Logging utilities and configuration management
- **aggie_mqtt**: MQTT broker and messaging utilities
- **base_classes**: Base hardware and configuration classes
- **command**: Command handling utilities
- **config_framework**: Configuration management framework
- **power_board**: Power board control and management
- **serial_comms**: Serial communication utilities
- **thread_handling**: Thread management and safe sleep utilities
- **type_validation**: Type validation utilities
- **usb_detect**: USB device detection and management
- **utils**: General utility functions

## Dependencies

- `paho-mqtt>=1.6.0`
- `pyserial>=3.5`
- `toml>=0.10.2`

## License

MIT License (see LICENSE file)

"""USB device detection and management utilities.

This module provides classes and functions for managing USB devices, including
device detection, symbolic link creation/removal, and device status monitoring.
The main components are USBManager for overall device management and USBPort
for individual device representation and operations.
"""

import os
import subprocess
from logging import getLogger
from typing import Dict, Optional

from .configs import USBConfig
from common.errors import USBPortError

class USBManager:
    """Manager class for USB device operations"""

    def __init__(self):
        # Load device_map and other settings from usb.toml, [device_map] section
        self.config = USBConfig()
        self.logger = getLogger("usb_manager")

    def _execute_command(self, command: list, error_msg: str) -> None:
        """Execute a subprocess command with error handling"""
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise USBPortError(f"{error_msg}: {e}") from e

    def create_symlink_direct(self, target: str, link_path: str) -> str:
        """Create symlink directly (without sudo)"""
        if os.path.islink(link_path):
            os.unlink(link_path)
        elif os.path.exists(link_path):
            raise USBPortError(f"Path {link_path} exists but is not a symlink")

        os.symlink(target, link_path)
        self.logger.debug("Created symlink: %s -> %s", link_path, target)
        return link_path

    def create_symlink_with_sudo(self, target: str, link_path: str) -> str:
        """Create symlink using sudo"""
        if os.path.islink(link_path):
            self._execute_command(['sudo', 'rm', link_path], "Failed to remove existing symlink")
        elif os.path.exists(link_path):
            raise USBPortError(f"Path {link_path} exists but is not a symlink")

        self._execute_command(['sudo', 'ln', '-s', target, link_path], "Failed to create symlink with sudo")
        self.logger.debug("Created symlink: %s -> %s", link_path, target)
        return link_path

    def _remove_symlink_direct(self, link_path: str) -> bool:
        """Remove symlink directly (without sudo)"""
        if os.path.islink(link_path):
            os.unlink(link_path)
            self.logger.debug("Removed symlink: %s", link_path)
            return True
        return False

    def _remove_symlink_with_sudo(self, link_path: str) -> bool:
        """Remove symlink using sudo"""
        try:
            if os.path.islink(link_path):
                self._execute_command(['sudo', 'rm', link_path], "Failed to remove symlink with sudo")
                self.logger.debug("Removed symlink with sudo: %s", link_path)
                return True
            return False
        except USBPortError as e:
            self.logger.error("Error rempving symlink withn sudo: %s", e)
            return False

    def get_usb_path(self, device_path: str) -> Optional[str]:
        """Get USB path from device file path"""
        import pyudev

        context = pyudev.Context()

        try:
            device = pyudev.Devices.from_device_file(context, device_path)

            current = device
            while current and current.properties:
                if (current.subsystem == 'usb' and
                    current.device_type == 'usb_device' and
                    '-' in current.sys_name):
                    return current.sys_name
                current = current.parent

            return None

        except Exception as e:  #pylint:disable=broad-except
            self.logger.error("Error getting USB path: %s", e)
            return None

    def get_device_file_from_name(self, device_name: str) -> Optional[str]:
        """Get the actual device file path from device name"""
        import pyudev

        target_usb_path = self.config.device_map.get(device_name)
        if not target_usb_path:
            return None

        context = pyudev.Context()
        for device in context.list_devices(subsystem=self.config.device_subsystem):
            if device.device_node and device.device_node.startswith(self.config.device_node_prefix):
                current_usb_path = self.get_usb_path(device.device_node)
                if current_usb_path == target_usb_path:
                    return device.device_node

        return None

    def get_device_info(self, identifier: str) -> Optional[Dict[str, Optional[str]]]:
        """Get device info by name or path"""
        # If identifier is in device_map keys (it's a name)
        if identifier in self.config.device_map:
            usb_path = self.config.device_map[identifier]
            port = f"{self.config.symlink_dir.rstrip('/')}/{identifier}"
            return {
                'name': identifier,
                'usb_path': usb_path,
                'device_file': self.get_device_file_from_name(identifier),
                'port': port
            }

        # If identifier is a USB path, search through device_map values
        for device_name, usb_path in self.config.device_map.items():
            if usb_path == identifier:
                port = f"{self.config.symlink_dir.rstrip('/')}/{device_name}"
                return {
                    'name': device_name,
                    'usb_path': identifier,
                    'device_file': self.get_device_file_from_name(device_name),
                    'port': port
                }

        return None

    def create_all_symlinks(self, use_sudo: bool = False) -> Dict[str, str]:
        """Create symbolic links for all devices in device_map"""
        symlinks = {}
        errors = []

        self.logger.debug("Creating symbolic links for all USB devices...")

        for device_name in self.config.device_map.keys():
            try:
                port = USBPort.from_name(device_name, self)
                self.logger.debug("Got port = %s for device_name = %s", port, device_name)
                symlink_path = port.create_symlink(symlink_path=f"{self.config.symlink_dir.rstrip('/')}/{device_name}", use_sudo=use_sudo)
                self.logger.debug("Got %s for device name: %s", symlink_path, device_name)
                symlinks[device_name] = symlink_path
            except USBPortError as e:
                error_msg = f"Failed to create symlink for {device_name}: {e}"
                self.logger.warning("Warning: %s", error_msg)
                errors.append(error_msg)

        if errors:
            self.logger.debug("Completed with %s errors:", len(errors))
            for error in errors:
                self.logger.error("  - %s", error)
        else:
            self.logger.debug("Successfully created %s symbolic links!", len(symlinks))

        return symlinks

    def remove_all_symlinks(self, use_sudo: bool = False) -> None:
        """Remove all symbolic links for devices in device_map"""
        self.logger.debug("Removing symbolic links for all USB devices...")

        removed_count = 0
        for device_name in self.config.device_map.keys():
            symlink_path = f"{self.config.symlink_dir.rstrip('/')}/{device_name}"
            try:
                if use_sudo and os.geteuid() != 0:
                    if self._remove_symlink_with_sudo(symlink_path):
                        removed_count += 1
                else:
                    if self._remove_symlink_direct(symlink_path):
                        removed_count += 1
                    elif os.path.exists(symlink_path):
                        self.logger.warning("Warning: %s exists but is not a symlink", symlink_path)
            except PermissionError:
                error_msg = f"Permission denied removing {symlink_path}"
                if not use_sudo:
                    error_msg += ". Try with use_sudo=True"
                else:
                    error_msg += " even with sudo"
                self.logger.error(error_msg)
            except Exception as e:  #pylint:disable=broad-except
                self.logger.error("Error removing %s: %s", symlink_path, e)

        self.logger.debug("Removed %s symbolic links", removed_count)

    def list_current_devices(self) -> None:
        """List all currently connected devices and their status"""
        print("Current USB device status:")
        print("-" * 60)

        for device_name in self.config.device_map.keys():
            try:
                port = USBPort.from_name(device_name, self)
                symlink_path = f"{self.config.symlink_dir.rstrip('/')}/{device_name}"
                symlink_exists = os.path.islink(symlink_path)
                symlink_valid = symlink_exists and os.path.exists(symlink_path)

                print(f"{device_name:20} | {port.device_file:12} | Symlink: {symlink_valid}")

            except USBPortError:
                symlink_path = f"{self.config.symlink_dir.rstrip('/')}/{device_name}"
                symlink_exists = os.path.islink(symlink_path)
                print(f"{device_name:20} | NOT CONNECTED | Symlink: {symlink_exists}")

    def refresh_usb_symlinks(self, use_sudo: bool = False):
        """Refresh all USB symlinks by removing old ones and creating new ones"""
        self.remove_all_symlinks(use_sudo=use_sudo)
        self.create_all_symlinks(use_sudo=use_sudo)


class USBPort:
    """Represents a USB device with its associated name, USB path, and device file.

    Provides functionality to create symbolic links, check connection status,
    and refresh device information for USB devices managed by the system.
    """
    def __init__(self, name: str, path: str, device_file: str, manager: USBManager):
        """Initialize USBPort with name, USB path, device file path, and manager

        Args:
            name: Device name (e.g., 'sunsaver', 'aggienaut_radio')
            path: USB path (e.g., '1-1.2')
            device_file: Device file path (e.g., '/dev/ttyACM0')
            manager: USBManager instance
        """
        self.name = name
        self.path = path
        self.device_file = device_file
        self.manager = manager

    @classmethod
    def from_name(cls, device_name: str, manager: USBManager|None = None) -> 'USBPort':
        """Create USBPort instance from device name"""
        if manager is None:
            manager = USBManager()

        info = manager.get_device_info(device_name)
        if not info or not all([info['name'], info['usb_path'], info['device_file']]):
            raise USBPortError(f"Could not find complete USB device info for '{device_name}', {info = }")

        if info['name'] is None:
            raise USBPortError(f"Could not find device name for USB path '{info['usb_path']}'")
        if info['usb_path'] is None:
            raise USBPortError(f"Could not find USB path for device name '{info['name']}'")
        if info['device_file'] is None:
            raise USBPortError(f"Could not find device file for device name '{info['name']}'")

        return cls(
            name=info['name'],
            path=info['usb_path'],
            device_file=info['device_file'],
            manager=manager
        )

    @classmethod
    def from_usb_path(cls, usb_path: str, manager: USBManager|None = None) -> 'USBPort':
        """Create USBPort instance from USB path"""
        if manager is None:
            manager = USBManager()

        info = manager.get_device_info(usb_path)
        if not info or not all([info['name'], info['usb_path'], info['device_file']]):
            raise USBPortError(f"Could not find complete USB device info for USB path '{usb_path}'")

        if info['name'] is None:
            raise USBPortError(f"Could not find device name for USB path '{info['usb_path']}'")
        if info['usb_path'] is None:
            raise USBPortError(f"Could not find USB path for device name '{info['name']}'")
        if info['device_file'] is None:
            raise USBPortError(f"Could not find device file for device name '{info['name']}'")

        return cls(
            name=info['name'],
            path=info['usb_path'],
            device_file=info['device_file'],
            manager=manager
        )

    @classmethod
    def from_device_file(cls, device_file_path: str, manager: USBManager|None = None) -> 'USBPort':
        """Create USBPort instance from device file path"""
        if manager is None:
            manager = USBManager()

        usb_path = manager.get_usb_path(device_file_path)
        if not usb_path:
            raise USBPortError(f"Could not determine USB path for device file '{device_file_path}'")

        info = manager.get_device_info(usb_path)
        if not info or not all([info['name'], info['usb_path']]):
            raise USBPortError(f"Could not find complete USB device info for device file '{device_file_path}'")

        if info['name'] is None:
            raise USBPortError(f"Could not find device name for USB path '{info['usb_path']}'")
        if info['usb_path'] is None:
            raise USBPortError(f"Could not find USB path for device name '{info['name']}'")

        return cls(
            name=info['name'],
            path=info['usb_path'],
            device_file=device_file_path,
            manager=manager
        )

    def is_connected(self) -> bool:
        """Check if the USB device is currently connected"""
        current_device_file = self.manager.get_device_file_from_name(self.name)
        return current_device_file is not None

    def refresh(self) -> None:
        """Refresh the device_file path (useful if device was reconnected)"""
        device_file = self.manager.get_device_file_from_name(self.name)
        if not device_file:
            raise USBPortError(f"Could not refresh device file for '{self.name}' - device not found")
        self.device_file = device_file

    def create_symlink(self, symlink_path: str|None = None, use_sudo: bool = False) -> str:
        """Create a symbolic link for this device"""
        if symlink_path is None:
            symlink_path = f"{self.manager.config.symlink_dir.rstrip('/')}/{self.name}"

        try:
            if use_sudo and os.geteuid() != 0:
                return self.manager.create_symlink_with_sudo(self.device_file, symlink_path)

            return self.manager.create_symlink_direct(self.device_file, symlink_path)

        except PermissionError as e:
            error_msg = f"Permission denied creating symlink {symlink_path}"
            if not use_sudo:
                error_msg += ". Try with use_sudo=True or run as root."
            else:
                error_msg += " even with sudo."
            raise USBPortError(error_msg) from e
        except Exception as e:
            raise USBPortError(f"Failed to create symlink {symlink_path}: {e}") from e

    def __str__(self) -> str:
        return f"USBPort(name='{self.name}', path='{self.path}', device_file='{self.device_file}')"

    def __repr__(self) -> str:
        return self.__str__()


def refresh_symlinks(manager: USBManager|None = None, use_sudo:bool=True) -> None:
    """Refresh all symlinks in the given directory. Helper function for USBManager.refresh_usb_symlinks()"""
    if manager is None:
        manager = USBManager()
    manager.refresh_usb_symlinks(use_sudo=use_sudo)

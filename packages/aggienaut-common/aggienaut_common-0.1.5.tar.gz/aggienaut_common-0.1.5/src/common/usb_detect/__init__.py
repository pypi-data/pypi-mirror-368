"""Module for detecting USB devices."""

from .usb_detect import USBManager, refresh_symlinks

__all__ = ['USBManager', 'refresh_symlinks']

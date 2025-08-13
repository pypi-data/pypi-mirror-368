"""Module containing a safe sleep function that can be interrupted."""
import threading
import time

# Simple global variables instead of singleton
_exit_event = None  # pylint: disable=invalid-name
_lock = threading.Lock()  # pylint: disable=invalid-name

def set_exit_event(exit_event: threading.Event):
    """Set the exit event for safe sleep operations"""

    with _lock:
        _exit_event = exit_event

def safe_sleep(duration:int|float):
    """Global safe sleep function that can be interrupted. Returns True if exit was requested."""

    if duration <= 0:
        return False

    with _lock:
        current_exit_event = _exit_event

    if current_exit_event is not None:
        return current_exit_event.wait(duration)

    time.sleep(duration)
    return False

def should_exit():
    """Check if exit has been requested"""
    with _lock:
        return _exit_event is not None and _exit_event.is_set()

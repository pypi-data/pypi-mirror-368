# pylint: disable=invalid-name, unnecessary-pass
""" Module containing custom errors. """
import sys
from logging import getLogger


class LoggingMixin:
    """Mixin class that provides automatic logging functionality with lazy string formatting."""
    log_level = 'error'  # Default log level
    logger_name = 'system'  # Default logger name
    include_exc_info = True  # New attribute to control exc_info

    @classmethod
    def get_logger(cls):
        """Get the logger for this class."""
        return getLogger(cls.logger_name)

    def log_message(self, *args):
        """
        Log a message using the class name and configured log level.
        Only includes exception info if we're in an exception handler.
        """
        class_name = self.__class__.__name__
        logger = self.__class__.get_logger()
        log_method = getattr(logger, self.log_level)

        # Format the message
        if not args:
            formatted_message = class_name
        elif len(args) == 1:
            formatted_message = f"{class_name}: {args[0]}"
        else:
            all_args = " ".join(str(arg) for arg in args)
            formatted_message = f"{class_name}: {all_args}"

        # Only include exc_info if we're actually handling an exception
        current_exc = sys.exc_info()[1]
        use_exc_info = self.include_exc_info and (current_exc is not None)

        # Log the message
        log_method(formatted_message, exc_info=use_exc_info)

class BaseSystemError(LoggingMixin, Exception):
    """Base class for all system errors that automatically logs using the class name."""

    def __init__(self, *args):
        self.log_message(*args)
        super().__init__(*args)

class BaseSystemWarning(LoggingMixin, Warning):
    """Base class for all system warning that automatically logs using the class name."""
    log_level = 'warning'  # Override default log level

    def __init__(self, *args):
        self.log_message(*args)
        super().__init__(*args)

class ExitError(BaseSystemError):
    """Error raised when system exit fails."""
    log_level = "critical"
    pass

class SystemExitError(ExitError):
    """Error raised when system exit fails."""
    pass

class ScienceExitError(ExitError):
    """Error raised when science exit fails."""
    pass

class AggienautExitError(ExitError):
    """Error raised when Aggienaut exit fails."""
    pass

class RebootError(BaseSystemError):
    """Error raised when system reboot fails."""
    log_level = "critical"
    pass

class ShutdownError(BaseSystemError):
    """Error raised when system shutdown fails."""
    log_level = "critical"
    pass

class GPSError(BaseSystemError):
    """Error raised when GPS operations fail."""
    pass

class AISError(BaseSystemError):
    """Error raised when AIS operations fail."""
    pass

class PowerMonitorError(BaseSystemError):
    """Error raised when power monitoring fails."""
    pass

class NavigationError(BaseSystemError):
    """Error raised when navigation operations fail."""
    pass

class IridiumError(BaseSystemError):
    """Error raised when Iridium satellite communication fails."""
    pass

class CommandError(BaseSystemError):
    """Error raised when command execution fails."""
    logger_name = 'commands'
    pass

class ConfigError(BaseSystemError):
    """Error raised when configuration is invalid."""
    pass

class InvalidChannelError(BaseSystemError):
    """Error raised when an invalid channel is specified."""
    pass

class InvalidStateError(BaseSystemError):
    """Error raised when system is in an invalid state."""
    pass

class RadioError(BaseSystemError):
    """Error raised when radio operations fail."""
    pass

class CTDError(BaseSystemError):
    """Error raised when CTDE operations fail."""
    pass

class USBPortError(BaseSystemError):
    """Error raised when USB port cannot be found or accessed."""
    pass

class NavigationPicoConnectionError(BaseSystemError):
    """Raised when NavigationPico cannot connect after all retries."""
    pass

class TypeAssertionError(BaseSystemError, AssertionError, TypeError):
    """Error raised when type validation fails."""
    logger_name = 'type_validation'
    pass

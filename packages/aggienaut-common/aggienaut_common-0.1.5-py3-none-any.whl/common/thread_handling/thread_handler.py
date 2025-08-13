"""Module containing the ThreadHandler class."""
import threading
import signal
import logging

from common.errors import RebootError, ShutdownError, ExitError
from common.thread_handling.safe_sleep import set_exit_event

class LoggerSetup:  # pylint: disable=too-few-public-methods
    """Centralized logger setup to avoid code execution on import"""
    _logger = None

    @classmethod
    def get_logger(cls):
        """"Get the logger instance"""
        if cls._logger is None:
            cls._logger = logging.getLogger("system")
        return cls._logger

class ThreadHandler:
    """Class to manage threads and handle shutdowns"""
    def __init__(self):
        self.threads: list[threading.Thread] = []
        self.exit_event = threading.Event()  # Global exit signal
        self.error_occurred = False
        self.error_message = ""
        self.exception_queue = []  # Store exceptions from threads
        self.exception_lock = threading.Lock()
        self.logger = LoggerSetup.get_logger()

        set_exit_event(self.exit_event)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Always shutdown threads first
        self.shutdown_all()

        # Don't suppress any exceptions - let them propagate
        return False

    def add_thread(self, thread_class, name=None, **kwargs):
        """
        Add a thread class instance to be managed

        Args:
            thread_class: The thread class to instantiate
            name: Optional name for the thread
            **kwargs: Additional keyword arguments to pass to the thread constructor
        """
        thread_instance = thread_class(self.exit_event, name, self, **kwargs)
        thread_instance.daemon = True
        thread_instance.start()
        self.threads.append(thread_instance)
        return thread_instance

    def report_exception(self, exception, thread_name):
        """Called by threads to report exceptions to the handler"""
        with self.exception_lock:
            self.exception_queue.append((exception, thread_name))

    def check_and_raise_thread_exceptions(self):
        """Check for exceptions reported by threads and raise them"""
        with self.exception_lock:
            if self.exception_queue:
                exception, thread_name = self.exception_queue.pop(0)

                # Add context about which thread raised the exception
                context_message = f"Thread {thread_name}: {str(exception)}"

                # Re-raise known system exceptions with thread context
                if isinstance(exception, (ShutdownError, RebootError, ExitError)):
                    exception_class = exception.__class__
                    raise exception_class(context_message) from exception

                # For unexpected exceptions, log them with full details
                self.logger.error(
                    f"Unexpected exception from thread {thread_name}: {exception.__class__.__name__}",
                    exc_info=exception
                )

                # Trigger exit event to initiate shutdown
                self.trigger_exit(f"Thread {thread_name} failed with {exception.__class__.__name__}")

                # Re-raise the original exception to preserve the type
                # This allows the caller to handle specific exception types if needed
                raise exception

    def trigger_exit(self, error_message="Manual shutdown"):
        """Trigger graceful shutdown of all threads"""
        if not self.error_occurred:
            self.error_occurred = True
            self.error_message = error_message
        self.exit_event.set()

    def shutdown_all(self):
        """Shutdown and join all threads"""
        if not self.exit_event.is_set():
            self.exit_event.set()

        if self.threads:
            self.logger.info(f"Shutting down {len(self.threads)} threads... Reason: '{self.error_message}'")

            # Wait for all threads to finish gracefully
            for thread in self.threads:
                if thread.is_alive():
                    self.logger.info(f"Waiting for {thread.name} to finish...")
                    thread.join(timeout=3)  # 3 second timeout per thread
                    if thread.is_alive():
                        self.logger.warning(f"Thread {thread.name} did not shutdown gracefully")
                    else:
                        self.logger.info(f"{thread.name} stopped successfully")

    def is_running(self):
        """Check if any threads are still running"""
        return any(thread.is_alive() for thread in self.threads)


class BaseThread(threading.Thread):
    """Base class for all managed threads"""

    def __init__(self, exit_event:threading.Event, name:str|None=None, thread_handler:ThreadHandler|None=None):
        super().__init__(name=name)
        self.exit_event = exit_event
        self.thread_name = name or self.__class__.__name__
        self.thread_handler = thread_handler
        self.logger = LoggerSetup.get_logger()

    def should_exit(self):
        """Check if thread should exit"""
        return self.exit_event.is_set()

    def safe_sleep(self, duration:int|float):
        """Sleep that can be interrupted by exit event

        Returns True if exit is requested, False if sleep completed normally
        """
        return self.exit_event.wait(duration)

    def run(self):
        try:
            self.logger.info(f"{self.thread_name}: Started")
            self.thread_work()
            self.logger.info(f"{self.thread_name}: Finished normally")
        except (RebootError, ShutdownError, ExitError) as e:
            self.logger.info(f"{self.thread_name}: {type(e).__name__} raised - '{e}'")
            # Report the exception to the thread handler
            if self.thread_handler:
                self.thread_handler.report_exception(e, self.thread_name)
            else:
                self.logger.warning(f"No thread handler for '{self.thread_name}'")
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error(f"{self.thread_name}: Unexpected error - {e}", exc_info=True)
            # Report unexpected exceptions
            if self.thread_handler:
                self.thread_handler.report_exception(e, self.thread_name)
            else:
                self.logger.warning(f"No thread handler for '{self.thread_name}'")
        finally:
            self.logger.info(f"{self.thread_name}: Cleaning up...")
            try:
                self.cleanup()
            except Exception as e:  # pylint: disable=broad-except
                self.logger.error(f"{self.thread_name}: Error during cleanup - {e}", exc_info=True)

    def thread_work(self):
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement thread_work()")

    def cleanup(self):
        """Override this method in subclasses to perform cleanup operations"""
        # Default implementation does nothing
        pass  # pylint: disable=unnecessary-pass

class SignalHandler:
    """Handle signals and trigger graceful shutdown"""
    def __init__(self, thread_handler):
        self.thread_handler = thread_handler
        self.logger = LoggerSetup.get_logger()
        self.original_sigint = signal.signal(signal.SIGINT, self.handle_signal)
        if hasattr(signal, 'SIGTERM'):
            self.original_sigterm = signal.signal(signal.SIGTERM, self.handle_signal)

    def handle_signal(self, signum, frame):  #pylint: disable=unused-argument
        """Handle signals and trigger graceful shutdown"""
        signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        self.logger.warning(f"{signal_name} received, initiating graceful shutdown...")
        self.thread_handler.trigger_exit(f"{signal_name} signal received")
        # Raise ExitError to propagate through the system
        raise ExitError(f"{signal_name} signal received")

    def restore(self):
        """Restore original signal handlers"""
        signal.signal(signal.SIGINT, self.original_sigint)
        if hasattr(signal, 'SIGTERM') and hasattr(self, 'original_sigterm'):
            signal.signal(signal.SIGTERM, self.original_sigterm)

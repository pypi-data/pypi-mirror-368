"""
High-level MQTT messaging interface for the Aggienaut system.

Provides simplified publish/subscribe functions that handle JSON serialization
and automatically manage broker connections through LocalMQTTBroker.
"""
import logging
import inspect
from datetime import datetime
from types import FrameType
from pathlib import Path
import json
from typing import Any, Callable, Optional


from common.type_validation import assert_type
from common.aggie_mqtt.mqtt_broker import LocalMQTTBroker


def publish(topic: str, data: Any, retain: bool = False):
    """
    Publish data to an MQTT topic.

    Args:
        topic: The topic to publish to
        data: The data to publish (will be converted to string if needed)
        retain: Whether to retain the message for new subscribers
    """
    broker = LocalMQTTBroker()
    broker.publish(topic, data, retain)

def subscribe(topic: str, callback: Callable[[str, Any], None]) -> int:
    """
    Subscribe to an MQTT topic.

    Args:
        topic: The topic to subscribe to
        callback: Function that takes (topic, payload) as arguments

    Returns:
        int: Callback index for unsubscribing
    """
    def _callback_wrapper(topic, payload):
        # Try to parse JSON, but fall back to raw payload if it fails
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = payload
        callback(topic, data)

    broker = LocalMQTTBroker()
    return broker.subscribe(topic, _callback_wrapper)

def unsubscribe(topic: str, callback_index: Optional[int] = None):
    """
    Unsubscribe from a topic.

    Args:
        topic: The topic to unsubscribe from
        callback_index: Optional index of callback to remove
    """
    broker = LocalMQTTBroker()
    broker.unsubscribe(topic, callback_index)

def get_valid_frame() -> FrameType:
    """
    Get a valid frame from the given frame.
    """
    return assert_type(inspect.currentframe(),FrameType)


def get_caller_module_name():
    """Extract the folder name after 'aggienaut' from caller's file path"""

    frame = assert_type(assert_type(inspect.currentframe(),FrameType).f_back,FrameType).f_back  # Go back 2 frames
    caller_file = assert_type(frame,FrameType).f_code.co_filename
    caller_path = Path(caller_file)

    try:
        parts = caller_path.parts
        aggienaut_index = parts.index('aggienaut')
        if aggienaut_index + 1 < len(parts):
            return parts[aggienaut_index + 1]
    except (ValueError, IndexError):
        pass

    return caller_path.parent.name  # Fallback

def log_and_publish(message:str|dict, topic:str|None = None, log_level:str = 'info', logger:logging.Logger|None = None):
    """
    Wrapper to log a message and publish it to an MQTT topic with timestamp formatting.

    Args:
        message: The message to log and publish (string or dict)
        topic: MQTT topic to publish to (defaults to 'radio_transmit' topic if None)
        log_level: Logging level ('debug', 'info', 'warning', 'error', 'critical') (defaults to 'info' if None)
        logger: Logger instance to use (auto-detects from caller if None)
    """
    from common.command.configs import MQTTConfigTopicMappings

    module_name = get_caller_module_name()

    # Set defaults
    if topic is None:
        topic = MQTTConfigTopicMappings().radio_transmit

    if logger is None:
        frame = inspect.currentframe().f_back  #type:ignore
        caller_locals = frame.f_locals  #type:ignore
        if 'self' in caller_locals and hasattr(caller_locals['self'], 'logger'):
            logger = caller_locals['self'].logger
        else:
            logger = logging.getLogger(module_name)

    if isinstance(logger,logging.Logger):
        # Log the message
        if log_level == 'debug':
            logger.debug(message)
        elif log_level == 'info':
            logger.info(message)
        elif log_level == 'warning':
            logger.warning(message)
        elif log_level == 'error':
            logger.error(message)
        elif log_level == 'critical':
            logger.critical(message)
        else:
            raise ValueError(f'Invalid log level {log_level}')
    else:
        raise ValueError('Invalid logger %s', logger)


    now = datetime.now()
    str_message = str(message)
    formatted_message = f'{now:%b-%d %H:%M:%S}: {str_message}'

    print(f"Publishing to {topic}: {formatted_message}")
    publish(topic=topic, data=formatted_message)

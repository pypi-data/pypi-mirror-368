"""
Command handling module for parsing, validating, and executing MQTT commands.

Provides Command class for structured command processing with category, action,
target, and state components (e.g., "nav set rudder -15").
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging
from common.aggie_mqtt import publish, log_and_publish
from common.errors import CommandError

from .configs import MQTTCommandMappings, MQTTConfigTopicMappings


@dataclass
class CommandBase:
    """Base class for command handling with lazy-loaded configurations and logger."""

    _logger = None

    @classmethod
    def _get_logger(cls):
        """Get logger instance, creating it if it doesn't exist."""
        if cls._logger is None:
            cls._logger = logging.getLogger("commands")
        return cls._logger

@dataclass
class Command(CommandBase):
    """
    Class representing a command using a command_byte and state.
    """
    command_byte: int
    state: list[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_byte": self.command_byte,
            "state": self.state,
        }

    def encode(self) -> bytes:
        """
        Encode the Command object into bytes for MQTT transmission.
        Format: [command_byte][state as utf-8 string]
        """
        try:
            state_str = " ".join(self.state)
            return bytes([self.command_byte]) + state_str.encode("utf-8")
        except Exception as e:
            self._get_logger().error(f"Failed to encode command: {e}")
            raise

    @classmethod
    def parse(cls, data) -> 'Command':
        """
        Parse bytes or str into a Command object.
        First byte is command_byte, rest is utf-8 encoded state string split by spaces.
        Accepts either bytes or str; str will be encoded as utf-8.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        if not data or len(data) < 1:
            raise CommandError("Command data must be at least 1 byte")
        command_byte = data[0]
        state = data[1:].decode("utf-8").split() if len(data) > 1 else []
        return cls(command_byte=command_byte, state=state)

    @classmethod
    def handle(cls, data: bytes|str) -> 'Command':
        """
        Parses a command from bytes and publishes it to MQTT.
        Args:
            data (bytes): command to parse and handle
        Returns:
            Command: The processed Command object
        Raises:
            CommandError: If the command is invalid
            RuntimeError: If MQTT publishing fails
        """
        try:
            cmd_obj = cls.parse(data)
            cls._get_logger().info(f"Processing command: {cmd_obj}")
            cls._publish_command(cmd_obj)
            cls._get_logger().debug("Command published successfully")
            return cmd_obj
        except CommandError as e:
            log_and_publish(
                message=f"Invalid command bytes: {e}",
                log_level='warning',
                logger=cls._get_logger()
            )
            raise
        except Exception as e:
            cls._get_logger().error(f"Failed to handle command bytes: {e}")
            raise RuntimeError(f"Command handling failed: {e}") from e

    @classmethod
    def _publish_command(cls, cmd_obj: 'Command') -> None:
        """
        Publish a Command state to MQTT.
        Args:
            cmd_obj: Command object
        Raises:
            RuntimeError: If encoding or publishing fails
        """
        try:
            state = cmd_obj.state
            topic = cls._get_mqtt_topic(cmd_obj.command_byte)
            if topic is None:
                log_and_publish(
                    message=f'Could not get publish topic for command byte {cmd_obj.command_byte}',
                    log_level='error',
                    logger=cls._get_logger()
                )
                raise KeyError(f'Could not get publish topic for command byte {cmd_obj.command_byte}')
            publish(topic=topic, data=state)
        except Exception as e:
            raise RuntimeError(f"Failed to publish command to MQTT: {e}") from e

    @classmethod
    def _get_mqtt_topic(cls, command_byte: int) -> Optional[str]:
        """
        Get the appropriate MQTT topic from mqtt_topics.toml based on command_byte.
        Args:
            command_byte: The command byte (int)
        Returns:
            MQTT topic string or None if not found
        """
        try:
            # Load byte-to-topic mapping from config
            byte_mapping = MQTTCommandMappings().command_byte_topic_mapping
            hex_key = f"0x{command_byte:02X}"  # Format as 0x0C instead of 0xc
            topic_name = byte_mapping.get(hex_key, None)
            if topic_name is None:
                log_and_publish(
                    message=f"Command byte mapping not found for: {hex_key}",
                    log_level='error',
                    logger=cls._get_logger()
                )
                return None
            topic_mappings = MQTTConfigTopicMappings()
            if topic_name not in topic_mappings:
                log_and_publish(
                    message=f"Topic key '{topic_name}' not found in MQTTConfigTopicMappings config",
                    log_level='error',
                    logger=cls._get_logger()
                )
                return None
            return topic_mappings[topic_name]
        except Exception as e:
            log_and_publish(
                message=f"Error getting topic for command byte 0x{command_byte:02X}: {e}",
                log_level='error',
                logger=cls._get_logger()
            )
            return None

    def __str__(self) -> str:
        state = " ".join(self.state)
        return f"Command(command_byte=0x{self.command_byte:02X}, state='{state}')"

    def __repr__(self) -> str:
        return self.__str__()

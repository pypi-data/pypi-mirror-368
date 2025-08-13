"""Local MQTT broker singleton for inter-thread communication."""
""" Module to wrap log and publish together. """

import json
import threading
from typing import Dict, Any, Optional
import logging

import paho.mqtt.client as mqtt


class LocalMQTTBroker:
    """
    A singleton class that manages a local MQTT client for inter-thread communication.
    """
    _instance = None
    _lock = threading.Lock()
    _initialized: bool

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LocalMQTTBroker, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        """Initialize MQTT client and connect to localhost broker."""

        import platform
        self.logger = logging.getLogger("mqtt")
        if self._initialized:
            return

        self._initialized = True
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # Store callbacks registered by topics
        self.topic_callbacks: Dict[str, list] = {}

        # Only connect to MQTT broker if not on Windows
        if platform.system() != "Windows":
            try:
                self.client.connect("localhost", 1883, 60)
                # Start the loop in a separate thread
                self.client.loop_start()
                self.logger.info("Connected to local MQTT broker")
            except Exception as e:  #pylint:disable=broad-except
                self.logger.error("Failed to connect to MQTT broker: %s", e)
        else:
            self.logger.info("Skipping MQTT broker connection on Windows.")

    def _on_connect(self, client, userdata, flags, rc):  #pylint:disable=unused-argument
        # Create a copy of the keys to avoid RuntimeError
        """Handle MQTT connection event by subscribing to registered topics."""
        topics = list(self.topic_callbacks.keys())
        for topic in topics:
            self.client.subscribe(topic)

    def _on_disconnect(self, client, userdata, rc):  #pylint:disable=unused-argument
        """Handle MQTT disconnection event."""
        if rc != 0:
            self.logger.warning("Unexpected disconnection from MQTT broker: %s", rc)

    def _on_message(self, client, userdata, msg):  #pylint:disable=unused-argument
        """Handle incoming MQTT messages by calling registered callbacks."""
        topic = msg.topic
        payload = msg.payload.decode()

        # Call all callbacks registered for this topic
        if topic in self.topic_callbacks:
            for callback in self.topic_callbacks[topic]:
                try:
                    callback(topic, payload)
                except Exception as e:
                    self.logger.error("Error in MQTT callback for topic %s: %s", topic, e)
                    raise

    def subscribe(self, topic: str, callback):
        """
        Subscribe to a topic with a callback function.

        Args:
            topic: The MQTT topic to subscribe to
            callback: Function that takes (topic, payload) as arguments
        """
        self.logger.debug("Subscribing to topic: %s", topic)
        if topic not in self.topic_callbacks:
            self.topic_callbacks[topic] = []
            self.client.subscribe(topic)

        self.topic_callbacks[topic].append(callback)
        return len(self.topic_callbacks[topic]) - 1  # Return callback index for unsubscribe

    def unsubscribe(self, topic: str, callback_index: Optional[int] = None):
        """
        Unsubscribe from a topic or remove a specific callback.

        Args:
            topic: The MQTT topic
            callback_index: Optional index of callback to remove (if None, removes all)
        """
        self.logger.debug("Unsubscribing from topic: %s", topic)
        if topic in self.topic_callbacks:
            if callback_index is not None:
                if 0 <= callback_index < len(self.topic_callbacks[topic]):
                    self.topic_callbacks[topic].pop(callback_index)
                    if not self.topic_callbacks[topic]:
                        del self.topic_callbacks[topic]
                        self.client.unsubscribe(topic)
            else:
                del self.topic_callbacks[topic]
                self.client.unsubscribe(topic)

    def publish(self, topic: str, payload: Any, retain: bool = False):
        """
        Publish a message to a topic.

        Args:
            topic: The MQTT topic to publish to
            payload: The message payload (will be converted to string)
            retain: Whether to retain the message for new subscribers
        """
        self.logger.debug("Publishing to topic: %s", topic)
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload)
        elif not isinstance(payload, str):
            payload = str(payload)

        self.client.publish(topic, payload, retain=retain)

    def close(self):
        """Stop the MQTT client loop and disconnect"""
        self.client.loop_stop()
        self.client.disconnect()

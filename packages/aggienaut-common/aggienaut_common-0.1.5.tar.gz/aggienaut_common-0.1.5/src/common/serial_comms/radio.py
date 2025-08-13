"""Module containing the Radio class."""
from pathlib import Path
import time
import threading
from typing import Optional
from logging import getLogger

import serial
import serial.tools.list_ports

from .configs import RadioConfig


class RadioSingleton:
    """Singleton class to manage a single radio connection"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._radio = None
            self._current_port = None
            self._initialized = True

    def get_radio(self, port: str) -> 'Radio':
        """Get or create radio instance for the specified port"""
        with self._lock:
            if (self._radio is None or
                self._current_port != port):
                # Close existing connection if port changed
                if self._radio is not None:
                    self._radio.close()

                self._radio = Radio(port)
                self._current_port = port

            return self._radio

    def close(self):
        """Close the current radio connection"""
        with self._lock:
            if self._radio is not None:
                self._radio.close()
                self._radio = None
                self._current_port = None

class Radio:
    """Class representing a radio connection."""
    # Define start and end bytes for packet framing
    START_BYTE = 0x02  # STX (Start of Text)
    END_BYTE = 0x03    # ETX (End of Text)

    def __init__(self, port):
        self.logger = getLogger("radio")
        self.config = RadioConfig()
        if not port:
            self.port = self.config.port
        else:
            self.port = port
        self.baud_rate = self.config.baud_rate
        self.ser = None
        self._lock = threading.Lock()
        self._buffer = bytearray()  # Buffer to store incomplete packets
        self._setup_serial()

    def _setup_serial(self):
        """Setup and return a serial connection"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.config.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                # Add these for better compatibility
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            # Add this check:
            if not self.ser.is_open:
                self.ser.open()

            # Clear any existing data in buffers
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._buffer.clear()  # Clear the packet buffer

            self.logger.info("Opened radio connection on %s at %s baud", self.port, self.baud_rate)
        except serial.SerialException as e:
            self.logger.error("Error opening %s: %s", self.port, e)
            raise ValueError("Error opening %s: %s", self.port, e) from e  #pylint: disable=raising-format-tuple

    def _parse_data(self, data: bytes) -> Optional[str]:
        """Logic to parse data and check if it is good"""
        try:
            # Log raw hex data for debugging
            hex_data = ' '.join(f'{b:02x}' for b in data)
            # self.logger.debug(f"Raw data (hex): {hex_data}")

            # Check if data looks like binary (non-printable characters)
            if self._is_binary_data(data):
                # self.logger.warning(f"Received binary data: {hex_data}")
                return f"BINARY_DATA:{hex_data}"

            # Try to decode as text
            decoded = data.decode('utf-8', errors='replace').strip()
            return decoded if decoded else None

        except Exception as e:  # pylint: disable=broad-except
            self.logger.error("Error parsing data: %s", e)
            return None

    def _is_binary_data(self, data: bytes) -> bool:
        """Check if data appears to be binary rather than text"""
        if not data:
            return False

        # Count non-printable characters (excluding common whitespace)
        non_printable = 0
        for byte in data:
            # Consider bytes outside printable ASCII range (32-126) plus common whitespace
            if byte < 32 and byte not in [9, 10, 13]:  # Tab, LF, CR are OK
                non_printable += 1
            elif byte > 126:
                non_printable += 1

        # If more than 50% of bytes are non-printable, consider it binary
        return (non_printable / len(data)) > 0.5

    def _extract_packets(self, new_data: bytes) -> list[bytes]:
        """Extract complete packets from buffer and new data"""
        # Add new data to buffer
        self._buffer.extend(new_data)

        packets = []

        # Process buffer to extract complete packets
        while True:
            # Find start byte
            start_idx = self._buffer.find(bytes([self.START_BYTE]))
            if start_idx == -1:
                # No start byte found, clear buffer and return
                self._buffer.clear()
                break

            # If there's data before the start byte, discard it
            if start_idx > 0:
                self._buffer = self._buffer[start_idx:]
                start_idx = 0

            # Find end byte after start byte
            end_idx = self._buffer.find(bytes([self.END_BYTE]), start_idx + 1)
            if end_idx == -1:
                # No end byte found, keep buffer for next time
                break

            # Extract packet (excluding start/end bytes)
            packet = self._buffer[start_idx + 1:end_idx]
            packets.append(packet)

            # Remove processed packet from buffer
            self._buffer = self._buffer[end_idx + 1:]

            # If buffer is empty, break
            if not self._buffer:
                break

        return packets

    def _receive_data(self, timeout: int|float) -> Optional[str]:
        """Continuously receive and display data"""
        timeout_counter = 0

        with self._lock:
            if not self.ser or not self.ser.is_open:
                self.logger.error("Serial port is not open")
                return None

            while timeout_counter < timeout:
                try:
                    if self.ser.in_waiting > 0:
                        data = self.ser.read(self.ser.in_waiting)
                        packets = self._extract_packets(data)

                        if packets:
                            # Return the first complete packet
                            parsed = self._parse_data(packets[0])
                            if parsed:
                                return parsed

                except Exception as e:  # pylint: disable=broad-except
                    self.logger.error("Error receiving data: %s", e)
                    break

                time.sleep(0.1)
                timeout_counter += 1

        return None  # Return None if timeout reached

    def _send_data(self, message: str|bytes) -> None:
        """Send data to the radio"""
        with self._lock:
            if not self.ser or not self.ser.is_open:
                raise serial.SerialException("Serial port is not open")

            try:
                # Encode the message
                if isinstance(message, str):
                    encoded_message = message.encode('utf-8')
                elif isinstance(message, bytes):
                    encoded_message = message
                else:
                    raise ValueError("Message must be a string or bytes")

                # Create framed message with start and end bytes
                framed_message = bytes([self.START_BYTE]) + encoded_message + bytes([self.END_BYTE])

                self.ser.write(framed_message)
                self.ser.flush()  # Ensure data is sent immediately

                hex_message = ' '.join(f'{b:02x}' for b in framed_message)
                self.logger.debug("Sent framed message: %s", hex_message)
            except Exception as e:
                self.logger.error("Error sending data: %s", e)
                raise

    def listen(self, timeout:int|float) -> Optional[str]:
        """Continuously receive and display data"""
        return self._receive_data(timeout=timeout)

    def send(self, message: str|bytes) -> None:
        """Send data to the radio"""
        self._send_data(message)

    def close(self):
        """Close the serial connection"""
        with self._lock:
            try:
                if self.ser and self.ser.is_open:
                    self.ser.close()
                    self.logger.info("Closed radio connection on %s", self.port)
            except Exception as e:  # pylint: disable=broad-except
                self.logger.error("Error closing serial port: %s", e)


def send_to_radio(port: str, message: str|bytes) -> None:
    """Send message to radio using singleton instance"""
    radio_singleton = RadioSingleton()
    radio = radio_singleton.get_radio(port)
    radio.send(message=message)

def listen_to_radio(port: str, timeout: int|float) -> Optional[str]:
    """Listen for data from radio using singleton instance"""
    radio_singleton = RadioSingleton()
    radio = radio_singleton.get_radio(port)
    return radio.listen(timeout)

def close_radio_connection():
    """Close the radio connection"""
    radio_singleton = RadioSingleton()
    radio_singleton.close()

def list_available_ports() -> list[str]:
    """List all available serial ports"""
    return [p.device for p in serial.tools.list_ports.comports()]

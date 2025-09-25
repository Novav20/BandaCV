import unittest
from unittest.mock import patch, MagicMock
import serial
import serial.tools.list_ports
import time
from src.hardware.serial_manager import SerialManager
from src.config.config import AppConfig
from src.vision.classifiers import ServoCode

class TestSerialManager(unittest.TestCase):

    @patch('serial.tools.list_ports.comports')
    def test_get_arduino_port_found(self, mock_comports):
        mock_port = MagicMock()
        mock_port.device = "/dev/ttyACM0"
        mock_port.description = "Arduino Uno (COM3)"
        mock_comports.return_value = [mock_port]

        manager = SerialManager()
        port = manager._get_arduino_port()
        self.assertEqual(port, "/dev/ttyACM0")

    @patch('serial.tools.list_ports.comports')
    def test_get_arduino_port_not_found(self, mock_comports):
        mock_comports.return_value = []

        manager = SerialManager()
        port = manager._get_arduino_port()
        self.assertIsNone(port)

    @patch('serial.Serial')
    @patch('serial.tools.list_ports.comports')
    def test_connect_success(self, mock_comports, mock_serial):
        mock_port = MagicMock()
        mock_port.device = "/dev/ttyACM0"
        mock_port.description = "Arduino Uno (COM3)"
        mock_comports.return_value = [mock_port]

        mock_serial_instance = MagicMock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True

        manager = SerialManager()
        with patch('time.sleep', return_value=None): # Mock time.sleep
            connected = manager.connect()

        self.assertTrue(connected)
        self.assertTrue(manager.connected)
        mock_serial.assert_called_once_with("/dev/ttyACM0", AppConfig.BAUDRATE, timeout=1)

    @patch('serial.Serial')
    @patch('serial.tools.list_ports.comports')
    def test_connect_failure(self, mock_comports, mock_serial):
        mock_comports.return_value = [] # No port found initially

        # Simulate port becoming available after some retries
        mock_port = MagicMock()
        mock_port.device = "/dev/ttyACM0"
        mock_port.description = "Arduino Uno (COM3)"
        mock_comports.side_effect = [[], [], [mock_port]] # Return empty list twice, then port

        mock_serial_instance = MagicMock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True

        manager = SerialManager()
        with patch('time.sleep', return_value=None): # Mock time.sleep
            connected = manager.connect()

        self.assertTrue(connected)
        self.assertTrue(manager.connected)
        self.assertEqual(mock_comports.call_count, 3) # Called 3 times due to retries

    @patch('serial.Serial')
    def test_disconnect(self, mock_serial):
        manager = SerialManager()
        manager.ser = MagicMock()
        manager.ser.is_open = True
        manager.connected = True

        manager.disconnect()

        manager.ser.close.assert_called_once()
        self.assertFalse(manager.connected)

    @patch('serial.Serial')
    def test_read_data_success(self, mock_serial):
        manager = SerialManager()
        manager.ser = MagicMock()
        manager.ser.is_open = True
        manager.connected = True
        manager.ser.readline.return_value = b"123_1\n"

        rpm, obstacle_state = manager.read_data()
        self.assertEqual(rpm, 123)
        self.assertEqual(obstacle_state, 1)

    @patch('serial.Serial')
    def test_read_data_invalid_format(self, mock_serial):
        manager = SerialManager()
        manager.ser = MagicMock()
        manager.ser.is_open = True
        manager.connected = True
        manager.ser.readline.return_value = b"invalid_data\n"

        result = manager.read_data()
        self.assertIsNone(result)

    @patch('serial.Serial')
    def test_send_command(self, mock_serial):
        manager = SerialManager()
        manager.ser = MagicMock()
        manager.ser.is_open = True
        manager.connected = True

        pwm_value = 150
        servo_code = ServoCode.RED
        manager.send_command(pwm_value, servo_code)

        manager.ser.write.assert_called_once_with(b"150_0\n")

    @patch('serial.Serial')
    def test_send_command_not_connected(self, mock_serial):
        manager = SerialManager()
        manager.connected = False

        pwm_value = 150
        servo_code = ServoCode.RED
        manager.send_command(pwm_value, servo_code)

        mock_serial.assert_not_called()

if __name__ == '__main__':
    unittest.main()

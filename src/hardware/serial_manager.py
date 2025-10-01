import serial
import serial.tools.list_ports
import time
from src.config.config import AppConfig
from src.vision.classifiers import ServoCode

class SerialManager:
    """Manages the serial communication with the Arduino.

    This class handles finding the correct serial port, connecting to the device,
    reading data, and sending commands.

    Args:
        baudrate (int): The baud rate for the serial communication.
    """
    def __init__(self, baudrate=AppConfig.BAUDRATE):
        self.baudrate = baudrate
        self.ser = None
        self.connected = False

    def _find_serial_device_port(self) -> str | None:
        """Finds a suitable serial port based on configured identifiers.

        Returns:
            str | None: The device port string if found, otherwise None.
        """
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            for identifier in AppConfig.SERIAL_DEVICE_IDENTIFIERS:
                if identifier in port.description or identifier in port.hwid or identifier in port.device:
                    return str(port.device)
        return None

    def connect(self) -> bool:
        """Connects to the serial device.

        This method searches for the serial device and establishes a connection.
        It will keep retrying until a device is found.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        if self.connected and self.ser.is_open:
            print("Already connected to serial device.")
            return True

        port = None
        while port is None:
            print("Searching for serial device...")
            port = self._find_serial_device_port()
            if port is None:
                print("Device not found. Retrying in 1 second...")
                time.sleep(1)

        try:
            self.ser = serial.Serial(port, self.baudrate, timeout=1) # Set a timeout
            time.sleep(2) # Allow device to reset
            self.connected = True
            print(f"Successfully connected to serial device on port {port}")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to serial device: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnects from the serial port."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connected = False
            print("Disconnected from serial device.")

    def read_data(self) -> tuple[int, int] | None:
        """Reads and parses data from the serial port.

        The expected format is "RPM_OBSTACLE_STATE".

        Returns:
            tuple[int, int] | None: A tuple containing the RPM value and the
                                     obstacle sensor state, or None if an error
                                     occurs.
        """
        if not self.connected or not self.ser.is_open:
            return None
        try:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if not line: # Handle empty line if timeout occurs
                return None
            data_list = line.split('_')
            if len(data_list) == 2:
                rpm_value = int(data_list[0])
                obstacle_sensor_state_value = int(data_list[1])
                return rpm_value, obstacle_sensor_state_value
        except (serial.SerialException, ValueError) as e:
            print(f"Error reading serial data: {e}")
        return None

    def send_command(self, pwm_value: int, servo_code: ServoCode):
        """Sends a command to the Arduino.

        The command format is "PWM_SERVOCODE".

        Args:
            pwm_value (int): The PWM value for the motor.
            servo_code (ServoCode): The code for the servo position.
        """
        if not self.connected or not self.ser.is_open:
            # Silently return if not connected, to avoid flooding the console
            return
        try:
            command = f"{pwm_value}_{servo_code.value}\n".encode()
            self.ser.write(command)
        except serial.SerialException as e:
            print(f"Error sending serial command: {e}")

import serial
import serial.tools.list_ports
import time
from src.config.config import AppConfig
from src.vision.classifiers import ServoCode

class SerialManager:
    def __init__(self, baudrate=AppConfig.BAUDRATE):
        self.baudrate = baudrate
        self.ser = None
        self.connected = False

    def _find_serial_device_port(self):
        """Finds a suitable serial port based on configured identifiers."""
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            for identifier in AppConfig.SERIAL_DEVICE_IDENTIFIERS:
                if identifier in port.description or identifier in port.hwid or identifier in port.device:
                    return str(port.device)
        return None

    def connect(self):
        """Connects to the serial device port."""
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
        """Reads data from the serial port (RPM_OBSTACLE_STATE)."""
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
        """Sends a command to the serial device (PWM_SERVOCODE)."""
        if not self.connected or not self.ser.is_open:
            print("Not connected to serial device. Command not sent.")
            return
        try:
            command = f"{pwm_value}_{servo_code.value}\n".encode()
            self.ser.write(command)
            # print(f"Sent: {command.decode().strip()}") # For debugging
        except serial.SerialException as e:
            print(f"Error sending serial command: {e}")

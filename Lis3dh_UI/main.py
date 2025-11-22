
from machine import I2C, UART  # Import I2C and UART modules from machine library
import utime as time  # Import time module with alias

# UART Initialization - Set up UART2 with 115200 baud, 8 data bits, no parity, 1 stop bit
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)

def uart_print(msg):  # Define function to send messages via UART
    try:  # Try block for error handling
        uart.write((msg + "\r\n").encode())  # Encode message and send via UART with newline
    except Exception as e:  # Catch any exceptions
        print("UART write error:", e)  # Print error to console if UART fails

# File for saving interval - Define configuration file path
CONFIG_FILE = "/usr/config.txt"

def save_interval(value):  # Function to save interval to file
    try:  # Try block for error handling
        with open(CONFIG_FILE, "w") as f:  # Open file in write mode
            f.write(str(value))  # Write interval value as string
    except Exception as e:  # Catch any exceptions
        uart_print("Error saving interval: {}".format(e))  # Send error via UART

def load_interval(default=2):  # Function to load interval from file
    try:  # Try block for error handling
        with open(CONFIG_FILE, "r") as f:  # Open file in read mode
            val = f.read().strip()  # Read and strip whitespace from file
            if val:  # Check if value exists
                return int(val)  # Return value as integer
            else:  # If file is empty
                return default  # Return default value
    except Exception:  # Catch any exceptions (file not found, etc.)
        return default  # Return default value on error

# LIS3DH Accelerometer Driver Class
class LIS3DH:
    WHO_AM_I_REG = 0x0F  # Device identification register address
    WHO_AM_I_VAL = 0x33  # Expected device identification value
    ADDR_LIST = [0x18, 0x19]  # List of possible I2C addresses

    def __init__(self, i2c):  # Constructor method
        self.i2c = i2c  # Store I2C object reference
        self.addr = None  # Initialize device address as None
        self.detect()  # Call detect method to find device
        self.init_sensor()  # Initialize sensor settings

    def write_reg(self, reg, value):  # Method to write to sensor register
        buf = bytearray([reg, value])  # Create byte array with register and value
        self.i2c.write(self.addr, b'', 0, buf, 2)  # Write to I2C device

    def read_reg(self, reg):  # Method to read from sensor register
        reg_buf = bytearray([reg])  # Create byte array with register address
        self.i2c.write(self.addr, b'', 0, reg_buf, 1)  # Send register address to read from
        val_buf = bytearray(1)  # Create buffer for response
        self.i2c.read(self.addr, b'', 0, val_buf, 1, 0)  # Read 1 byte from register
        return val_buf[0]  # Return the read value

    def detect(self):  # Method to detect sensor on I2C bus
        for addr in self.ADDR_LIST:  # Iterate through possible addresses
            self.addr = addr  # Set current address
            try:  # Try to communicate with device
                val = self.read_reg(self.WHO_AM_I_REG)  # Read WHO_AM_I register
                if val == self.WHO_AM_I_VAL:  # Check if value matches expected
                    # uart_print("LIS3DH detected at 0x{:02X}".format(addr))  # Print detection message
                    return  # Exit method if found
            except Exception:  # Catch communication errors
                continue  # Try next address
        raise Exception("LIS3DH not found on I2C bus")  # Raise error if not found

    def init_sensor(self):  # Method to initialize sensor settings
        self.write_reg(0x20, 0x57)  # CTRL_REG1: Enable sensor, 50Hz data rate
        self.write_reg(0x23, 0x08)  # CTRL_REG4: High resolution mode
        uart_print("LIS3DH initialized.")  # Print initialization message

    def read_axes(self):  # Method to read acceleration data from all three axes
        def twos_complement(val, bits):  # Nested function for two's complement conversion
            if val & (1 << (bits - 1)):  # Check if value is negative (MSB set)
                val -= 1 << bits  # Convert from two's complement
            return val  # Return signed value

        data = []  # Initialize list for axis data
        scale = 0.001  # Scale factor for conversion (g per LSB)
        try:  # Try block for error handling
            for reg in [0x28, 0x2A, 0x2C]:  # Loop through X, Y, Z axis data registers
                l = self.read_reg(reg)  # Read low byte of axis data
                h = self.read_reg(reg + 1)  # Read high byte of axis data
                raw = (l | (h << 8))  # Combine low and high bytes
                raw = twos_complement(raw, 16)  # Convert to signed value
                raw = raw >> 4  # Right shift for 12-bit resolution
                data.append(raw * scale * 9.80665)  # Convert to m/s² and add to list
        except Exception as e:  # Catch any exceptions
            uart_print("Error reading axes: {}".format(e))  # Send error message
            data = [0, 0, 9.80665]  # Fallback data (gravity on Z-axis)
        return tuple(data)  # Return data as tuple

# Initialize I2C - Set up I2C0 interface in fast mode (400kHz)
i2c = I2C(I2C.I2C0, I2C.FAST_MODE)

# Global Variables
interval = load_interval(default=1)  # Load interval from file or use default
uart_buffer = ""  # Initialize buffer for UART commands
sensor = None  # Initialize sensor object as None

def initialize_system():  # Function to initialize/reinitialize the system
    global sensor, uart_buffer, interval  # Access global variables
    uart_buffer = ""  # Clear UART buffer
    interval = load_interval()  # Reload interval from file
    try:  # Try to initialize sensor
        sensor = LIS3DH(i2c)  # Create LIS3DH sensor object
    except Exception as e:  # Catch initialization errors
        uart_print("Sensor init error: {}".format(e))  # Send error message
        sensor = None  # Set sensor to None on error
    uart_print("System Restarted. Interval: {} sec".format(interval))  # Print status
    # uart_print("Use 'Interval Configuration : <seconds>' to change interval.")  # Print usage

initialize_system()  # Call initialization function at startup

# Main Program Loop
while True:  # Infinite loop
    try:  # Main try block for error handling
        # UART Command Handling
        if uart.any():  # Check if data available on UART
            incoming = uart.read().decode('utf-8')  # Read and decode incoming data
            uart_buffer += incoming  # Append to buffer
            if '\n' in uart_buffer:  # Check if buffer contains complete line
                lines = uart_buffer.split('\n')  # Split buffer into lines
                for line in lines[:-1]:  # Process all complete lines
                    line = line.strip()  # Remove whitespace
                    if line == "Restart Device":  # Check for restart command
                        interval = 1
                        save_interval(interval)  # Save to file
                        initialize_system()  # Reinitialize system
                    elif line.startswith("Interval Configuration :"):  # Check for interval config
                        try:  # Try to parse interval
                            parts = line.split(":")  # Split command at colon
                            if len(parts) > 1:  # Check if value exists
                                new_interval = int(parts[1].strip())  # Extract and convert interval
                                if new_interval > 0:  # Validate interval
                                    interval = new_interval  # Update interval
                                    save_interval(interval)  # Save to file
                                    uart_print("Interval updated: {} sec".format(interval))  # Confirm
                                else:  # Invalid interval
                                    uart_print("Invalid interval (>0)")  # Error message
                            else:  # Malformed command
                                uart_print("Command format invalid")  # Error message
                        except ValueError:  # Catch conversion error
                            uart_print("Invalid number")  # Error message
                uart_buffer = lines[-1]  # Keep incomplete line in buffer

        # Sensor Reading
        if sensor:  # Check if sensor is initialized
            x, y, z = sensor.read_axes()  # Read acceleration data
        else:  # If sensor not available
            x = y = 0  # Set X and Y to zero
            z = 9.80665  # Set Z to gravity value

        uart_print("LIS3DH: X={:.3f}, Y={:.3f}, Z={:.3f}".format(x, y, z))  # Print sensor data

    except Exception as e:  # Catch any exceptions in main loop
        uart_print("Error: {}".format(e))  # Send error message

    time.sleep(interval)  # Wait for specified interval before next reading

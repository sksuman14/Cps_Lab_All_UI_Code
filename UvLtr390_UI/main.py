from machine import I2C, UART  # Import I2C and UART modules for hardware communication
import utime as time  # Import time module with alias for timing functions

# UART Initialization - Set up serial communication interface
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)  # Initialize UART2 with 115200 baud rate, 8 data bits, no parity, 1 stop bit

def uart_print(msg):  # Function to send messages over UART
    try:  # Try block for error handling
        uart.write((msg + "\r\n").encode())  # Convert message to bytes, add carriage return and newline, then send via UART
    except Exception as e:  # Catch any exceptions during UART write
        print("UART write error:", e)  # Print error to console as backup

# File for saving interval - Configuration file management
CONFIG_FILE = "/usr/config.txt"  # Path to configuration file for storing measurement interval

def save_interval(value):  # Function to save interval value to file
    try:  # Try block for file operations
        with open(CONFIG_FILE, "w") as f:  # Open file in write mode using context manager
            f.write(str(value))  # Convert integer to string and save as plain text
    except Exception as e:  # Catch any file operation exceptions
        uart_print("Error saving interval: {}".format(e))  # Send error message via UART

def load_interval(default=1):  # Function to load interval value from file
    try:  # Try block for file operations
        val = open(CONFIG_FILE, "r").read().strip()  # Open file, read content, and remove whitespace
        return int(val) if val else default  # Convert to integer if not empty, else return default value
    except Exception:  # Catch all exceptions (file not found, invalid data, etc.)
        return default  # Return default value if loading fails

# LTR390 Driver - Register addresses and constants for LTR390 UV light sensor
LTR390_I2C_ADDR = 0x53  # I2C address of LTR390 sensor
MAIN_CTRL = 0x00  # Main control register address
MEAS_RATE = 0x04  # Measurement rate control register address
GAIN = 0x05  # Gain control register address
UVS_DATA_0 = 0x10  # UV sensor data byte 0 (LSB) register address
UVS_DATA_1 = 0x11  # UV sensor data byte 1 register address
UVS_DATA_2 = 0x12  # UV sensor data byte 2 (MSB) register address
MAIN_STATUS = 0x07  # Main status register address

UVS_MODE = 0x0A  # UVS active mode value for MAIN_CTRL register
RESOLUTION_18BIT_TIME100MS = 0x20  # 18-bit resolution with 100ms measurement time value for MEAS_RATE register
GAIN_3X = 0x01  # 3x gain value for GAIN register

def write_reg(i2c, reg, val):  # Function to write a value to a specific register
    reg_addr = bytearray([reg])  # Create bytearray with register address
    data = bytearray([val])  # Create bytearray with data value
    i2c.write(LTR390_I2C_ADDR, b'', 0, reg_addr + data, 2)  # Write register address and data using I2C

def read_reg(i2c, reg):  # Function to read a value from a specific register
    reg_addr = bytearray([reg])  # Create bytearray with register address
    buf = bytearray(1)  # Create buffer to store read data
    i2c.write(LTR390_I2C_ADDR, b'', 0, reg_addr, 1)  # Write register address to set read pointer
    time.sleep_ms(1)  # Short delay for sensor to prepare data
    i2c.read(LTR390_I2C_ADDR, b'', 0, buf, 1, 0)  # Read 1 byte from register into buffer
    return buf[0]  # Return the read value

def burst_read(i2c, start_reg, length):  # Function to read multiple bytes starting from a register
    reg_addr = bytearray([start_reg])  # Create bytearray with starting register address
    buf = bytearray(length)  # Create buffer to store read data
    i2c.write(LTR390_I2C_ADDR, b'', 0, reg_addr, 1)  # Write register address to set read pointer
    time.sleep_ms(1)  # Short delay for sensor to prepare data
    i2c.read(LTR390_I2C_ADDR, b'', 0, buf, length, 0)  # Read specified number of bytes into buffer
    return buf  # Return the read data

class LTR390:  # Main sensor driver class for LTR390 UV light sensor
    def __init__(self, i2c):  # Constructor method to initialize sensor
        self.i2c = i2c  # Store I2C object reference
        self.init_sensor()  # Initialize sensor configuration
        self.wait_for_ready()  # Wait for sensor to be ready for measurements

    def init_sensor(self):  # Method to configure sensor settings
        write_reg(self.i2c, MAIN_CTRL, UVS_MODE)  # Set sensor to UV measurement mode
        write_reg(self.i2c, MEAS_RATE, RESOLUTION_18BIT_TIME100MS)  # Set 18-bit resolution with 100ms measurement time
        write_reg(self.i2c, GAIN, GAIN_3X)  # Set gain to 3x
        time.sleep_ms(100)  # Wait 100ms for configuration to take effect
        uart_print("LTR390 initialized.")  # Print initialization message

    def wait_for_ready(self):  # Method to wait for sensor data to be ready
        timeout = 20  # max 2 sec (20 * 100ms = 2000ms)
        while timeout > 0:  # Loop until timeout or data ready
            status = read_reg(self.i2c, MAIN_STATUS)  # Read main status register
            if status & 0x08:  # Check if UV data ready bit is set (bit 3)
                return  # Exit if data is ready
            time.sleep_ms(100)  # Wait 100ms before checking again
            timeout -= 1  # Decrement timeout counter
        uart_print("Warning: UV data not ready after init")  # Print warning if timeout reached

    def read_uv_index(self):  # Method to read UV index measurement from sensor
        status = read_reg(self.i2c, MAIN_STATUS)  # Read main status register
        if not (status & 0x08):  # Check if UV data ready bit is NOT set (bit 3)
            return None  # Return None if data is not ready
        uv_bytes = burst_read(self.i2c, UVS_DATA_0, 3)  # Read 3 bytes of UV data starting from UVS_DATA_0
        uv_index = (uv_bytes[2] << 16) | (uv_bytes[1] << 8) | uv_bytes[0]  # Combine 3 bytes into 24-bit value
        return uv_index  # Return the UV index value

# Initialize I2C - Set up I2C communication bus
i2c = I2C(I2C.I2C0, I2C.FAST_MODE)  # Initialize I2C0 interface in fast mode (400kHz)

# Global Variables - Shared variables across the program
interval = load_interval()  # Current measurement interval loaded from file or default
uart_buffer = ""  # Buffer to store incoming UART data
sensor = None  # Sensor object placeholder, will be initialized later

def initialize_system():  # Function to initialize or reinitialize the system
    global sensor, uart_buffer, interval  # Access global variables
    uart_buffer = ""  # Clear UART command buffer
    interval = load_interval()  # Load interval from configuration file
    try:  # Try to initialize sensor
        sensor = LTR390(i2c)  # Create LTR390 sensor object
    except Exception as e:  # Catch sensor initialization errors
        uart_print("Sensor init error: {}".format(e))  # Send error message via UART
        sensor = None  # Set sensor to None on error
    uart_print("System Restarted. Current interval: {} seconds.".format(interval))  # Send startup message
    # uart_print("Use 'Interval Configuration : <seconds>' to change interval.")  # Send usage instructions

initialize_system()  # Call initialization function at program start

# Main Loop - Continuous program execution
while True:  # Infinite loop
    try:  # Main try block for error handling
        # UART Command Handling - Process incoming serial commands
        if uart.any():  # Check if there's data available on UART
            incoming = uart.read().decode('utf-8')  # Read UART data and decode from bytes to string
            uart_buffer += incoming  # Append new data to buffer
            if '\n' in uart_buffer:  # Check if buffer contains complete line (newline character)
                lines = uart_buffer.split('\n')  # Split buffer into individual lines
                for line in lines[:-1]:  # Process all complete lines (all except the last one)
                    line = line.strip()  # Remove leading and trailing whitespace from line
                    if line == "Restart Device":  # Check for system restart command
                        interval = 1  # Set interval to 1 second
                        save_interval(interval)  # Save interval to configuration file
                        initialize_system()  # Reinitialize the system
                    elif line.startswith("Interval Configuration :"):  # Check for interval configuration command
                        try:  # Try block for parsing interval value
                            parts = line.split(":")  # Split command at colon separator
                            if len(parts) > 1:  # Check if there's a value after colon
                                new_interval = int(parts[1].strip())  # Extract value, remove whitespace, convert to integer
                                if new_interval > 0:  # Validate that interval is positive
                                    interval = new_interval  # Update current interval
                                    save_interval(interval)  # Save new interval to configuration file
                                    uart_print("Interval updated to {} seconds.".format(interval))  # Send confirmation
                                else:  # Invalid interval value
                                    uart_print("Invalid interval: must be > 0.")  # Send error message
                            else:  # Malformed command
                                uart_print("Command format invalid.")  # Send format error
                        except ValueError:  # Catch integer conversion errors
                            uart_print("Invalid number. Use: Interval Configuration : <number>")  # Send number format error
                uart_buffer = lines[-1]  # Keep incomplete line in buffer for next iteration

        # Sensor Reading - Get UV index data from LTR390 sensor
        if sensor:  # Check if sensor is properly initialized
            uv = sensor.read_uv_index()  # Call sensor method to get UV index reading
            if uv is not None:  # Check if read was successful
                uart_print("LTR390: UV Index:{}".format(uv))  # Format and send UV index data
            else:  # Read failed or data not ready
                uart_print("UV data not ready")  # Send data not ready message
        else:  # Sensor not initialized
            uart_print("Sensor not initialized")  # Send initialization error message

    except Exception as e:  # Catch any exceptions in main loop
        uart_print("Error: {}".format(e))  # Send error message via UART
        print("Error:", e)  # Also print error to console for debugging

    time.sleep(interval)  # Wait for specified interval before next iteration
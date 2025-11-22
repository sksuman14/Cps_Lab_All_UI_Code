from machine import I2C, UART  # Import I2C and UART modules for hardware communication
import utime as time  # Import time module with alias for timing functions

# === UART Initialization === - Set up serial communication interface
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)  # Initialize UART2 with 115200 baud rate, 8 data bits, no parity, 1 stop bit

def uart_print(msg):  # Function to send messages over UART
    try:  # Try block for error handling
        uart.write((msg + "\r\n").encode())  # Convert message to bytes, add carriage return and newline, then send via UART
    except Exception as e:  # Catch any exceptions during UART write
        print("UART write error:", e)  # Print error to console as backup

# === File for saving interval === - Configuration file management
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

# === VL53L0X Registers === - Register addresses for VL53L0X time-of-flight sensor
VL53L0X_I2C_ADDR = 0x29  # I2C address of VL53L0X sensor
SYSRANGE_START          = 0x00  # Register to start distance measurement
SYSTEM_INTERRUPT_CLEAR  = 0x0B  # Register to clear interrupt status
FINAL_RANGE_MSB         = 0x1E  # Register for most significant byte of final range measurement
FINAL_RANGE_LSB         = 0x1F  # Register for least significant byte of final range measurement

# === I2C Helpers === - Low-level I2C communication functions
def write_reg(i2c, reg, val):  # Function to write a value to a specific register
    reg_addr = bytearray([reg])  # Create bytearray with register address
    data = bytearray([val])  # Create bytearray with data value
    i2c.write(VL53L0X_I2C_ADDR, reg_addr, 1, data, 1)  # Write data to register using I2C

def burst_read(i2c, start_reg, length):  # Function to read multiple bytes starting from a register
    reg_addr = bytearray([start_reg])  # Create bytearray with starting register address
    buf = bytearray(length)  # Create buffer to store read data
    i2c.write(VL53L0X_I2C_ADDR, b'', 0, reg_addr, 1)  # Write register address to set read pointer
    time.sleep_ms(1)  # Short delay for sensor to prepare data
    i2c.read(VL53L0X_I2C_ADDR, b'', 0, buf, length, 0)  # Read specified number of bytes into buffer
    return buf  # Return the read data

# === VL53L0X Driver === - Main sensor driver class
class VL53L0X:
    def __init__(self, i2c):  # Constructor method to initialize sensor
        self.i2c = i2c  # Store I2C object reference
        uart_print("VL53L0X initialized at 0x{:02X}".format(VL53L0X_I2C_ADDR))  # Print initialization message

    def read_distance(self):  # Method to read distance measurement from sensor
        try:  # Try block for error handling during sensor read
            # Start single measurement
            write_reg(self.i2c, SYSRANGE_START, 0x01)  # Write 0x01 to start register to begin measurement
            time.sleep_ms(50)  # Wait 50ms for measurement to complete

            # Read result - get distance data from sensor
            dist_bytes = burst_read(self.i2c, FINAL_RANGE_MSB, 2)  # Read 2 bytes (MSB and LSB) of distance data
            distance_mm = (dist_bytes[0] << 8) | dist_bytes[1]  # Combine MSB and LSB to get distance in millimeters
            distance_cm = distance_mm / 10.0  # Convert millimeters to centimeters

            # Clear interrupt - reset sensor for next measurement
            write_reg(self.i2c, SYSTEM_INTERRUPT_CLEAR, 0x01)  # Write 0x01 to clear interrupt register
            return distance_cm  # Return distance in centimeters
        except Exception as e:  # Catch any exceptions during distance reading
            uart_print("Error reading distance: {}".format(e))  # Send error message via UART
            return None  # Return None to indicate failure

# === Initialize I2C === - Set up I2C communication bus
i2c = I2C(I2C.I2C0, I2C.FAST_MODE)  # Initialize I2C0 interface in fast mode (400kHz)

# === Global Variables === - Shared variables across the program
interval = load_interval(default=1)  # Current measurement interval loaded from file or default
uart_buffer = ""  # Buffer to store incoming UART data
sensor = None  # Sensor object placeholder, will be initialized later

def initialize_system():  # Function to initialize or reinitialize the system
    global sensor, uart_buffer, interval  # Access global variables
    uart_buffer = ""  # Clear UART command buffer
    interval = load_interval()  # Load interval from configuration file
    try:  # Try to initialize sensor
        sensor = VL53L0X(i2c)  # Create VL53L0X sensor object
    except Exception as e:  # Catch sensor initialization errors
        uart_print("Sensor init error: {}".format(e))  # Send error message via UART
        sensor = None  # Set sensor to None on error
    uart_print("System Restarted. Current interval: {} seconds.".format(interval))  # Send startup message
    uart_print("Use 'Interval Configuration : <seconds>' to change interval.")  # Send usage instructions

initialize_system()  # Call initialization function at program start

# === Main Loop === - Continuous program execution
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

        # Sensor Reading - Get distance data from VL53L0X sensor
        if sensor:  # Check if sensor is properly initialized
            dist = sensor.read_distance()  # Call sensor method to get distance reading
            if dist is not None:  # Check if read was successful
                uart_print("VL53L0X: Distance = {:.2f} cm".format(dist))  # Format and send distance data
            else:  # Read failed
                uart_print("VL53L0X: Failed to read distance")  # Send failure message
        else:  # Sensor not initialized
            uart_print("Sensor not initialized")  # Send initialization error message

    except Exception as e:  # Catch any exceptions in main loop
        uart_print("Error: {}".format(e))  # Send error message via UART
        print("Error:", e)  # Also print error to console for debugging

    time.sleep(interval)  # Wait for specified interval before next iteration

from machine import I2C, UART  # Import I2C and UART modules for hardware communication
import utime as time  # Import time module with alias for timing functions
from usr.veml_7700_driver import VEML7700  # Import VEML7700 light sensor driver

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

def load_interval(default=2):  # Function to load interval value from file
    try:  # Try block for file operations
        val = open(CONFIG_FILE, "r").read().strip()  # Open file, read content, and remove whitespace
        return int(val) if val else default  # Convert to integer if not empty, else return default value
    except Exception:  # Catch all exceptions (file not found, invalid data, etc.)
        return default  # Return default value if loading fails

# Global Variables - Shared variables across the program
interval = load_interval(default=2)  # Current measurement interval loaded from file or default
uart_buffer = ""  # Buffer to store incoming UART data
veml = None  # VEML7700 sensor object placeholder, will be initialized later

# Initialize I2C - Set up I2C communication bus
i2c_dev = I2C(I2C.I2C0, I2C.FAST_MODE)  # Initialize I2C0 interface in fast mode (400kHz)

def initialize_system():  # Function to initialize or reinitialize the system
    global veml, uart_buffer, interval  # Access global variables
    uart_buffer = ""  # Clear UART command buffer
    interval = load_interval(default=2)  # Load interval from configuration file
    try:  # Try to initialize sensor
        veml = VEML7700(i2c_dev)  # Create VEML7700 sensor object using I2C device
        uart_print("VEML7700 Initialized.")  # Send initialization success message
    except Exception as e:  # Catch sensor initialization errors
        uart_print("VEML7700 init error: {}".format(e))  # Send error message via UART
        veml = None  # Set sensor to None on error
    uart_print("System Restarted. Interval: {} seconds.".format(interval))  # Send startup message
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
                        interval=1
                        save_interval(interval)
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

        # Sensor Reading - Get light intensity data from VEML7700 sensor
        if veml:  # Check if sensor is properly initialized
            lux = veml.lux()  # Call sensor method to get lux reading (light intensity)
            uart_print("VEML7700: Lux={:.2f}".format(lux))  # Format and send lux data with 2 decimal places
        else:  # Sensor not initialized
            uart_print("Sensor not initialized.")  # Send initialization error message

    except Exception as e:  # Catch any exceptions in main loop
        uart_print("Error: {}".format(e))  # Send error message via UART

    time.sleep(interval)  # Wait for specified interval before next iteration

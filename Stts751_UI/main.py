from machine import I2C, UART                                                              # Import I2C and UART modules for hardware communication
from usr.stts751 import STTS751                                                            # Import STTS751 temperature sensor driver
import utime as time                                                                       # Import time module with alias for timing functions

# UART Initialization - Set up serial communication interface
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)                                                  # Initialize UART2 with 115200 baud rate, 8 data bits, no parity, 1 stop bit

def uart_print(msg):                                                                        # Function to send messages over UART
    try:                                                                                    # Try block for error handling
        uart.write((msg + "\r\n").encode())                                                 # Convert message to bytes, add carriage return and newline, then send via UART
    except Exception as e:                                                                  # Catch any exceptions during UART write
        print("UART write error:", e)                                                       # Print error to console as backup

# File for saving interval - Configuration file path
CONFIG_FILE = "/usr/config.txt"                                                              # Path to configuration file for storing measurement interval

def save_interval(value):                                                                    # Function to save interval value to file
    try:                                                                                     # Try block for file operations
        with open(CONFIG_FILE, "w") as f:                                                    # Open file in write mode
            f.write(str(value))                                                              # Convert integer to string and save as plain text
    except Exception as e:                                                                   # Catch any file operation exceptions
        uart_print("Error saving interval: {}".format(e))                                    # Send error message via UART

def load_interval(default=1):                                                                # Function to load interval value from file
    try:                                                                                     # Try block for file operations
        with open(CONFIG_FILE, "r") as f:                                                    # Open file in read mode
            return int(f.read().strip())                                                     # Read file content, remove whitespace, convert to integer and return
    except:                                                                                  # Catch all exceptions (file not found, invalid data, etc.)
        return default                                                                       # Return default value if loading fails

# Global Variables - Shared variables across the program
interval = load_interval(default=1)                                                          # Current measurement interval loaded from file or default
uart_buffer = ""                                                                             # Buffer to store incoming UART data
sensor = None                                                                                # Sensor object placeholder, will be initialized later

# Initialize I2C - Set up I2C communication bus
i2c = I2C(I2C.I2C0, I2C.FAST_MODE)                                                           # Initialize I2C0 interface in fast mode (400kHz)

def initialize_system():                                                                     # Function to initialize or reinitialize the system
    global sensor, uart_buffer, interval                                                      # Access global variables
    uart_buffer = ""                                                                              # Clear UART command buffer
    interval = load_interval(default=1)                                                      # Load interval from configuration file
    sensor = STTS751(i2c, address=0x4a)                                                      # Initialize STTS751 temperature sensor with I2C address 0x48
    uart_print("System Restarted. Current interval: {} seconds.".format(interval))           # Send startup message
    uart_print("Use 'Interval Configuration : <seconds>' to change interval.")                  # Send usage instructions

initialize_system()                                                                           # Call initialization function at program start

# Main program loop - runs continuously
while True:                                                                                   # Infinite loop
    try:                                                                                       # Main try block for error handling
         # UART Command Handling - Process incoming serial commands
        if uart.any():                                                                        # Check if there's data available on UART
            incoming = uart.read().decode('utf-8')                                              # Read UART data and decode from bytes to string
            uart_buffer += incoming                                                           # Append new data to buffer

            if '\n' in uart_buffer:                                                           # Check if buffer contains complete line (newline character)
                lines = uart_buffer.split('\n')                                               # Split buffer into individual lines
                for line in lines[:-1]:                                                       # Process all complete lines (all except the last one)
                    line = line.strip()                                                         # Remove leading and trailing whitespace from line

                    if line == "Restart Device":                                                # Check for system restart command
                        interval=1
                        save_interval(interval)
                        initialize_system()                                                     # Reinitialize the system

                    elif line.startswith("Interval Configuration :"):                             # Check for interval configuration command
                        try:                                                                     # Try block for parsing interval value
                            parts = line.split(":")                                             # Split command at colon separator
                            if len(parts) > 1:                                                     # Check if there's a value after colon
                                new_interval = int(parts[1].strip())                             # Extract value, remove whitespace, convert to integer
                                if new_interval > 0:                                                # Validate that interval is positive
                                    interval = new_interval                                         # Update current interval
                                    save_interval(interval)                                           # Save new interval to configuration file
                                    uart_print("Interval updated to {} seconds.".format(interval))                   # Send confirmation
                                else:                                                                # Invalid interval value
                                    uart_print("Invalid interval: must be > 0.")                       # Send error message
                            else:                                                                    # Malformed command
                                uart_print("Command format invalid.")                                 # Send format error
                        except ValueError:                                                            # Catch integer conversion errors
                            uart_print("Invalid number. Use: Interval Configuration : <number>")            # Send number format error

                uart_buffer = lines[-1]                                                                    # Keep incomplete line in buffer for next iteration
                
        tempc = sensor.get_temperature()                      
        tempf = tempc * 1.8 + 32
        uart_print("STTS751: Temperature: {:.2f} °C | {:.2f} °F".format(tempc, tempf))

        time.sleep(interval)
    except Exception as e:                                                                                 # Catch any exceptions in main loop
        uart_print("Error: {}".format(e))                                                                 # Send error message via UART
        print("Sensor read error:", e)                                                                      # Also print error to console for debugging

    time.sleep(interval)                                                                                 # Wait for specified interval before next iteration
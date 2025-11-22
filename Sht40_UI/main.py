from machine import I2C, UART  # Import hardware interfaces for I2C and UART communication
from usr.sht4x import SHT4X  # Import SHT40 temperature/humidity sensor driver
import utime as time  # Import time functions with alias

# UART Initialization - Set up serial communication
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)  # UART2, 115200 baud, 8 data bits, no parity, 1 stop bit

def uart_print(msg):  # Function to send messages over UART
    try:  # Error handling for UART communication
        uart.write((msg + "\r\n").encode())  # Convert message to bytes and send with newline
    except Exception as e:  # Catch any UART write errors
        print("UART write error:", e)  # Print error to console as backup

# File for saving interval - Configuration storage
CONFIG_FILE = "/usr/config.txt"  # Path to configuration file

def save_interval(value):  # Function to save measurement interval to file
    try:  # Error handling for file operations
        with open(CONFIG_FILE, "w") as f:  # Open file in write mode
            f.write(str(value))   # Convert integer to string and save as plain text
    except Exception as e:  # Catch file write errors
        uart_print("Error saving interval: {}".format(e))  # Notify user via UART

def load_interval(default=2):  # Function to load interval from file
    try:  # Error handling for file operations
        with open(CONFIG_FILE, "r") as f:  # Open file in read mode
            return int(f.read().strip())  # Read content, remove whitespace, convert to integer
    except:  # Catch all exceptions (file not found, corrupt data, etc.)
        return default  # Return default value if loading fails

# Global Variables - Shared state across the program
interval = load_interval(default=2)  # Current measurement interval, loaded from file
uart_buffer = ""  # Buffer to accumulate incoming UART commands
sht = None  # Sensor object, will be initialized later

# Initialize I2C bus for sensor communication
i2c = I2C(I2C.I2C0, I2C.FAST_MODE)  # I2C0 interface, fast mode (400kHz)

def initialize_system():  # Function to set up or reset the system
    global sht, uart_buffer, interval  # Access global variables
    uart_buffer = ""  # Clear any pending UART commands
    interval = 1
    save_interval(interval)
    # interval = load_interval(default=1)  # Reload interval from persistent storage
    sht = SHT4X(i2c)  # Initialize SHT40 sensor on I2C bus
    uart_print("System Restarted. Current interval: {} seconds.".format(interval))  # Status message
   
interval = load_interval()
initialize_system()  # Call initialization function at program start

# Main program loop - runs continuously
while True:  # Infinite loop for continuous operation
    try:  # Main error handling block
        # UART Command Processing - Check for user input
        if uart.any():  # Check if data is available on UART
            incoming = uart.read().decode('utf-8')  # Read bytes and decode to string
            uart_buffer += incoming  # Append new data to buffer

            # Process complete lines (ending with newline)
            if '\n' in uart_buffer:  # Check if buffer contains complete command
                lines = uart_buffer.split('\n')  # Split buffer into individual lines
                # Process all complete lines (all but the last)
                for line in lines[:-1]:  # Iterate through complete commands
                    line = line.strip()  # Remove leading/trailing whitespace

                    # Command: Restart Device - Reinitialize system
                    if line == "Restart Device":  # Check for restart command
                        initialize_system()  # Reset system state

                    # Command: Interval Configuration - Change measurement interval
                    elif line.startswith("Interval Configuration :"):  # Check for config command
                        try:  # Error handling for interval parsing
                            parts = line.split(":")  # Split command at colon
                            if len(parts) > 1:  # Ensure value is present
                                new_interval = int(parts[1].strip())  # Extract and convert interval
                                if new_interval > 0:  # Validate positive interval
                                    interval = new_interval  # Update current interval
                                    save_interval(interval)  # Persist to file
                                    uart_print("Interval updated to {} seconds.".format(interval))  # Confirm
                                else:  # Invalid interval value
                                    uart_print("Invalid interval: must be > 0.")  # Error message
                            else:  # Malformed command
                                uart_print("Command format invalid.")  # Syntax error
                        except ValueError:  # Catch number conversion errors
                            uart_print("Invalid number. Use: Interval Configuration : <number>")  # Help message

                uart_buffer = lines[-1]  # Keep incomplete line in buffer for next iteration

        # Read Sensor Data - Main measurement task
        temperature = sht.get_temperature()  # Get temperature from SHT40 sensor
        humidity = sht.get_humidity()  # Get relative humidity from SHT40 sensor
        uart_print("SHT40:Temperature:{}°C, Humidity:{}%".format(temperature, humidity))  # Output formatted data

    except Exception as e:  # Catch any errors in main loop
        uart_print("Error: {}".format(e))  # Send error message via UART
        print("Sensor read error:", e)  # Also print to console for debugging

    time.sleep(interval)  # Wait for specified interval before next measurement

# from misc import ADC
# import utime

# adc = ADC()
# adc.open()

# # AO pin connected to ADC0
# threshold = 2000  # Set depending on your AO output

# while True:
#     val = adc.read(ADC.ADC0)  # Read analog voltage
#     if val > threshold:
#         print("1  # Magnet detected")
#     else:
#         print("0  # No magnet")
    
#     print("AO Value:", val)
#     utime.sleep(1)





from misc import ADC  # Import ADC module for analog input functionality
from machine import UART  # Import UART module for serial communication
import utime as time  # Import time module for delays and timing operations

#  UART Initialization
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)  # Initialize UART2 at 115200 baud, 8N1 configuration

def uart_print(msg):  # Function to print messages via UART safely
    try:
        uart.write((msg + "\r\n").encode())  # Encode and send message through UART with newline
    except Exception as e:
        print("UART write error:", e)  # Print error to console if UART fails

# File for saving interval
CONFIG_FILE = "/usr/config.txt"  # File path used to store interval setting

def save_interval(value):  # Function to save interval value into file
    try:
        with open(CONFIG_FILE, "w") as f:  # Open file in write mode
            f.write(str(value))  # Write interval value as string
    except Exception as e:
        uart_print("Error saving interval: {}".format(e))  # Print error message if saving fails

def load_interval(default=1):  # Function to load saved interval from file
    try:
        val = open(CONFIG_FILE, "r").read().strip()  # Read stored value and remove extra spaces
        return int(val) if val else default  # Convert to int if valid, else return default
    except:
        return default  # Return default if file missing or invalid

#  Initialize ADC for AO pin
adc = ADC()  # Create ADC object
adc.open()  # Initialize ADC hardware
threshold = 2000  # Set threshold for detecting magnet via AO signal level

# Global Variables
interval = load_interval(default=1)  # Load stored interval or default to 2 seconds
uart_buffer = ""  # Initialize empty UART receive buffer

def initialize_system():  # Function to reset and reinitialize system
    global interval, uart_buffer  # Access global variables
    uart_buffer = ""  # Clear UART buffer
    interval = load_interval(default=1)  # Reload stored interval
    uart_print("System Restarted. Interval: {} sec".format(interval))  # Notify via UART
    # uart_print("Use 'Interval Configuration : <seconds>' to change interval.")  # Print usage info

initialize_system()  # Call initialization function once at startup

#  Main Loop 
while True:  # Continuous execution loop
    try:
        # UART command handling
        if uart.any():  # Check if UART has received data
            incoming = uart.read().decode('utf-8')  # Read available bytes and decode
            uart_buffer += incoming  # Append new data to buffer

            if '\n' in uart_buffer:  # Process if newline found (end of command)
                lines = uart_buffer.split('\n')  # Split multiple commands by newline
                for line in lines[:-1]:  # Iterate over complete commands
                    line = line.strip()  # Remove spaces

                    if line == "Restart Device":  # Command to restart system
                        interval = 1  # Set interval to 1 second
                        save_interval(interval)  # Save to file
                        initialize_system()  # Reinitialize

                    elif line.startswith("Interval Configuration :"):  # Command to set new interval
                        try:
                            parts = line.split(":")  # Split command and value
                            if len(parts) > 1:  # Check for value part
                                new_interval = int(parts[1].strip())  # Convert value to integer
                                if new_interval > 0:  # Ensure positive interval
                                    interval = new_interval  # Update global interval
                                    save_interval(interval)  # Save new interval to file
                                    uart_print("Interval updated: {} sec".format(interval))  # Confirm update
                                else:
                                    uart_print("Invalid interval (>0)")  # Warn invalid interval
                            else:
                                uart_print("Command format invalid")  # Missing value part
                        except ValueError:
                            uart_print("Invalid number")  # Handle non-numeric input

                uart_buffer = lines[-1]  # Keep incomplete command (if any) in buffer

        # Read AO value
        ao_val = adc.read(ADC.ADC0)  # Read analog output from ADC channel 0
        if ao_val > threshold:  # Compare with magnet detection threshold
            magnet_state = 0  # Magnet not detected (high analog voltage)
        else:
            magnet_state = 1  # Magnet detected (low analog voltage)

        uart_print("Hall Sensor: State={}, AO={}".format(magnet_state, ao_val))  # Send sensor state via UART

    except Exception as e:
        uart_print("Error: {}".format(e))  # Print runtime errors safely

    time.sleep(interval)  # Wait for defined interval before next reading

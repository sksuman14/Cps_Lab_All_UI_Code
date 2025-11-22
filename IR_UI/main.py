# from misc import ADC  # (Commented) Import ADC module for analog input
# import utime  # (Commented) Import utime for delay and timing functions

# # Initialize ADC
# adc = ADC()  # Create ADC instance
# adc.open()  # Open ADC channel for reading

# # Adjust threshold experimentally
# threshold = 1500  # Set detection threshold (tune as needed)

# while True:  # Infinite loop for continuous readings
#     val = adc.read(ADC.ADC0)  # Read analog value from ADC0
    
#     if val < threshold:   # If ADC value below threshold, object close
#         print("1  # Object detected")  # Print detection
#     else:
#         print("0  # No object")  # Print no detection
    
#     utime.sleep(0.5)  # Wait 0.5 seconds before next read


from misc import ADC  # Import ADC class to read analog input (IR sensor)
from machine import UART  # Import UART class for serial communication
import utime  # Import utime for timing and sleep functions

# === Initialize ADC and UART ===
adc = ADC()  # Create an instance of the ADC class
adc.open()  # Open ADC to prepare it for reading

uart = UART(UART.UART2, 115200, 8, 0, 1, 0)  # Initialize UART2 with baud rate 115200, 8 data bits, no parity, 1 stop bit, and no flow control

# File to store interval
CONFIG_FILE = "/usr/config.txt"  # File path where the interval configuration is stored

def uart_print(msg):  # Function to print messages through UART
    try:
        uart.write((msg + "\r\n").encode())  # Write message to UART with carriage return and newline
    except Exception as e:
        print("UART write error:", e)  # If UART fails, print error to console

def save_interval(value):  # Function to save time interval into file
    try:
        with open(CONFIG_FILE, "w") as f:  # Open the config file in write mode
            f.write(str(value))  # Write interval value as string
    except Exception as e:
        uart_print("Error saving interval: {}".format(e))  # Send error message through UART

def load_interval(default=1):  # Function to load saved interval or return default value
    try:
        val = open(CONFIG_FILE, "r").read().strip()  # Read stored interval value and strip whitespace
        return int(val) if val else default  # Return integer if valid, else default
    except Exception:
        return default  # If reading fails, return default value

# === Global Variables ===
interval = load_interval(default=1)  # Load interval value from file or set default to 1 second
uart_buffer = ""  # Initialize UART buffer for incoming data
threshold = 1500  # Define ADC threshold for object detection (lower = object closer)

def initialize_system():  # Function to initialize or reset system variables
    global interval, uart_buffer  # Use global variables inside function
    uart_buffer = ""  # Reset UART input buffer
    interval = load_interval(default=1)  # Reload interval from file
    uart_print("System Restarted. Current interval: {} seconds.".format(interval))  # Print restart message
    # uart_print("Use 'Interval Configuration : <seconds>' to change interval.")  # Print instructions for configuration

# Initialize system
initialize_system()  # Run system initialization on startup

# === Main Loop ===
while True:  # Continuous loop for sensor monitoring and command handling
    try:
        # UART command handling
        if uart.any():  # Check if UART has received any data
            incoming = uart.read().decode('utf-8')  # Read available data and decode from bytes to string
            uart_buffer += incoming  # Append received characters to buffer
            if '\n' in uart_buffer:  # Check if a full line (command) is received
                lines = uart_buffer.split('\n')  # Split received data into lines
                for line in lines[:-1]:  # Iterate over complete lines (ignore last if incomplete)
                    line = line.strip()  # Remove whitespace
                    if line == "Restart Device":  # Check if command is to restart device
                        interval = 1  # Set interval to 1 second
                        save_interval(interval)  # Save interval to file
                        initialize_system()  # Call initialize function
                    elif line.startswith("Interval Configuration :"):  # Check for interval configuration command
                        try:
                            parts = line.split(":")  # Split command string at colon
                            if len(parts) > 1:  # Ensure value part exists
                                new_interval = int(parts[1].strip())  # Convert provided value to integer
                                if new_interval > 0:  # Validate interval (must be positive)
                                    interval = new_interval  # Update global interval
                                    save_interval(interval)  # Save updated interval to file
                                    uart_print("Interval updated to {} seconds.".format(interval))  # Confirm change
                                else:
                                    uart_print("Invalid interval (>0)")  # Invalid interval warning
                            else:
                                uart_print("Command format invalid")  # Missing or incorrect format message
                        except ValueError:  # Handle invalid number input
                            uart_print("Invalid number")  # Print invalid number message
                uart_buffer = lines[-1]  # Keep leftover (incomplete) command data for next read

        # === IR Sensor Reading ===
        val = adc.read(ADC.ADC0)  # Read analog value from ADC0 pin
        if val < threshold:  # If analog value below threshold → object detected
            uart_print(" IR Sensor: Infrared = 0 ")  # Send detection message over UART
        else:
            uart_print(" IR Sensor: Infrared = 1 ")  # Send no-object message over UART

    except Exception as e:  # Handle unexpected errors
        uart_print("Error: {}".format(e))  # Print error through UART
        print("Error:", e)  # Also print error to console

    utime.sleep(interval)  # Wait for defined interval before next reading

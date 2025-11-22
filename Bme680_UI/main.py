from machine import I2C, UART
import utime as time
from usr.bmedriver import BME680

# UART Initialization 
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)  # Initialize UART2 with baud rate 115200, 8 data bits, no parity, 1 stop bit

def uart_print(msg):
    try:
        uart.write((msg + "\r\n").encode())  # Send message via UART followed by carriage return and newline
    except Exception as e:
        print("UART write error:", e)  # Print error message in case UART write fails

#  File for saving interval
CONFIG_FILE = "/usr/config.txt"  # File path used to store the sensor reading interval

def save_interval(value):
    """Save the current interval value to a configuration file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(str(value))  # Write the interval value to file
    except Exception as e:
        uart_print("Error saving interval: {}".format(e))  # Report error if file operation fails

def load_interval(default=2):
    """Load the interval value from the configuration file; return default if unavailable."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return int(f.read().strip())  # Read and convert stored value to integer
    except:
        return default  # Return default value if file not found or invalid content

#  Global variables 
interval = load_interval(default=2)  # Load interval from file or use default (2 seconds)
uart_buffer = ""  # Buffer for incoming UART commands
sensor = None  # Global variable for the BME680 sensor instance

# Initialize I2C and sensor
i2c = I2C(I2C.I2C0, I2C.FAST_MODE)  # Initialize I2C0 in fast mode for communication with sensor

def wait_for_data(sensor, timeout_ms=1000):
    """Wait for sensor data to be ready, up to timeout_ms milliseconds."""
    start = time.ticks_ms()  # Record start time
    while True:
        if sensor.get_sensor_data():  # Check if sensor has data ready
            return True
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:  # Check for timeout
            return False
        time.sleep_ms(50)  # Wait briefly before checking again

def initialize_system():
    """Initialize or restart system: sensor, UART buffer, and configuration."""
    global sensor, uart_buffer, interval
    uart_buffer = ""  # Clear UART buffer
    interval = load_interval(default=2)  # Reload saved interval value

    sensor = BME680(i2c)  # Create BME680 sensor instance using I2C bus
    sensor.soft_reset()  # Perform soft reset on the sensor
    time.sleep_ms(100)  # Give time for sensor to stabilize after reset

    # Configure oversampling and filter settings for better accuracy
    sensor.set_humidity_oversample(2)
    sensor.set_pressure_oversample(3)
    sensor.set_temperature_oversample(4)
    sensor.set_filter(2)

    # Notify via UART that system has restarted and show current interval
    uart_print("System Restarted. Current interval: {} seconds.".format(interval))
    # uart_print("Use 'Interval Configuration : <seconds>' to change interval.")

initialize_system()  # Perform initial setup

# Main program loop
while True:
    try:
        #  UART command handling
        if uart.any():  # Check if there is incoming UART data
            incoming = uart.read().decode('utf-8')  # Read and decode incoming bytes
            uart_buffer += incoming  # Append to UART buffer

            if '\n' in uart_buffer:  # Process commands when newline is detected
                lines = uart_buffer.split('\n')
                for line in lines[:-1]:
                    line = line.strip()  # Clean up extra spaces and newline characters

                    if line == "Restart Device":  # Command to restart device
                        interval = 1
                        save_interval(interval)
                        initialize_system()

                    elif line.startswith("Interval Configuration :"):  # Command to change data interval
                        try:
                            parts = line.split(":")
                            if len(parts) > 1:
                                new_interval = int(parts[1].strip())  # Parse new interval value
                                if new_interval > 0:
                                    interval = new_interval  # Update global interval
                                    save_interval(interval)  # Save new interval to file
                                    uart_print("Interval updated to {} seconds.".format(interval))
                                else:
                                    uart_print("Invalid interval: must be > 0.")  # Reject non-positive values
                            else:
                                uart_print("Command format invalid.")  # If command format is wrong
                        except ValueError:
                            uart_print("Invalid number. Use: Interval Configuration : <number>")  # Handle non-integer inputs

                uart_buffer = lines[-1]  # Keep the incomplete command (if any) for next loop

        #  Read sensor data 
        if wait_for_data(sensor):  # Check if sensor data is ready
            try:
                t = sensor.data.temperature  # Read temperature
                p = sensor.data.pressure  # Read pressure
                h = sensor.data.humidity  # Read humidity
                # Send formatted sensor readings via UART
                uart_print("BME680: Temperature: {:.2f} °C, Pressure: {:.2f} hPa, Humidity: {:.2f} %".format(t, p, h))
            except Exception as e:
                uart_print("[ERROR] Failed to read sensor values: {}".format(e))  # Handle data read errors
        else:
            uart_print("[ERROR] Sensor data not ready after timeout.")  # Handle data timeout errors

    except Exception as e:
        uart_print("Error: {}".format(e))  # Report generic error to UART
        print("Sensor read error:", e)  # Print for debugging

    time.sleep(interval)  # Wait for specified interval before next reading

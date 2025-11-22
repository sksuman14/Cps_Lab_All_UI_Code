from machine import I2C, UART  # Import I2C and UART modules for hardware communication
import utime as time  # Import time module with alias for timing functions

# UART Initialization - Set up serial communication interface
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)  # Initialize UART2 with 115200 baud rate, 8 data bits, no parity, 1 stop bit

def uart_print(msg):  # Function to send messages over UART
    try:  # Try block for error handling
        uart.write((msg + "\r\n").encode())  # Convert message to bytes, add carriage return and newline, then send via UART
    except Exception as e:  # Catch any exceptions during UART write
        # fallback to console if UART write fails
        print("UART write error:", e)  # Print error to console as backup

# === Config file helpers - Configuration file management ===
CONFIG_FILE = "/usr/config.txt"  # Path to configuration file for storing measurement interval
def save_interval(value):  # Function to save interval value to file
    try:  # Try block for file operations
        with open(CONFIG_FILE, "w") as f:  # Open file in write mode
            f.write(str(value))  # Convert integer to string and save as plain text
    except Exception as e:  # Catch any file operation exceptions
        uart_print("Error saving interval: {}".format(e))  # Send error message via UART

def load_interval(default=1):  # Function to load interval value from file
    try:  # Try block for file operations
        with open(CONFIG_FILE, "r") as f:  # Open file in read mode
            val = f.read().strip()  # Read file content and remove whitespace
            return int(val) if val else default  # Convert to integer if not empty, else return default
    except Exception:  # Catch all exceptions (file not found, invalid data, etc.)
        return default  # Return default value if loading fails

# I2C setup - Initialize I2C communication for TLV493D sensor
I2C_ADDR = 0x5E  # I2C address of TLV493D magnetic sensor
i2c = I2C(I2C.I2C0, I2C.FAST_MODE)  # Initialize I2C0 interface in fast mode (400kHz)

# Robust I2C read / write wrappers (tries multiple call signatures)
def i2c_write_try(addr, data):  # Function to write data to I2C device with multiple method attempts
    """Try several i2c.write signatures until one works."""
    # data: bytearray or bytes
    last_e = None  # Variable to store last error encountered
    try:  # Attempt first write method
        i2c.write(addr, data)  # Simple write method
        return  # Exit if successful
    except Exception as e:  # Catch write exception
        last_e = e  # Store error
    try:  # Attempt second write method
        # some platforms accept (addr, b'', 0, data, len)
        i2c.write(addr, b'', 0, data, len(data))  # Extended write method
        return  # Exit if successful
    except Exception as e:  # Catch write exception
        last_e = e  # Store error
    try:  # Attempt third write method
        # try writeto_mem if available (reg at first byte)
        if hasattr(i2c, "writeto_mem") and len(data) >= 2:  # Check if method exists and data length sufficient
            reg = data[0]  # Extract register address from first byte
            payload = data[1:]  # Extract payload from remaining bytes
            i2c.writeto_mem(addr, reg, payload)  # Write to specific memory address
            return  # Exit if successful
    except Exception as e:  # Catch write exception
        last_e = e  # Store error
    # give up - all methods failed
    raise Exception("i2c write failed, last error: {}".format(last_e))  # Raise final exception

def i2c_read_try(addr, reg, length):  # Function to read data from I2C device with multiple method attempts
    """Try multiple ways to read 'length' bytes starting at register 'reg'.
       Returns bytearray of length bytes on success or raises Exception."""
    buf = bytearray(length)  # Create buffer to store read data
    last_e = None  # Variable to store last error encountered
    # Variant 1: read(addr, reg, buf, regaddr_len)
    try:  # Attempt first read method
        i2c.read(addr, reg, buf, 1)  # Read with register address
        return buf  # Return buffer if successful
    except Exception as e:  # Catch read exception
        last_e = e  # Store error
    # Variant 2: read(addr, buf, regaddr=reg, regaddr_len=1)
    try:  # Attempt second read method
        i2c.read(addr, buf, regaddr=reg, regaddr_len=1)  # Read with named parameters
        return buf  # Return buffer if successful
    except Exception as e:  # Catch read exception
        last_e = e  # Store error
    # Variant 3: write reg then read using two-step low-level signature
    try:  # Attempt third read method (two-step process)
        reg_buf = bytearray([reg])  # Create register address buffer
        # Write register pointer
        try:  # Attempt to write register address
            i2c.write(addr, b'', 0, reg_buf, 1)  # Extended write method
        except Exception:  # Catch write exception
            # fallback to simple write(addr, [reg])
            i2c.write(addr, reg_buf)  # Simple write method fallback
        time.sleep_ms(2)  # Short delay for sensor processing
        # Read into buf using the style seen in some examples
        i2c.read(addr, b'', 0, buf, length, 0)  # Extended read method
        return buf  # Return buffer if successful
    except Exception as e:  # Catch read exception
        last_e = e  # Store error
    # Variant 4: readfrom_mem (MicroPython)
    try:  # Attempt fourth read method
        if hasattr(i2c, "readfrom_mem"):  # Check if method exists
            tmp = i2c.readfrom_mem(addr, reg, length)  # Read from memory address
            if isinstance(tmp, (bytes, bytearray)):  # Check if valid data type
                buf[:] = tmp  # Copy data to buffer
                return buf  # Return buffer if successful
    except Exception as e:  # Catch read exception
        last_e = e  # Store error
    # Variant 5: direct read(addr, buf) - no reg
    try:  # Attempt fifth read method (direct read)
        i2c.read(addr, buf)  # Direct read without register address
        return buf  # Return buffer if successful
    except Exception as e:  # Catch read exception
        last_e = e  # Store error

    raise Exception("I2C read failed all variants, last error: {}".format(last_e))  # Raise final exception

# TLV493D helpers - Functions for TLV493D magnetic sensor operations
def twos_complement(val, bits=12):  # Convert two's complement values to signed integers
    if val & (1 << (bits - 1)):  # Check if value is negative (MSB set)
        val -= 1 << bits  # Convert from two's complement to signed integer
    return val  # Return signed value

def enable_continuous_measurement():  # Enable continuous measurement mode on TLV493D
    """Try to enable continuous measurement. TLV493D needs a write to register 0x10."""
    try:  # Attempt to enable continuous mode
        # Common simple form: write register 0x10 value 0x01
        i2c_write_try(I2C_ADDR, bytearray([0x10, 0x01]))  # Write configuration to sensor
        time.sleep_ms(20)  # Wait for sensor to initialize
        return True  # Return success
    except Exception as e:  # Catch configuration exception
        uart_print("TLV493D: enable_cont failed: {}".format(e))  # Send error message
        return False  # Return failure

def parse_6byte_frame(buf6):  # Parse 6-byte data frame from TLV493D
    # buf6 length must be 6
    x_raw = ((buf6[1] & 0x0F) << 8) | (buf6[0] & 0xFF)  # Extract X-axis raw data (12-bit)
    y_raw = ((buf6[3] & 0x0F) << 8) | (buf6[2] & 0xFF)  # Extract Y-axis raw data (12-bit)
    z_raw = ((buf6[5] & 0x0F) << 8) | (buf6[4] & 0xFF)  # Extract Z-axis raw data (12-bit)
    x = twos_complement(x_raw, 12)  # Convert X-axis to signed integer
    y = twos_complement(y_raw, 12)  # Convert Y-axis to signed integer
    z = twos_complement(z_raw, 12)  # Convert Z-axis to signed integer
    return x, y, z  # Return parsed values

def parse_10byte_frame(buf10):  # Parse 10-byte data frame from TLV493D (alternative format)
    # alternative packing used on some breakouts
    bx = ((buf10[0] << 4) | (buf10[4] & 0x0F)) & 0xFFF  # Extract X-axis raw data (12-bit)
    by = ((buf10[1] << 4) | ((buf10[4] >> 4) & 0x0F)) & 0xFFF  # Extract Y-axis raw data (12-bit)
    bz = ((buf10[2] << 4) | (buf10[5] & 0x0F)) & 0xFFF  # Extract Z-axis raw data (12-bit)
    bx = twos_complement(bx, 12)  # Convert X-axis to signed integer
    by = twos_complement(by, 12)  # Convert Y-axis to signed integer
    bz = twos_complement(bz, 12)  # Convert Z-axis to signed integer
    return bx, by, bz  # Return parsed values

def read_tlv493d_values():  # Main function to read magnetic field values from TLV493D
    """Try to read TLV493D; return (x_mT, y_mT, z_mT) or (None,None,None) on failure."""
    # Ensure continuous measurement mode is enabled at least once
    enable_continuous_measurement()  # Configure sensor for continuous reading
    # Try 6-byte read parsing first
    try:  # Attempt 6-byte read method
        b6 = i2c_read_try(I2C_ADDR, 0x00, 6)  # Read 6 bytes from sensor
        # If all zeros, try alternative
        if any(b6):  # Check if data contains non-zero values
            x,y,z = parse_6byte_frame(b6)  # Parse 6-byte frame
            # convert to mT (milliTesla)
            scale = 0.098  # Conversion factor from raw data to milliTesla
            return round(x*scale, 3), round(y*scale, 3), round(z*scale, 3)  # Return scaled values
    except Exception as e:  # Catch read/parse exception
        # keep going to try 10-byte variant
        uart_print("TLV493D: 6-byte read failed: {}".format(e))  # Send error message

    # Try 10-byte read variant
    try:  # Attempt 10-byte read method
        b10 = i2c_read_try(I2C_ADDR, 0x00, 10)  # Read 10 bytes from sensor
        if any(b10):  # Check if data contains non-zero values
            x,y,z = parse_10byte_frame(b10)  # Parse 10-byte frame
            scale = 0.098  # Conversion factor from raw data to milliTesla
            return round(x*scale, 3), round(y*scale, 3), round(z*scale, 3)  # Return scaled values
    except Exception as e:  # Catch read/parse exception
        uart_print("TLV493D: 10-byte read failed: {}".format(e))  # Send error message

    return None, None, None  # Return failure indication

# Global control / initialization - System state variables
interval = load_interval()  # Current measurement interval loaded from file or default
uart_buffer = ""  # Buffer to store incoming UART data
interval=1
def initialize_system():  # Function to initialize or reinitialize the system
    global interval, uart_buffer  # Access global variables
    uart_buffer = ""  # Clear UART command buffer
    interval = load_interval()  # Load interval from configuration file
    # try to enable continuous measurement explicitly on init
    enable_continuous_measurement()  # Configure sensor for continuous reading
    uart_print("System Restarted. Current interval: {} seconds.".format(interval))  # Send startup message
    # uart_print("Use 'Interval Configuration : <seconds>' to change interval.")  # Send usage instructions
    # uart_print("Send 'Restart Device' to reinitialize.")  # Send restart instructions

initialize_system()  # Call initialization function at program start

# === Main loop === - Continuous program execution
while True:  # Infinite loop
    try:  # Main try block for error handling
        # Handle UART commands (exact same style as your SHT4x code)
        if uart.any():  # Check if there's data available on UART
            incoming = uart.read().decode('utf-8')  # Read UART data and decode from bytes to string
            uart_buffer += incoming  # Append new data to buffer
            if '\n' in uart_buffer:  # Check if buffer contains complete line (newline character)
                lines = uart_buffer.split('\n')  # Split buffer into individual lines
                for line in lines[:-1]:  # Process all complete lines (all except the last one)
                    cmd = line.strip()  # Remove leading and trailing whitespace from command
                    if cmd == "Restart Device":  # Check for system restart command
                        interval=1
                        save_interval(interval)
                        initialize_system()  # Reinitialize the system
                    elif cmd.startswith("Interval Configuration :"):  # Check for interval configuration command
                        try:  # Try block for parsing interval value
                            parts = cmd.split(":")  # Split command at colon separator
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

        # Read TLV493D values robustly
        x_mT, y_mT, z_mT = read_tlv493d_values()  # Get magnetic field readings from sensor
        if x_mT is not None:  # Check if read was successful
            uart_print("TLV493D: X={} mT, Y={} mT, Z={} mT".format(x_mT, y_mT, z_mT))  # Format and send sensor data
        else:  # Read failed
            uart_print("TLV493D: Read failed")  # Send failure message

    except Exception as e:  # Catch any exceptions in main loop
        uart_print("Error: {}".format(e))  # Send error message via UART

    time.sleep(interval)  # Wait for specified interval before next iteration
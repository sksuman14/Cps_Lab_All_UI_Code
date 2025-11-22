import _thread
import utime
from machine import UART
from queue import Queue

# ----------------------------------------------
# GLOBAL CONFIG
# ----------------------------------------------
CONFIG_FILE = "/usr/config.txt"
uart_buffer = ""
interval = 1  # default interval

uart2 = UART(UART.UART2, 115200, 8, 0, 1, 0)  # Sensor UART
uart1 = UART(UART.UART1, 115200, 8, 0, 1, 0)  # Command UART

data_queue = Queue(5)

# WIND DATA STORAGE (GLOBAL)
last_wind_speed = None
last_wind_direction = None

# ----------------------------------------------
# UART PRINT
# ----------------------------------------------
def uart_print(msg):
    try:
        uart1.write((msg + "\r\n").encode())
    except Exception as e:
        print("UART1 write error:", e)


# ----------------------------------------------
# SAVE / LOAD INTERVAL
# ----------------------------------------------
def save_interval(value):
    global interval
    interval = value
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(str(value))
    except Exception as e:
        uart_print("Error saving interval: {}".format(e))

def load_interval(default=1):
    try:
        with open(CONFIG_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return default

# ----------------------------------------------
# INITIALIZE SYSTEM
# ----------------------------------------------
def initialize_system():
    global uart_buffer, interval

    uart_buffer = ""           # clear UART1 buffer
    interval = load_interval(default=1)

    uart_print("System Restarted. Current interval: {} seconds.".format(interval))


# Load interval BEFORE starting system
interval = load_interval(default=1)
initialize_system()


# ----------------------------------------------
# UART1 COMMAND HANDLER
# ----------------------------------------------
def handle_uart_commands():
    global uart_buffer, interval

    try:
        if uart1.any():
            incoming = uart1.read().decode("utf-8")
            uart_buffer += incoming

            if "\n" in uart_buffer:
                lines = uart_buffer.split("\n")

                for line in lines[:-1]:
                    line = line.strip()

                    # Restart Device
                    if line == "Restart Device":
                        interval = 1
                        save_interval(interval)
                        initialize_system()

                    # Interval Configuration
                    elif line.startswith("Interval Configuration :"):
                        try:
                            parts = line.split(":")
                            if len(parts) > 1:
                                new_interval = int(parts[1].strip())
                                if new_interval > 0:
                                    interval = new_interval
                                    save_interval(interval)
                                    uart_print("Interval updated to {} seconds.".format(interval))
                                else:
                                    uart_print("Invalid interval: must be > 0.")
                            else:
                                uart_print("Command format invalid.")
                        except ValueError:
                            uart_print("Invalid number. Use: Interval Configuration : <number>")

                uart_buffer = lines[-1]

    except Exception as e:
        uart_print("UART handler error: {}".format(e))


# ----------------------------------------------
# UART2 CALLBACK – SENSOR INPUT ONLY (NO PRINTING)
# ----------------------------------------------
def callback(para):
    if para[0] == 0:  # valid data available
        data_queue.put(para[2])

uart2.set_callback(callback)


# ----------------------------------------------
# READ UART2 SENSOR DATA
# ----------------------------------------------
def uart_read(length):
    msg = uart2.read(length)
    if msg:
        utf8_msg = msg.decode()
        extract_data(utf8_msg)
    return msg


def handler_thread():
    while True:
        recv_len = data_queue.get()
        uart_read(recv_len)

_thread.start_new_thread(handler_thread, ())


# ----------------------------------------------
# PARSE WIND SENSOR DATA (STORE ONLY)
# ----------------------------------------------
def extract_data(uart_msg):
    global last_wind_speed, last_wind_direction

    try:
        data = uart_msg.split(",")

        for i in range(0, len(data)-1, 2):
            key = data[i].strip().upper()
            value = float(data[i+1].strip())

            if key == "WS":
                last_wind_speed = value
            elif key == "WD":
                last_wind_direction = value

    except:
        pass  # ignore errors silently (sensor noise)


# ----------------------------------------------
# MAIN LOOP – PRINT ONLY AT INTERVAL
# ----------------------------------------------
while True:
    handle_uart_commands()

    if last_wind_speed is not None and last_wind_direction is not None:
        msg = "Wind speed: {:.2f}, Wind direction: {:.2f}".format(
                last_wind_speed, last_wind_direction)
        uart_print(msg)

    utime.sleep(interval)

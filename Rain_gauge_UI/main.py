from misc import ADC  # type: ignore
from machine import UART  # type: ignore
import utime
import _thread

# ---------------- UART Initialization ----------------
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)

def uart_print(msg):
    try:
        uart.write((msg + "\r\n").encode())
    except Exception as e:
        print("UART write error:", e)

# ---------------- ADC Initialization ----------------
adc = ADC()
adc.open()

# ---------------- Global Variables ----------------
rain_fall_count = 0
uart_buffer = ""
interval = 1  # default interval in seconds

# ---------------- Save/Load Interval ----------------
CONFIG_FILE = "/usr/interval.txt"

def save_interval(value):
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(str(value))
    except Exception as e:
        uart_print("Error saving interval: {}".format(e))

def load_interval(default=1):
    try:
        val = open(CONFIG_FILE, "r").read().strip()
        return int(val) if val else default
    except:
        return default

interval = load_interval()

# ---------------- ADC Loop ----------------
def adc_loop():
    global rain_fall_count, interval
    uart_print("Starting ADC Rain Tip Detection...")
    while True:
        try:
            adcVal = adc.read(ADC.ADC0)
            if adcVal > 1000:  # rain tip detected
                rain_fall_count += 1
                uart_print("Rain Tip Detected! Rainfall: {}".format(rain_fall_count))
                utime.sleep(interval)  # debounce using dynamic interval
            utime.sleep(0.1)
        except Exception as e:
            uart_print("ADC Loop Error: {}".format(e))

# ---------------- UART Command Handler ----------------
def uart_loop():
    global rain_fall_count, uart_buffer, interval
    while True:
        try:
            if uart.any():
                incoming = uart.read().decode('utf-8')
                uart_buffer += incoming

                if '\n' in uart_buffer:
                    lines = uart_buffer.split('\n')
                    for line in lines[:-1]:
                        line = line.strip()

                        # Restart device
                        if line == "Restart Device":
                            rain_fall_count = 0
                            interval = 1  # reset to default
                            save_interval(interval)  # persist default
                            uart_print("Device restarted. Rainfall counter reset to 0.")

                        # Change interval
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
            utime.sleep(0.1)
        except Exception as e:
            uart_print("UART Loop Error: {}".format(e))

# ---------------- Start Threads ----------------
_thread.start_new_thread(adc_loop, ())
_thread.start_new_thread(uart_loop, ())

# ---------------- Keep Main Alive ----------------
while True:
    utime.sleep(1)


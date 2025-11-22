# from machine import I2C, UART
# import utime as time
# from usr.bmedriver import BME680
# from usr.veml_7700_driver import VEML7700

# # -----------------------------
# # UART Initialization
# # -----------------------------
# uart = UART(UART.UART2, 115200, 8, 0, 1, 0)

# def uart_print(msg):
#     try:
#         uart.write((msg + "\r\n").encode())
#     except Exception as e:
#         print("UART write error:", e)

# # -----------------------------
# # Config File for Interval
# # -----------------------------
# CONFIG_FILE = "/usr/config.txt"

# def save_interval(value):
#     try:
#         with open(CONFIG_FILE, "w") as f:
#             f.write(str(value))
#     except Exception as e:
#         uart_print("Error saving interval: {}".format(e))

# def load_interval(default=2):
#     try:
#         with open(CONFIG_FILE, "r") as f:
#             return int(f.read().strip())
#     except:
#         return default

# # -----------------------------
# # Global Variables
# # -----------------------------
# interval = load_interval(default=2)
# uart_buffer = ""
# bme = None
# veml = None

# # -----------------------------
# # I2C Initialization
# # -----------------------------
# i2c = I2C(I2C.I2C0, I2C.FAST_MODE)

# # -----------------------------
# # System Initialization
# # -----------------------------
# def initialize_system():
#     global interval, uart_buffer, bme, veml

#     uart_buffer = ""
#     interval = load_interval(default=2)

#     # Initialize sensors
#     bme = BME680(i2c)
#     veml = VEML7700(i2c)

#     # Reset + configure BME680
#     bme.soft_reset()
#     time.sleep_ms(50)
#     bme.set_humidity_oversample(2)
#     bme.set_pressure_oversample(3)
#     bme.set_temperature_oversample(4)
#     bme.set_filter(2)

#     uart_print("System Restarted. Current interval: {} seconds.".format(interval))
#     uart_print("Use 'Interval Configuration : <seconds>' to change interval.")

# initialize_system()

# # -----------------------------
# # Main Loop
# # -----------------------------
# while True:
#     try:
#         # -------------------------------------
#         # UART Command Handling
#         # -------------------------------------
#         if uart.any():
#             incoming = uart.read().decode('utf-8')
#             uart_buffer += incoming

#             if '\n' in uart_buffer:
#                 lines = uart_buffer.split('\n')

#                 # The last element might be an incomplete line, so we process all but the last
#                 # and keep the last one in the buffer.
#                 complete_lines = lines[:-1]
#                 uart_buffer = lines[-1]

#                 for line in complete_lines:
#                     line = line.strip()
#                     if not line:  # Skip empty lines
#                         continue

#                     # Restart Device command
#                     if line == "Restart Device":
#                         initialize_system()

#                     # Interval change command
#                     elif line.lower().startswith("interval configuration :"):
#                         try:
#                             parts = line.split(":")
#                             if len(parts) > 1:
#                                 new_interval = int(parts[1].strip())
#                                 if new_interval > 0:
#                                     interval = new_interval
#                                     save_interval(interval)
#                                     uart_print("Interval updated to {} seconds.".format(interval))
#                                 else:
#                                     uart_print("Invalid interval: must be > 0.")
#                             else:
#                                 uart_print("Command format invalid.")
#                         except:
#                             uart_print("Invalid number. Use: Interval Configuration : <number>")

#         # -------------------------------------
#         # Read Sensor Data
#         # -------------------------------------
#         data_ready = bme.get_sensor_data()
#         if data_ready:
#             temperature = bme.data.temperature
#             humidity = bme.data.humidity
#             pressure = bme.data.pressure
#             bme_ok = True
#         else:
#             temperature = humidity = pressure = None
#             bme_ok = False

#         try:
#             lux = veml.lux()
#             veml_ok = True
#         except Exception as e:
#             lux = None
#             veml_ok = False
#             print("VEML7700 read error:", e) # Print to REPL for debugging

#         # -------------------------------------
#         # Send UI Data (Option A Format)
#         # -------------------------------------
#         if bme_ok and veml_ok:
#             packet = "T:{:.2f},H:{:.2f},P:{:.2f},L:{:.2f}".format(
#                 temperature, humidity, pressure, lux
#             )
#             uart_print(packet)
#         else:
#             # Provide more specific error messages
#             error_msg = "ERROR: " + ("BME680 failed. " if not bme_ok else "") + ("VEML7700 failed." if not veml_ok else "")
#             uart_print(error_msg.strip())

#     except Exception as e:
#         uart_print("Error: {}".format(e))
#         print("Sensor error:", e)

#     time.sleep(interval)






# from machine import I2C, UART
# import utime as time
# import _thread
# from usr.bmedriver import BME680
# from usr.veml_7700_driver import VEML7700

# # -------------------------------------
# # UART Initialization
# # -------------------------------------
# uart = UART(UART.UART2, 115200, 8, 0, 1, 0)

# def uart_print(msg):
#     try:
#         uart.write((msg + "\r\n").encode())
#     except Exception as e:
#         print("UART write error:", e)

# # -------------------------------------
# # Global Variables
# # -------------------------------------
# uart_buffer = ""
# interval = 1
# bme = None
# veml = None

# # -------------------------------------
# # Config File for Interval
# # -------------------------------------
# CONFIG_FILE = "/usr/config.txt"

# def save_interval(value):
#     try:
#         with open(CONFIG_FILE, "w") as f:
#             f.write(str(value))
#     except Exception as e:
#         uart_print("Error saving interval: {}".format(e))

# def load_interval(default=1):
#     try:
#         val = open(CONFIG_FILE, "r").read().strip()
#         return int(val) if val else default
#     except:
#         return default

# # -------------------------------------
# # I2C Initialization
# # -------------------------------------
# i2c = I2C(I2C.I2C0, I2C.FAST_MODE)

# # -------------------------------------
# # System Initialization
# # -------------------------------------
# def initialize_system():
#     global interval, uart_buffer, bme, veml

#     uart_buffer = ""
#     interval = load_interval()

#     # Initialize sensors
#     uart_print("Initializing sensors...")
#     bme = BME680(i2c)
#     veml = VEML7700(i2c)

#     # Configure BME680
#     bme.soft_reset()
#     time.sleep_ms(50)
#     bme.set_humidity_oversample(2)
#     bme.set_pressure_oversample(3)
#     bme.set_temperature_oversample(4)
#     bme.set_filter(2)

#     uart_print("System Restarted. Current interval: {} seconds.".format(interval))
#     uart_print("Commands:")
#     uart_print("  • Restart Device")
#     uart_print("  • Interval Configuration : <seconds>")

# initialize_system()

# # -------------------------------------
# # UART Command Thread
# # -------------------------------------
# def uart_loop():
#     global uart_buffer, interval

#     while True:
#         try:
#             if uart.any():
#                 incoming = uart.read().decode('utf-8')
#                 uart_buffer += incoming

#                 if '\n' in uart_buffer:
#                     lines = uart_buffer.split('\n')
#                     complete = lines[:-1]
#                     uart_buffer = lines[-1]

#                     for line in complete:
#                         line = line.strip()
#                         if not line:
#                             continue

#                         # Restart system
#                         if line == "Restart Device":
#                             initialize_system()

#                         # Set interval
#                         elif line.lower().startswith("interval configuration :"):
#                             try:
#                                 parts = line.split(":")
#                                 new_interval = int(parts[1].strip())

#                                 if new_interval > 0:
#                                     interval = new_interval
#                                     save_interval(interval)
#                                     uart_print("Interval updated to {} seconds.".format(interval))
#                                 else:
#                                     uart_print("Invalid interval (must be > 0)")
#                             except:
#                                 uart_print("Invalid format. Use: Interval Configuration : <number>")

#         except Exception as e:
#             uart_print("UART Loop Error: {}".format(e))

#         time.sleep(0.1)

# # -------------------------------------
# # Sensor Loop Thread
# # -------------------------------------
# def sensor_loop():
#     global interval, bme, veml

#     while True:
#         try:
#             # ------------- BME680 Read -------------
#             data_ready = bme.get_sensor_data()
#             if data_ready:
#                 temperature = bme.data.temperature
#                 humidity = bme.data.humidity
#                 pressure = bme.data.pressure
#                 bme_ok = True
#             else:
#                 temperature = humidity = pressure = None
#                 bme_ok = False

#             # ------------- VEML7700 Read -------------
#             try:
#                 lux = veml.lux()
#                 veml_ok = True
#             except Exception as e:
#                 lux = None
#                 veml_ok = False
#                 print("VEML7700 error:", e)

#             # ------------- Send UI Packet -------------
#             if bme_ok and veml_ok:
#                 packet = "T:{:.2f},H:{:.2f},P:{:.2f},L:{:.2f}".format(
#                     temperature, humidity, pressure, lux
#                 )
#                 uart_print(packet)

#             else:
#                 msg = "ERROR: "
#                 if not bme_ok:
#                     msg += "BME680 failed. "
#                 if not veml_ok:
#                     msg += "VEML7700 failed."
#                 uart_print(msg.strip())

#         except Exception as e:
#             uart_print("Sensor Error: {}".format(e))

#         time.sleep(interval)

# # -------------------------------------
# # Start Threads
# # -------------------------------------
# _thread.start_new_thread(uart_loop, ())
# _thread.start_new_thread(sensor_loop, ())

# # Keep main thread alive
# while True:
#     time.sleep(1)










from machine import I2C, UART
import utime as time
import _thread
from usr.bmedriver import BME680
from usr.veml_7700_driver import VEML7700

# -------------------------------------
# UART Initialization
# -------------------------------------
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)

def uart_print(msg):
    try:
        uart.write((msg + "\r\n").encode())
    except Exception as e:
        print("UART write error:", e)

# -------------------------------------
# Global Variables
# -------------------------------------
uart_buffer = ""
interval = 1               # DEFAULT INTERVAL
bme = None
veml = None

# -------------------------------------
# Config File for Interval
# -------------------------------------
CONFIG_FILE = "/usr/config.txt"

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

# -------------------------------------
# I2C Initialization
# -------------------------------------
i2c = I2C(I2C.I2C0, I2C.FAST_MODE)

# -------------------------------------
# System Initialization
# -------------------------------------
def initialize_system():
    global interval, uart_buffer, bme, veml

    uart_buffer = ""

    # RESET INTERVAL TO DEFAULT (as you requested)
    interval = 1
    save_interval(interval)

    # Initialize sensors
    uart_print("Initializing sensors...")
    bme = BME680(i2c)
    veml = VEML7700(i2c)

    # Configure BME680
    bme.soft_reset()
    time.sleep_ms(50)
    bme.set_humidity_oversample(2)
    bme.set_pressure_oversample(3)
    bme.set_temperature_oversample(4)
    bme.set_filter(2)

    uart_print("System Restarted. Current interval: {} seconds.".format(interval))
    

# Load interval before initialization
interval = load_interval()
initialize_system()

# -------------------------------------
# UART Command Thread
# -------------------------------------
def uart_loop():
    global uart_buffer, interval

    while True:
        try:
            if uart.any():
                incoming = uart.read().decode('utf-8')
                uart_buffer += incoming

                if '\n' in uart_buffer:
                    lines = uart_buffer.split('\n')
                    complete = lines[:-1]
                    uart_buffer = lines[-1]

                    for line in complete:
                        line = line.strip()
                        if not line:
                            continue

                        # Restart system
                        if line == "Restart Device":
                            initialize_system()
                            continue

                        # Interval configuration
                        elif line.lower().startswith("interval configuration :"):
                            try:
                                parts = line.split(":")
                                new_interval = int(parts[1].strip())

                                if new_interval > 0:
                                    interval = new_interval
                                    save_interval(interval)
                                    uart_print("Interval updated to {} seconds.".format(interval))
                                else:
                                    uart_print("Invalid interval (must be > 0)")
                            except:
                                uart_print("Invalid format. Use: Interval Configuration : <number>")

        except Exception as e:
            uart_print("UART Loop Error: {}".format(e))

        time.sleep(0.1)

# -------------------------------------
# Sensor Loop Thread
# -------------------------------------
def sensor_loop():
    global interval, bme, veml

    while True:
        try:
            data_ready = bme.get_sensor_data()
            if data_ready:
                temperature = bme.data.temperature
                humidity = bme.data.humidity
                pressure = bme.data.pressure
                bme_ok = True
            else:
                temperature = humidity = pressure = None
                bme_ok = False

            try:
                lux = veml.lux()
                veml_ok = True
            except Exception as e:
                lux = None
                veml_ok = False

            if bme_ok and veml_ok:
                packet = "T:{:.2f},H:{:.2f},P:{:.2f},L:{:.2f}".format(
                    temperature, humidity, pressure, lux
                )
                uart_print(packet)
            else:
                msg = "ERROR: "
                if not bme_ok:
                    msg += "BME680 failed. "
                if not veml_ok:
                    msg += "VEML7700 failed."
                uart_print(msg.strip())

        except Exception as e:
            uart_print("Sensor Error: {}".format(e))

        time.sleep(interval)

# -------------------------------------
# Start Threads
# -------------------------------------
_thread.start_new_thread(uart_loop, ())
_thread.start_new_thread(sensor_loop, ())

# Keep main thread alive
while True:
    time.sleep(1)

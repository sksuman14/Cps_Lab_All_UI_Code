from machine import I2C, UART
from usr.stts751 import STTS751
import utime
import osTimer
from misc import Power

# ────────────────────────────────────────────────
# Device state (same pattern as SHT40)

class DeviceState:
    def __init__(self):
        self.CurrentTemp = 0.0
        self.SensorInterval = 5000  # ms

device_state = DeviceState()

# ────────────────────────────────────────────────
# UART1 for output

uart1 = UART(UART.UART1, 115200, 8, 0, 1, 0)

def uart_print(msg):
    """Send message to UART1 with newline"""
    try:
        uart1.write((msg + "\r\n").encode())
    except:
        pass

# ────────────────────────────────────────────────
# Sensor read function

def get_temp_stts751():
    try:
        temp = stts.get_temperature()
        device_state.CurrentTemp = temp
        uart_print("STTS751: Temperature {} C".format(temp))
        return temp
    except Exception as e:
        uart_print("STTS751 read error: {}".format(e))
        return None

# ────────────────────────────────────────────────
# Timer callback (same role as data_check in SHT40)

def data_check(args):
    get_temp_stts751()

# ────────────────────────────────────────────────
# Init I2C + Sensor

i2c_dev = I2C(0, fastmode=True)
stts = STTS751(i2c_dev, address=0x48)

uart_print("STTS751 initialized")

# ────────────────────────────────────────────────
# Start timer

Sensor_timer = osTimer()
Sensor_timer.start(device_state.SensorInterval, 1, data_check)

# ────────────────────────────────────────────────
# Main loop – UART command handling

while True:
    if uart1.any() > 0:
        incoming = uart1.read(uart1.any())
        if incoming:
            try:
                text = incoming.decode('utf-8').strip()
                uart_print("RX: {}".format(text))

                if text.startswith("SET_INTERVAL:"):
                    Interval = int(text.split(":", 1)[1])
                    device_state.SensorInterval = Interval * 1000
                    uart_print("Interval set to {}s".format(Interval))

                    if Sensor_timer:
                        Sensor_timer.stop()

                    Sensor_timer = osTimer()
                    Sensor_timer.start(
                        device_state.SensorInterval,
                        1,
                        data_check
                    )

                elif text == "restartDevice":
                    uart_print("Restarting device...")
                    Power.powerRestart()

                else:
                    uart_print("Unknown command: {}".format(text))

            except Exception as e:
                uart_print("Error processing command: {}".format(e))

    utime.sleep(0.1)

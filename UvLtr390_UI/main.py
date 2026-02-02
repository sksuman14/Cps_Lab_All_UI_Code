from machine import I2C, UART
import utime
import osTimer
from misc import Power
from usr.ltr390_drv import LTR390

# ─────────────────────────────────────────────
# Device State

class DeviceState:
    def __init__(self):
        self.UV = 0
        self.SensorInterval = 1000  # ms

device_state = DeviceState()

# ─────────────────────────────────────────────
# UART

uart1 = UART(UART.UART1, 115200, 8, 0, 1, 0)

def uart_print(msg):
    try:
        uart1.write((msg + "\r\n").encode())
    except:
        pass

# ─────────────────────────────────────────────
# I2C + Sensor init

i2c = I2C(I2C.I2C0, I2C.FAST_MODE)
sensor = LTR390(i2c)

uart_print("LTR390 initialized")

# ─────────────────────────────────────────────
# Timer callback

def data_check(args):
    uv = sensor.read_uv_raw()
    if uv is not None:
        device_state.UV = uv
        uart_print("UV {}".format(uv))
    else:
        uart_print("uv not_ready")

# ─────────────────────────────────────────────
# Start timer

Sensor_timer = osTimer()
Sensor_timer.start(device_state.SensorInterval, 1, data_check)

# ─────────────────────────────────────────────
# UART command loop

while True:
    if uart1.any():
        incoming = uart1.read(uart1.any())
        if incoming:
            try:
                cmd = incoming.decode().strip()
                uart_print("RX: {}".format(cmd))

                if cmd.startswith("SET_INTERVAL:"):
                    sec = int(cmd.split(":", 1)[1])
                    device_state.SensorInterval = sec * 1000

                    Sensor_timer.stop()
                    Sensor_timer = osTimer()
                    Sensor_timer.start(device_state.SensorInterval,1,data_check)
                    uart_print("Interval set to {} seconds".format(sec))

                elif cmd == "restartDevice":
                    uart_print("Restarting device...")
                    Power.powerRestart()
                else:
                    uart_print("Unknown command")

            except Exception as e:
                uart_print("CMD error: {}".format(e))

    utime.sleep(0.1)

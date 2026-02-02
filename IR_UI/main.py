from misc import ADC
from machine import UART
import utime
import osTimer
from misc import Power

# ─────────────────────────────────────────────
# Device State

class DeviceState:
    def __init__(self):
        self.IR = 0                  # 0 = object detected, 1 = no object
        self.SensorInterval = 1000   # ms

device_state = DeviceState()

# ─────────────────────────────────────────────
# UART setup

uart = UART(UART.UART2, 115200, 8, 0, 1, 0)

def uart_print(msg):
    try:
        uart.write((msg + "\r\n").encode())
    except:
        pass

THRESHOLD = 1500  # Tune experimentally

adc = ADC()
adc.open()

def read_ir():
    val = adc.read(ADC.ADC0)
    return 0 if val < THRESHOLD else 1

def data_check(args):
    device_state.IR = read_ir()
    # Parser-friendly output
    uart_print("IR {}".format(device_state.IR))
Sensor_timer = osTimer()
Sensor_timer.start(device_state.SensorInterval, 1, data_check)

uart_print("IR ADC sensor initialized")

while True:
    if uart.any():
        incoming = uart.read(uart.any())
        if incoming:
            try:
                cmd = incoming.decode().strip()
                uart_print("RX: {}".format(cmd))

                if cmd.startswith("SET_INTERVAL:"):
                    sec = int(cmd.split(":", 1)[1])
                    device_state.SensorInterval = sec * 1000

                    Sensor_timer.stop()
                    Sensor_timer = osTimer()
                    Sensor_timer.start(
                        device_state.SensorInterval,
                        1,
                        data_check
                    )

                    uart_print("Interval set to {} seconds".format(sec))

                elif cmd == "restartDevice":
                    uart_print("Restarting device...")
                    Power.powerRestart()

                else:
                    uart_print("Unknown command")

            except Exception as e:
                uart_print("CMD error: {}".format(e))

    utime.sleep(0.1)

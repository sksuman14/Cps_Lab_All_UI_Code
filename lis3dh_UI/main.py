from machine import I2C, UART
import utime as time

#  UART Initialization 
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)

def uart_print(msg):
    try:
        uart.write((msg + "\r\n").encode())
    except Exception as e:
        print("UART write error:", e)

# File for saving interval
CONFIG_FILE = "/usr/config.txt"

def save_interval(value):
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(str(value))
    except Exception as e:
        uart_print("Error saving interval: {}".format(e))

def load_interval(default=2):
    try:
        with open(CONFIG_FILE, "r") as f:
            val = f.read().strip()
            if val:
                return int(val)
            else:
                return default
    except Exception:
        return default

#  LIS3DH Driver 
class LIS3DH:
    WHO_AM_I_REG = 0x0F
    WHO_AM_I_VAL = 0x33
    ADDR_LIST = [0x18, 0x19]

    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = None
        self.detect()
        self.init_sensor()

    def write_reg(self, reg, value):
        buf = bytearray([reg, value])
        self.i2c.write(self.addr, b'', 0, buf, 2)

    def read_reg(self, reg):
        reg_buf = bytearray([reg])
        self.i2c.write(self.addr, b'', 0, reg_buf, 1)
        val_buf = bytearray(1)
        self.i2c.read(self.addr, b'', 0, val_buf, 1, 0)
        return val_buf[0]

    def detect(self):
        for addr in self.ADDR_LIST:
            self.addr = addr
            try:
                val = self.read_reg(self.WHO_AM_I_REG)
                if val == self.WHO_AM_I_VAL:
                    uart_print("LIS3DH detected at 0x{:02X}".format(addr))
                    return
            except Exception:
                continue
        raise Exception("LIS3DH not found on I2C bus")

    def init_sensor(self):
        self.write_reg(0x20, 0x57)  # CTRL_REG1
        self.write_reg(0x23, 0x08)  # CTRL_REG4 HR mode
        uart_print("LIS3DH initialized.")

    def read_axes(self):
        def twos_complement(val, bits):
            if val & (1 << (bits - 1)):
                val -= 1 << bits
            return val

        data = []
        scale = 0.001  # g per LSB
        try:
            for reg in [0x28, 0x2A, 0x2C]:
                l = self.read_reg(reg)
                h = self.read_reg(reg + 1)
                raw = (l | (h << 8))
                raw = twos_complement(raw, 16)
                raw = raw >> 4
                data.append(raw * scale * 9.80665)  # convert to m/s² but no unit printed
        except Exception as e:
            uart_print("Error reading axes: {}".format(e))
            data = [0, 0, 9.80665]  # fallback
        return tuple(data)

#  Initialize I2C 
i2c = I2C(I2C.I2C0, I2C.FAST_MODE)

#  Global Variables 
interval = load_interval(default=2)
uart_buffer = ""
sensor = None

def initialize_system():
    global sensor, uart_buffer, interval
    uart_buffer = ""
    interval = 1
    save_interval(interval)
    try:
        sensor = LIS3DH(i2c)
    except Exception as e:
        uart_print("Sensor init error: {}".format(e))
        sensor = None
    uart_print("System Restarted. Interval: {} sec".format(interval))
    

initialize_system()

#  Main Loop 
while True:
    try:
        # UART Command Handling
        if uart.any():
            incoming = uart.read().decode('utf-8')
            uart_buffer += incoming
            if '\n' in uart_buffer:
                lines = uart_buffer.split('\n')
                for line in lines[:-1]:
                    line = line.strip()
                    if line == "Restart Device":
                        initialize_system()
                    elif line.startswith("Interval Configuration :"):
                        try:
                            parts = line.split(":")
                            if len(parts) > 1:
                                new_interval = int(parts[1].strip())
                                if new_interval > 0:
                                    interval = new_interval
                                    save_interval(interval)
                                    uart_print("Interval updated: {} sec".format(interval))
                                else:
                                    uart_print("Invalid interval (>0)")
                            else:
                                uart_print("Command format invalid")
                        except ValueError:
                            uart_print("Invalid number")
                uart_buffer = lines[-1]

        # Sensor Reading
        if sensor:
            x, y, z = sensor.read_axes()
        else:
            x = y = 0
            z = 9.80665

        uart_print("LIS3DH: X={:.3f}, Y={:.3f}, Z={:.3f}".format(x, y, z))

    except Exception as e:
        uart_print("Error: {}".format(e))

    time.sleep(interval)

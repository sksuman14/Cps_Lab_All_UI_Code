# ltr390_drv.py
import utime
from machine import I2C

# I2C address
LTR390_I2C_ADDR = 0x53

# Registers
MAIN_CTRL   = 0x00
MEAS_RATE   = 0x04
GAIN        = 0x05
MAIN_STATUS = 0x07
UVS_DATA_0  = 0x10

# Config values
UVS_MODE = 0x0A
RESOLUTION_18BIT_TIME100MS = 0x20
GAIN_3X = 0x01


class LTR390:
    def __init__(self, i2c):
        self.i2c = i2c
        self._init_sensor()
        self._wait_for_ready()

    # ─────────────────────────────────────────────
    # Low-level I2C helpers (QuecPython safe)

    def _write_reg(self, reg, val):
        buf = bytearray([reg, val])
        self.i2c.write(LTR390_I2C_ADDR, b'', 0, buf, 2)

    def _read_reg(self, reg):
        reg_buf = bytearray([reg])
        self.i2c.write(LTR390_I2C_ADDR, b'', 0, reg_buf, 1)
        val_buf = bytearray(1)
        self.i2c.read(LTR390_I2C_ADDR, b'', 0, val_buf, 1, 0)
        return val_buf[0]

    def _burst_read(self, start_reg, length):
        buf = bytearray(length)
        self.i2c.write(
            LTR390_I2C_ADDR,
            b'', 0,
            bytearray([start_reg]), 1
        )
        utime.sleep_ms(1)
        self.i2c.read(
            LTR390_I2C_ADDR,
            b'', 0,
            buf, length, 0
        )
        return buf

    # ─────────────────────────────────────────────
    # Sensor setup

    def _init_sensor(self):
        self._write_reg(MAIN_CTRL, UVS_MODE)
        self._write_reg(MEAS_RATE, RESOLUTION_18BIT_TIME100MS)
        self._write_reg(GAIN, GAIN_3X)
        utime.sleep_ms(100)

    def _wait_for_ready(self):
        timeout = 20
        while timeout > 0:
            if self._read_reg(MAIN_STATUS) & 0x08:
                return
            utime.sleep_ms(100)
            timeout -= 1

    # ─────────────────────────────────────────────
    # Public API

    def read_uv_raw(self):
        status = self._read_reg(MAIN_STATUS)
        if not (status & 0x08):
            return None

        data = self._burst_read(UVS_DATA_0, 3)
        return (data[2] << 16) | (data[1] << 8) | data[0]

import utime as time
from machine import I2C

# STTS751 Registers
WHO_AM_I = 0x01
TEMP_HIGH = 0x00
TEMP_LOW = 0x02
CONFIG = 0x03
ONESHOT = 0x0F
SOFT_RESET = 0x2F

class STTS751:
    def __init__(self, i2c_bus, address=0x48):
        if i2c_bus is None:
            raise ValueError("I2C interface must be passed explicitly in QuecPython")

        self._i2c = i2c_bus
        self._address = address

        # Reset device
        self.reset()
        time.sleep(0.1)

    def _write_register(self, reg, value):
        buf = bytearray([reg, value])
        # QuecPython I2C write: write(addr, memaddr, memlen, databuf, datalen)
        return self._i2c.write(self._address, b'', 0, buf, len(buf))

    def _read_register(self, reg, length=1):
        buf = bytearray(length)
        regbuf = bytearray([reg])
        # First send register address
        self._i2c.write(self._address, b'', 0, regbuf, 1)
        # Then read bytes (note: dalay arg required)
        self._i2c.read(self._address, b'', 0, buf, length, 0)
        return buf

    def reset(self):
        self._write_register(SOFT_RESET, 0x00)
        time.sleep(0.05)

    def get_temperature(self):
        """Read temperature in °C"""
        high = self._read_register(TEMP_HIGH, 1)[0]   # MSB
        low = self._read_register(TEMP_LOW, 1)[0]     # LSB (fraction)

        # Combine integer + fractional (LSB upper nibble = fraction * 0.0625°C)
        temp = high + (low >> 4) * 0.0625
        return round(temp, 2)

    def oneshot_measurement(self):
        """Trigger one-shot measurement"""
        self._write_register(ONESHOT, 0x00)
        time.sleep(0.1)
        return self.get_temperature()

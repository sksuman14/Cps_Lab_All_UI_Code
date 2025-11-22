import utime as time
from machine import I2C

# Commands
_RESET = 0x30A2
_MEASURE_HIGHREP = 0x2400
_MEASURE_MEDREP = 0x240B
_MEASURE_LOWREP = 0x2416

# Precision modes
HIGH_PRECISION = 0
MEDIUM_PRECISION = 1
LOW_PRECISION = 2

precision_commands = {
    HIGH_PRECISION: _MEASURE_HIGHREP,
    MEDIUM_PRECISION: _MEASURE_MEDREP,
    LOW_PRECISION: _MEASURE_LOWREP,
}

class STS30:
    def __init__(self, i2c_bus, address=0x4A):
        if i2c_bus is None:
            raise ValueError("I2C interface must be passed explicitly in QuecPython")

        self._i2c = i2c_bus
        self._address = address
        self._precision = HIGH_PRECISION
        self.reset()
        time.sleep(0.1)

    def _write_cmd(self, cmd):
        buf = bytearray([cmd >> 8, cmd & 0xFF])
        return self._i2c.write(self._address, b'', 0, buf, len(buf))

    def _read_bytes(self, length, delay=0):
        buf = bytearray(length)
        self._i2c.read(self._address, b'', 0, buf, length, delay)
        return buf

    def _crc(self, data):
        crc = 0xFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x31
                else:
                    crc <<= 1
        return crc & 0xFF

    def reset(self):
        self._write_cmd(_RESET)
        time.sleep(0.01)

    def set_precision(self, mode):
        if mode not in precision_commands:
            raise ValueError("Invalid precision mode")
        self._precision = mode

    def get_temperature(self):
        # Send measure command
        self._write_cmd(precision_commands[self._precision])
        time.sleep(0.02)

        # Read 6 bytes (temp + CRC + dummy humidity + CRC)
        raw = self._read_bytes(2)

        # Temperature part
        tval = (raw[0] << 8) | raw[1]
        

        # Convert raw value to °C
        temp = -45 + (175 * tval / 65535.0)
        return round(temp, 2)

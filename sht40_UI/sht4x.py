
import utime as time
from machine import I2C

# Constants
_RESET = 0x94

HIGH_PRECISION = 0
MEDIUM_PRECISION = 1
LOW_PRECISION = 2

temperature_precision_values = {
    HIGH_PRECISION: 0xFD,
    MEDIUM_PRECISION: 0xF6,
    LOW_PRECISION: 0xE0,
}

HEATER200mW = 0
HEATER110mW = 1
HEATER20mW = 2

TEMP_1 = 0
TEMP_0_1 = 1

wat_config = {
    HEATER200mW: (0x39, 0x32),
    HEATER110mW: (0x2F, 0x24),
    HEATER20mW: (0x1E, 0x15),
}


class SHT4X:
    def __init__(self, i2c_bus, address=0x44):
        if i2c_bus is None:
                raise ValueError("I2C interface must be passed explicitly in QuecPython")

        self._i2c = i2c_bus
        self._address = address
        self._data = bytearray(6)

        print("[DEBUG] I2C object set.")
        print("[DEBUG] I2C address set to: 0x%02X" % self._address)

        # Set defaults
        self._command = 0xFD
        self._temperature_precision = HIGH_PRECISION
        self._heater_power = HEATER20mW
        self._heat_time = TEMP_0_1

        # Try communicating with the sensor (soft reset as a test)
        try:
                print("[DEBUG] Attempting soft reset of SHT40...")
                self._write(_RESET)
                time.sleep(0.1)
                print("[DEBUG] Soft reset sent successfully.")

        except Exception as e:
                print("[ERROR] Failed to communicate with SHT40 sensor.")
                raise RuntimeError("Unable to communicate with SHT40")  # Don't raise original error to keep log clean


    def _write(self, command):
        data = bytearray([command])
        result = self._i2c.write(self._address, b'', 0, data, 1)
        print("[DEBUG] Sent command:", hex(command), "| Write result:", result)
        if result != 0:
            print("[ERROR] I2C write failed. Check wiring, address, power.")
        return result


    def _read(self, length, delay=0):
        buf = bytearray(length)
        self._i2c.read(self._address, b'', 0, buf, length, delay)
        print("[DEBUG] Read", length, "bytes:", list(buf))
        return buf

    def _crc(self, buffer):
        crc = 0xFF
        for byte in buffer:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x31
                else:
                    crc = crc << 1
        result = crc & 0xFF
        print("[DEBUG] CRC calculated:", result)
        return result

    def get_temperature(self):
        return self.get_measurements()[0]

    def get_humidity(self):
        return self.get_measurements()[1]

    def get_measurements(self):
        print("[DEBUG] Sending measurement command:", hex(self._command))
        self._write(self._command)

        if self._command in (0x39, 0x2F, 0x1E):
            print("[DEBUG] Waiting 1.2s (heater power)")
            time.sleep(1.2)
        elif self._command in (0x32, 0x24, 0x15):
            print("[DEBUG] Waiting 0.2s (heater power low)")
            time.sleep(0.2)

        time.sleep(0.2)

        self._data = self._read(6)

        temperature_raw = (self._data[0] << 8) | self._data[1]
        temp_crc = self._data[2]
        humidity_raw = (self._data[3] << 8) | self._data[4]
        humidity_crc = self._data[5]


        print("[DEBUG] Raw Temp:", temperature_raw, "| Temp CRC:", temp_crc)
        print("[DEBUG] Raw Hum:", humidity_raw, "| Hum CRC:", humidity_crc)

        if temp_crc != self._crc(self._data[0:2]) or humidity_crc != self._crc(self._data[3:5]):
            print("[ERROR] CRC check failed")
            raise Exception("CRC check failed")

        temperature = -45.0 + 175.0 * temperature_raw / 65535.0
        humidity = -6.0 + 125.0 * humidity_raw / 65535.0
        humidity = max(min(humidity, 100), 0)


        print("[DEBUG] Converted Temp:", temperature, "C")
        print("[DEBUG] Converted Hum:", humidity, "%RH")

        temperature = round(temperature, 2)
        humidity = round(humidity, 2)

        return temperature, humidity

    def get_temperature_precision(self):
        values = ("HIGH_PRECISION", "MEDIUM_PRECISION", "LOW_PRECISION")
        return values[self._temperature_precision]

    def set_temperature_precision(self, value):
        if value not in temperature_precision_values:
            raise ValueError("Invalid temperature precision")
        self._temperature_precision = value
        self._command = temperature_precision_values[value]
        print("[DEBUG] Set temp precision:", self.get_temperature_precision(), "| Command:", hex(self._command))

    def get_heater_power(self):
        values = ("HEATER200mW", "HEATER110mW", "HEATER20mW")
        return values[self._heater_power]

    def set_heater_power(self, value):
        if value not in (0, 1, 2):
            raise ValueError("Invalid heater power")
        self._heater_power = value
        self._command = wat_config[value][self._heat_time]
        print("[DEBUG] Set heater power:", self.get_heater_power(), "| Command:", hex(self._command))

    def get_heat_time(self):
        values = ("TEMP_1", "TEMP_0_1")
        return values[self._heat_time]

    def set_heat_time(self, value):
        if value not in (0, 1):
            raise ValueError("Invalid heat time")
        self._heat_time = value
        self._command = wat_config[self._heater_power][value]
        print("[DEBUG] Set heat time:", self.get_heat_time(), "| Command:", hex(self._command))

    def reset(self):
        print("[DEBUG] Sending reset command")
        self._write(_RESET)
        time.sleep(0.1)
        print("[DEBUG] Sensor reset complete")

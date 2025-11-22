from machine import I2C
import utime
import usr.veml7700_registers as reg

class VEML7700:
    def __init__(self, i2c_bus, address=0x10):
        self.i2c = i2c_bus
        self.addr = address
        self._gain = reg.GAIN_1_8
        self._integration_time = reg.IT_25MS

        self._write_u16(reg.ALS_CONF, 0x0003)
        self.set_gain(self._gain)
        self.set_integration_time(self._integration_time)
        self.enable()
        self._read_u16(reg.ID)

    def _read_u16(self, register):
        r_data = bytearray(2)
        try:
            self.i2c.read(self.addr, bytearray([register]), 1, r_data, 2, 0)
            return r_data[0] | (r_data[1] << 8)
        except:
            return 0

    def _write_u16(self, register, value):
        try:
            data = bytearray([value & 0xFF, (value >> 8) & 0xFF])
            self.i2c.write(self.addr, bytearray([register]), 1, data, len(data))
        except:
            pass

    def enable(self):
        config_before = self._read_u16(reg.ALS_CONF)
        config_enabled = config_before & 0xFFFE
        self._write_u16(reg.ALS_CONF, config_enabled)
        utime.sleep_ms(150)

    def disable(self):
        config = self._read_u16(reg.ALS_CONF)
        config |= (1 << 0)
        self._write_u16(reg.ALS_CONF, config)

    def set_gain(self, gain):
        config = self._read_u16(reg.ALS_CONF)
        config &= ~(0x3 << 11)
        config |= (gain << 11)
        self._write_u16(reg.ALS_CONF, config)
        self._gain = gain

    def set_integration_time(self, it):
        config = self._read_u16(reg.ALS_CONF)
        config &= ~(0xF << 6)
        config |= (it << 6)
        self._write_u16(reg.ALS_CONF, config)
        self._integration_time = it

    def get_als(self):
        return self._read_u16(reg.ALS)

    def get_white(self):
        return self._read_u16(reg.WHITE)

    def integration_time_values(self):
        return {
            reg.IT_25MS: 25,
            reg.IT_50MS: 50,
            reg.IT_100MS: 100,
            reg.IT_200MS: 200,
            reg.IT_400MS: 400,
            reg.IT_800MS: 800
        }

    def lux(self):
        utime.sleep_ms(self.integration_time_values()[self._integration_time])
        als_raw = self.get_als()

        gain_factor = {
            reg.GAIN_2: 2,
            reg.GAIN_1: 1,
            reg.GAIN_1_4: 0.25,
            reg.GAIN_1_8: 0.125,
        }[self._gain]

        integration_time_ms = self.integration_time_values()[self._integration_time]
        lux = (als_raw / gain_factor) * (10 / integration_time_ms)

        return lux

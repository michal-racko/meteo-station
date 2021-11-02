import time

from ctypes import c_short

from .sensor_base import SensorBase


class BMP180(SensorBase):
    """
    Represents a BMP180 temperature / pressure sensor
    """

    # Registers
    __CALIBRATION_REGISTER = 0xAA
    __CONTROL_REGISTER = 0xF4

    __TEMPERATURE_DATA_REGISTER = 0xF6
    __PRESSURE_DATA_REGISTER = 0xF6

    # Commands
    __READ_TEMPERATURE_COMMAND = 0x2E
    __READ_PRESSURE_COMMAND = 0x34

    def __init__(self,
                 address=0x77):
        super(BMP180, self).__init__(address)

        self.temperature = None
        self.pressure = None

        self._ac1 = None
        self._ac2 = None
        self._ac3 = None
        self._ac4 = None
        self._ac5 = None
        self._ac6 = None
        self._b1 = None
        self._b2 = None
        self._b5 = None
        self._mc = None
        self._md = None

        self._oversample = 3

    def read(self):
        self._read_calibration()

        self._read_temperature()
        self._read_pressure()

    def _read_temperature(self):
        self._bus.write_byte_data(
            self._address,
            self.__CONTROL_REGISTER,
            self.__READ_TEMPERATURE_COMMAND
        )
        time.sleep(0.005)
        msb, lsb = self._bus.read_i2c_block_data(
            self._address,
            self.__TEMPERATURE_DATA_REGISTER,
            2
        )
        ut = (msb << 8) + lsb
        x1 = ((ut - self._ac6) * self._ac5) >> 15
        x2 = (self._mc << 11) / (x1 + self._md)
        self._b5 = x1 + x2

        self.temperature = int(self._b5 + 8) >> 4
        self.temperature /= 10
        self.temperature -= 2

    def _read_pressure(self):
        if self._b5 is None:
            raise RuntimeError('Temperature must be read first')

        self._bus.write_byte_data(
            self._address,
            self.__CONTROL_REGISTER,
            self.__READ_PRESSURE_COMMAND + (self._oversample << 6)
        )
        time.sleep(0.04)
        msb, lsb, xsb = self._bus.read_i2c_block_data(
            self._address,
            self.__PRESSURE_DATA_REGISTER,
            3
        )
        up = ((msb << 16) + (lsb << 8) + xsb) >> (8 - self._oversample)

        b6 = self._b5 - 4000
        b62 = int(b6 ** 2) >> 12
        x1 = (self._b2 * b62) >> 11
        x2 = int(self._ac2 * b6) >> 11
        x3 = x1 + x2
        b3 = (((self._ac1 * 4 + x3) << self._oversample) + 2) >> 2
        x1 = int(self._ac3 * b6) >> 13
        x2 = (self._b1 * b62) >> 13
        x3 = ((x1 + x2) + 2) >> 2
        b4 = (self._ac4 * (x3 + 32768)) >> 15
        b7 = (up - b3) * (50000 >> self._oversample)
        p = (b7 * 2) / b4
        x1 = (int(p) >> 8) * (int(p) >> 8)
        x1 = (x1 * 3038) >> 16
        x2 = int(-7357 * p) >> 16

        self.pressure = int(p + ((x1 + x2 + 3791) >> 4))

    def _read_calibration(self):
        calibration = self._bus.read_i2c_block_data(
            self._address,
            self.__CALIBRATION_REGISTER,
            22
        )

        self._ac1 = self._get_short(calibration, 0)
        self._ac2 = self._get_short(calibration, 2)
        self._ac3 = self._get_short(calibration, 4)
        self._ac4 = self._get_ushort(calibration, 6)
        self._ac5 = self._get_ushort(calibration, 8)
        self._ac6 = self._get_ushort(calibration, 10)
        self._b1 = self._get_short(calibration, 12)
        self._b2 = self._get_short(calibration, 14)
        self._mc = self._get_short(calibration, 18)
        self._md = self._get_short(calibration, 20)

    @staticmethod
    def _get_short(data, index):
        return c_short((data[index] << 8) + data[index + 1]).value

    @staticmethod
    def _get_ushort(data, index):
        return (data[index] << 8) + data[index + 1]

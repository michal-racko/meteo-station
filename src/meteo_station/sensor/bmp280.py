import time

from ctypes import c_short

from .sensor_base import SensorBase


class BMP280(SensorBase):
    """
    Represents a BMP280 temperature / pressure sensor
    """

    __CALIBRATION_REGISTER = 0x88
    __CTRL_MEAS_REGISTER = 0xF4
    __CONFIG_REGISTER = 0xF5
    __DATA_REGISTER = 0xF7

    def __init__(self,
                 address=0x76):
        super(BMP280, self).__init__(address)

        self.temperature = None
        self.pressure = None

        self._calibration_t1 = None
        self._calibration_t2 = None
        self._calibration_t3 = None

        self._calibration_p1 = None
        self._calibration_p2 = None
        self._calibration_p3 = None
        self._calibration_p4 = None
        self._calibration_p5 = None
        self._calibration_p6 = None
        self._calibration_p7 = None
        self._calibration_p8 = None
        self._calibration_p9 = None

    def read(self):
        self._bus.write_byte_data(
            self._address,
            self.__CTRL_MEAS_REGISTER,
            0xFF  # x16 oversampling for both p and T
        )
        self._bus.write_byte_data(
            self._address,
            self.__CONFIG_REGISTER,
            0xA0
        )
        time.sleep(0.005)

        data = self._bus.read_i2c_block_data(
            self._address,
            self.__DATA_REGISTER,
            8
        )

        adc_t = ((data[3] << 16) + (data[4] << 8) + (data[5] & 0xF0)) / 16
        var1 = (
                       adc_t / 16384.0 - self._calibration_t1 / 1024.0
               ) * self._calibration_t2
        var2 = (
                       (adc_t / 131072.0 - self._calibration_t1 / 8192.0) *
                       (adc_t / 131072.0 - self._calibration_t1 / 8192.0)
               ) * self._calibration_t3
        t_fine = var1 + var2

        self.temperature = t_fine / 5120

        adc_p = ((data[0] << 16) + (data[1] << 8) + (data[2] & 0xF0)) / 16

        var1 = (t_fine / 2) - 64000
        var2 = var1 * var1 * self._calibration_p6 / 32768
        var2 = var2 + var1 * self._calibration_p5 * 2
        var2 = (var2 / 4) + (self._calibration_p4 * 65536)
        var1 = (
                       self._calibration_p3 * var1 ** 2 / 524288 +
                       self._calibration_p2 * var1
               ) / 524288
        var1 = (1.0 + var1 / 32768) * self._calibration_p1
        p = 1048576 - adc_p
        p = (p - (var2 / 4096)) * 6250 / var1
        var1 = self._calibration_p9 * p ** 2 / 2147483648
        var2 = p * self._calibration_p8 / 32768

        self.pressure = (p + (var1 + var2 + self._calibration_p7) / 16) / 100

    def _read_calibration(self):
        data = self._bus.read_i2c_block_data(
            self._address,
            self.__CALIBRATION_REGISTER,
            24
        )

        self._calibration_t1 = self._get_ushort(data, 0)
        self._calibration_t2 = self._get_short(data, 2)
        self._calibration_t3 = self._get_short(data, 4)

        self._calibration_p1 = self._get_ushort(data, 6)
        self._calibration_p2 = self._get_short(data, 8)
        self._calibration_p3 = self._get_short(data, 10)
        self._calibration_p4 = self._get_short(data, 12)
        self._calibration_p5 = self._get_short(data, 14)
        self._calibration_p6 = self._get_short(data, 16)
        self._calibration_p7 = self._get_short(data, 18)
        self._calibration_p8 = self._get_short(data, 20)
        self._calibration_p9 = self._get_short(data, 22)

    @staticmethod
    def _get_short(data, index):
        return c_short((data[index + 1] << 8) + data[index]).value

    @staticmethod
    def _get_ushort(data, index):
        return (data[index + 1] << 8) + data[index]

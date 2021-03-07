from .sensor_base import SensorBase


class SI7021(SensorBase):
    """
    Represents an SI7021 sensor. Only reading relative humidity
    """
    __READ_HUMIDITY_COMMAND = 0xE5

    def __init__(self, address=0x40):
        super(SI7021, self).__init__(address)

        self.humidity = None

    def read(self):
        data = self._bus.read_i2c_block_data(
            self._address,
            self.__READ_HUMIDITY_COMMAND,
            2
        )
        self.humidity = ((data[0] * 256 + data[1]) * 125 / 65536.0) - 6

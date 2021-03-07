import smbus

from abc import ABCMeta, abstractmethod


class SensorBase:
    """
    Abstracts an electronic sensor connected to Raspberry pi's i2c bus
    """
    __metaclass__ = ABCMeta

    def __init__(self, address: int):
        self._address = address
        self._bus: smbus.SMBus = smbus.SMBus(1)

    @abstractmethod
    def read(self):
        pass

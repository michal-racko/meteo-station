import time
import numpy as np

from .sensor import BMP180, BMP280, SI7021


class MeteoStation:
    """
    Reads data in the given time interval
    and keeps track of the last N measurements.
    """

    def __init__(self,
                 time_interval=100,
                 n_measurements=300):
        self._bmp_180 = BMP180()
        self._bmp_280 = BMP280()
        self._si_7021 = SI7021()

        self._last_measurement_at = 0
        self._time_interval = time_interval

        self._n_measurements = n_measurements

        # measured parameters
        self._outside_temeprature = np.zeros(n_measurements)
        self._outside_pressure = np.zeros(n_measurements)
        self._outside_humidity = np.zeros(n_measurements)

        self._inside_temperature = np.zeros(n_measurements)

        self._first_measurement_round_done = False

        self._offset = 0
        self._running = False

    @property
    def outside_temperature(self) -> float:
        print(self._outside_temeprature[:self._offset])
        if self._first_measurement_round_done:
            return self._outside_temeprature.mean()
        else:
            return self._outside_temeprature[:self._offset].mean()

    @property
    def outside_pressure(self) -> float:
        if self._first_measurement_round_done:
            return self._outside_pressure.mean()
        else:
            return self._outside_pressure[:self._offset].mean()

    @property
    def outside_humidity(self) -> float:
        if self._first_measurement_round_done:
            return self._outside_humidity.mean()
        else:
            return self._outside_humidity[:self._offset].mean()

    @property
    def inside_temperature(self) -> float:
        if self._first_measurement_round_done:
            return self._inside_temperature.mean()
        else:
            return self._inside_temperature[:self._offset].mean()

    def _read(self):
        if self._offset >= self._n_measurements:
            self._offset = 0
            self._first_measurement_round_done = True

        self._bmp_280.read()
        self._bmp_180.read()
        self._si_7021.read()

        self._outside_temeprature[self._offset] = self._bmp_280.temperature
        self._outside_pressure[self._offset] = self._bmp_280.pressure
        self._outside_humidity[self._offset] = self._si_7021.humidity

        self._inside_temperature[self._offset] = self._bmp_180.temperature

        self._offset += 1

    def run(self):
        self._running = True

        while True:
            if time.time() - self._last_measurement_at > self._time_interval:
                self._last_measurement_at = time.time()
                self._read()

                print(
                    f'outside_temperature: {self.outside_temperature}\n'
                    f'outside_pressure: {self.outside_pressure}\n'
                    f'outside_humidity: {self.outside_humidity}\n'
                    f'inside_temperature: {self.inside_temperature}\n'
                    '===\n'
                    f'{self._outside_temeprature}\n\n\n'
                )

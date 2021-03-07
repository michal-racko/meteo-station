import time
import logging
import numpy as np

from .sensor import BMP180, BMP280, SI7021
from .metrics import (
    meteo_station_inside_temperature_value,
    meteo_station_inside_temperature_trend,
    meteo_station_outside_temperature_value,
    meteo_station_outside_temperature_trend,
    meteo_station_outside_humidity_value,
    meteo_station_outside_humidity_trend,
    meteo_station_outside_pressure_value,
    meteo_station_outside_pressure_trend
)

logger = logging.getLogger(__name__)


class MeteoStation:
    """
    Reads data in the given time interval
    and keeps track of the last N measurements.
    """

    def __init__(self,
                 measurement_interval=0.1,
                 metric_update_interval=1,
                 sliding_window=300):
        """
        :param measurement_interval:    Time interval in seconds between measurements
        :param metric_update_interval:  How often to update the metrics
        :param sliding_window:          How many measurements to average over
        """
        self._bmp_180 = BMP180()
        self._bmp_280 = BMP280()
        self._si_7021 = SI7021()

        self._last_measurement_at = 0
        self._measurement_interval = measurement_interval

        self._metrics_updated_at = 0
        self._metric_update_interval = metric_update_interval

        self._sliding_window = sliding_window

        # measured parameters
        self._outside_temepratures = np.zeros(sliding_window)
        self._outside_pressures = np.zeros(sliding_window)
        self._outside_humidities = np.zeros(sliding_window)

        self._inside_temperatures = np.zeros(sliding_window)

        self._first_measurement_round_done = False

        self._offset = 0
        self._running = False

    @property
    def outside_temperature(self) -> float:
        return self._get_timeseries(self._outside_temepratures).mean()

    @property
    def outside_temperature_trend(self) -> float:
        return self._get_trend(self._outside_temepratures)

    @property
    def outside_pressure(self) -> float:
        return self._get_timeseries(self._outside_pressures).mean()

    @property
    def outside_pressure_trend(self) -> float:
        return self._get_trend(self._outside_pressures)

    @property
    def outside_humidity(self) -> float:
        return self._get_timeseries(self._outside_humidities).mean()

    @property
    def outside_humidity_trend(self) -> float:
        return self._get_trend(self._outside_humidities)

    @property
    def inside_temperature(self) -> float:
        return self._get_timeseries(self._inside_temperatures).mean()

    @property
    def inside_temperature_trend(self) -> float:
        return self._get_trend(self._inside_temperatures)

    def _get_trend(self, values) -> float:
        """
        Returns of the time series or 0 if it is less than its spread
        """
        x = np.arange(self._sliding_window) * self._measurement_interval
        timeseries = self._get_timeseries(values)
        A = np.vstack([x, np.ones(len(x))]).T

        (_, slope), res, _, _ = np.linalg.lstsq(A, timeseries, rcond=None)
        spread = np.sqrt(res[0] / len(timeseries))

        if abs(slope) > spread:
            return slope
        else:
            return 0

    def _get_timeseries(self, values: np.ndarray) -> np.ndarray:
        """
        Prepares time series for the given value array
        """
        if self._first_measurement_round_done:
            return values[:self._offset]
        else:
            return np.concatenate((
                values[self._offset:],
                values[:self._offset]
            ))

    def _update_metrics(self):
        logger.debug('Updating metrics')

        meteo_station_outside_temperature_value.set(self.outside_temperature)
        meteo_station_outside_pressure_value.set(self.outside_pressure)
        meteo_station_outside_humidity_value.set(self.outside_humidity)
        meteo_station_inside_temperature_value.set(self.inside_temperature)

        meteo_station_outside_temperature_trend.set(
            self.outside_temperature_trend
        )
        meteo_station_outside_pressure_trend.set(self.outside_pressure_trend)
        meteo_station_outside_humidity_trend.set(self.outside_humidity_trend)
        meteo_station_inside_temperature_trend.set(
            self.inside_temperature_trend
        )

    def _read(self):
        """
        Reads data from all sensors and writes it into the local history
        """
        logger.debug('Reading data from sensors')

        if self._offset >= self._sliding_window:
            self._offset = 0
            self._first_measurement_round_done = True

        self._bmp_280.read()
        self._bmp_180.read()
        self._si_7021.read()

        self._outside_temepratures[self._offset] = self._bmp_280.temperature
        self._outside_pressures[self._offset] = self._bmp_280.pressure
        self._outside_humidities[self._offset] = self._si_7021.humidity

        self._inside_temperatures[self._offset] = self._bmp_180.temperature

        self._offset += 1

    def run(self):
        self._running = True

        while True:
            if time.time() - self._last_measurement_at > self._measurement_interval:
                self._last_measurement_at = time.time()
                self._read()

            if time.time() - self._metrics_updated_at > self._metric_update_interval:
                self._update_metrics()
                self._metrics_updated_at = time.time()

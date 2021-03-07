import logging

from prometheus_client import start_http_server

from meteo_station import MeteoStation
from meteo_station.settings import (
    MEASUREMENT_INTERVAL,
    SLIDING_WINDOW,
    PROMETHEUS_PORT
)

logging.basicConfig(
    format="%(asctime)s %(levelname)-6s %(name) %(message)s",
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    start_http_server(PROMETHEUS_PORT)

    meteo = MeteoStation(
        measurement_interval=MEASUREMENT_INTERVAL,
        sliding_window=SLIDING_WINDOW
    )
    meteo.run()

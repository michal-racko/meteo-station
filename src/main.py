import logging

from prometheus_client import start_http_server

from meteo_station import MeteoStation
from meteo_station.settings import (
    MEASUREMENT_INTERVAL,
    SLIDING_WINDOW,
    PROMETHEUS_PORT,
    LOG_LEVEL
)

logging.basicConfig(
    format="%(asctime)s %(levelname)-6s %(name) %(message)s",
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info(f'Starting prometheus on port: {PROMETHEUS_PORT}')
    start_http_server(PROMETHEUS_PORT)

    logger.info('Starting the meteo station')
    meteo = MeteoStation(
        measurement_interval=MEASUREMENT_INTERVAL,
        sliding_window=SLIDING_WINDOW
    )
    meteo.run()

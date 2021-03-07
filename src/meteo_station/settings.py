import os
import logging

log_level_map = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}
log_level_choice = str(
    os.getenv(
        'METEO_STATION_LOG_LEVEL',
        'info'
    )
).lower()

try:
    LOG_LEVEL = log_level_map[log_level_choice]
except KeyError:
    raise EnvironmentError(
        f'Invalid log level setting: {log_level_choice}'
    )

MEASUREMENT_INTERVAL = float(
    os.getenv(
        'METEO_STATION_MEASUREMENT_INTERVAL_SECONDS',
        0.1
    )
)

SLIDING_WINDOW = int(
    os.getenv(
        'METEO_STATION_SLIDING_WINDOW',
        300
    )
)

PROMETHEUS_PORT = int(
    os.getenv(
        'METEO_STATION_PROMETHEUS_PORT',
        8000
    )
)

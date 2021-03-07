import os

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

from prometheus_client import Gauge

meteo_station_outside_temperature_value = Gauge(
    'meteo_station_outside_temperature_value',
    'Outside temperature measurement mean'
)

meteo_station_outside_temperature_trend = Gauge(
    'meteo_station_outside_temperature_trend',
    'Outside temperature trend'
)

meteo_station_outside_pressure_value = Gauge(
    'meteo_station_outside_pressure_value',
    'Outside relative pressure measurement mean'
)

meteo_station_outside_pressure_trend = Gauge(
    'meteo_station_outside_pressure_trend',
    'Outside relative pressure trend'
)

meteo_station_outside_humidity_value = Gauge(
    'meteo_station_outside_humidity_value',
    'Outside relative humidity measurement mean'
)

meteo_station_outside_humidity_trend = Gauge(
    'meteo_station_outside_humidity_trend',
    'Outside relative humidity trend'
)

meteo_station_inside_temperature_value = Gauge(
    'meteo_station_intside_temperature_value',
    'Inside temperature measurement mean'
)

meteo_station_inside_temperature_trend = Gauge(
    'meteo_station_intside_temperature_trend',
    'Inside temperature trend'
)

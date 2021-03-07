from .meteo_station import MeteoStation

if __name__ == '__main__':
    meteo = MeteoStation(time_interval=1000, n_measurements=20)
    meteo.run()

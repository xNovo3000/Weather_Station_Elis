# encoding: UTF-8

"""
Version: 0.2
Updated: 29/04/2021
Author: NetcomGroup Innovation Team
"""

# AMBIENT IMPORT
from Simulation import SimulationClient
from WeatherStation import WeatherStationClient


# MAIN
if __name__ == "__main__":
    client = WeatherStationClient()
    client.start()

import os
from dataclasses import dataclass

from utils import JSONFile, Log

from dmc.core.station.StationLatLngData import StationLatLngData
from utils_future import LatLng

log = Log('Station')


@dataclass
class Station(StationLatLngData):
    DATA_PATH = os.path.join('data-static', 'stations.json')

    river_basin: str
    river: str
    name: str
    latLng: LatLng
    alert_level: float
    minor_flood_level: float
    major_flood_level: float

    def to_dict(self) -> dict:
        return {
            'river_basin': self.river_basin,
            'river': self.river,
            'station': self.name,
            'latLng': self.latLng.to_tuple(),
            'alert_level': self.alert_level,
            'minor_flood_level': self.minor_flood_level,
            'major_flood_level': self.major_flood_level,
        }

    @staticmethod
    def from_dict(data: dict) -> 'Station':
        return Station(
            river_basin=data['river_basin'],
            river=data['river'],
            name=data['station'],
            latLng=LatLng.from_tuple(data['latLng']),
            alert_level=data['alert_level'],
            minor_flood_level=data['minor_flood_level'],
            major_flood_level=data['major_flood_level'],
        )

    @staticmethod
    def get_latlng(station_name: str) -> LatLng:
        if station_name not in Station.NAME_TO_LATLNG:
            print(f'"{station_name}": LatLng(0, 0),')
            return LatLng(0, 0)
        return Station.NAME_TO_LATLNG[station_name]

    @staticmethod
    def build_from_rwl() -> list['Station']:
        rwl_path = os.path.join(
            'data-parsed',
            'river-water-level-and-flood-warnings',
            '20240523.063000.json',
        )
        data_list = JSONFile(rwl_path).read()
        station_list = []
        for data in data_list:
            station = Station(
                river_basin=data['river_basin'],
                river=data['river'],
                name=data['station'],
                latLng=Station.get_latlng(data['station']),
                alert_level=data['alert_level'],
                minor_flood_level=data['minor_flood_level'],
                major_flood_level=data['major_flood_level'],
            )
            station_list.append(station)

        n = len(station_list)
        JSONFile(Station.DATA_PATH).write(
            [station.to_dict() for station in station_list]
        )
        log.info(f'Wrote {n} stations to {Station.DATA_PATH}')

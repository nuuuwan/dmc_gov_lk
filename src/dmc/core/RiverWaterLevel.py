import os
from dataclasses import dataclass

from utils import JSONFile, Log, TimeUnit

from dmc.core.RiverWaterLevelParser import RiverWaterLevelParser

log = Log('RiverWaterLevel')


@dataclass
class RiverWaterLevel(RiverWaterLevelParser):
    # constants
    DOC_TYPE = 'river-water-level-and-flood-warnings'
    DIR_PDFS = os.path.join(
        'data',
        DOC_TYPE,
    )
    DIR_PARSED_DATA = os.path.join(
        'data-parsed',
        DOC_TYPE,
    )

    # dataclass
    ut: float
    river_basin: str
    river: str
    station: str
    alert_level: float
    minor_flood_level: float
    major_flood_level: float
    ut_water_level_1: float
    ut_water_level_2: float
    water_level_1: float
    water_level_2: float
    remarks: str
    remarks_rising: str
    ut_rainfall_end: float
    rainfall_duration: str
    rainfall: float

    @property
    def level(self):
        if self.water_level_2 >= self.major_flood_level:
            return 3
        if self.water_level_2 >= self.minor_flood_level:
            return 2
        if self.water_level_2 >= self.alert_level:
            return 1
        return 0

    @property
    def alert_emoji(self):
        return ['🟢', '🟡', '🟠', '🔴'][self.level]

    @property
    def level_text(self):
        return ['Normal', 'Alert', 'Minor Flood', 'Major Flood'][self.level]

    @property
    def rising_rate_m_per_s(self) -> float:
        return (self.water_level_2 - self.water_level_1) / (
            self.ut_water_level_2 - self.ut_water_level_1
        )

    @property
    def rising_rate_mm_per_hr(self) -> float:
        MM_IN_M = 1_000
        return self.rising_rate_m_per_s * TimeUnit.SECONDS_IN.HOUR * MM_IN_M

    @property
    def rising_rate_emoji(self):
        if self.rising_rate_mm_per_hr > 0:
            return '🡅'
        if self.rising_rate_mm_per_hr < 0:
            return '🡇'
        return ''

    @staticmethod
    def get_data_path_from_time_id(time_id):
        return os.path.join(
            RiverWaterLevel.DIR_PARSED_DATA, f'{time_id}.json'
        )

    def to_dict(self):
        return dict(
            ut=self.ut,
            river_basin=self.river_basin,
            river=self.river,
            station=self.station,
            alert_level=self.alert_level,
            minor_flood_level=self.minor_flood_level,
            major_flood_level=self.major_flood_level,
            ut_water_level_1=self.ut_water_level_1,
            ut_water_level_2=self.ut_water_level_2,
            water_level_1=self.water_level_1,
            water_level_2=self.water_level_2,
            remarks=self.remarks,
            remarks_rising=self.remarks_rising,
            ut_rainfall_end=self.ut_rainfall_end,
            rainfall_duration=self.rainfall_duration,
            rainfall=self.rainfall,
        )

    @staticmethod
    def get_time_ids():
        return [
            f[:-5]
            for f in os.listdir(RiverWaterLevel.DIR_PARSED_DATA)
            if f.endswith('.json')
        ]

    @staticmethod
    def get_latest_time_id():
        time_ids = RiverWaterLevel.get_time_ids()
        if not time_ids:
            return None
        return max(time_ids)

    @staticmethod
    def list_from_latest():
        time_id = RiverWaterLevel.get_latest_time_id()
        if time_id is None:
            return None
        return RiverWaterLevel.list_from_time_id(time_id)

    @staticmethod
    def list_from_time_id(time_id):
        data_path = RiverWaterLevel.get_data_path_from_time_id(time_id)
        data_list = [RiverWaterLevel(**d) for d in JSONFile(data_path).read()]
        return data_list

    @staticmethod
    def get_pdf_path_list():
        return [
            os.path.join(RiverWaterLevel.DIR_PDFS, f)
            for f in os.listdir(RiverWaterLevel.DIR_PDFS)
            if f.endswith('.pdf')
        ]

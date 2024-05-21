import os
from dataclasses import dataclass

import camelot
from utils import JSONFile, Log, Time, TimeFormat

log = Log('RiverWaterLevel')


def parse_float(s):
    if s == '-':
        return 0
    return float(s)


@dataclass
class RiverWaterLevel:
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
    def emoji(self):
        return ['🟢', '🟡', '🟠', '🔴'][self.level]

    @property
    def level_text(self):
        return ['Normal', 'Alert', 'Minor Flood', 'Major Flood'][self.level]

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
    def list_from_pdf(pdf_path):
        tables = camelot.read_pdf(pdf_path, pages='1', flavor='stream')
        table = tables[0]
        df = table.df
        d_list = df.values.tolist()

        date = d_list[1][1]
        time = d_list[1][9]
        log.debug(f'{date=}, {time=}, ')

        # 21-May-2024 6:30 AM
        def get_ut(time1):
            return TimeFormat('%d-%b-%Y %I:%M %p').parse(f'{date} {time1}').ut

        ut = get_ut(time)
        log.debug(f'{ut=}')

        water_level_time_1 = d_list[7][7]
        water_leveL_time_2 = d_list[7][8]
        log.debug(f'{water_level_time_1=}, {water_leveL_time_2=}')
        ut_water_level_1 = get_ut(water_level_time_1)
        ut_water_level_2 = get_ut(water_leveL_time_2)
        log.debug(f'{ut_water_level_1=}, {ut_water_level_2=}')
        assert ut_water_level_1 <= ut_water_level_2
        assert ut_water_level_2 <= ut

        rainfall_duration = int(d_list[3][12].split(' ')[0])
        rainfall_end_time = d_list[7][12]
        log.debug(f'{rainfall_duration=}, {rainfall_end_time=}')
        ut_rainfall_end = get_ut(rainfall_end_time)
        log.debug(f'{ut_rainfall_end=}')
        assert ut_rainfall_end <= ut

        rwl_list = []
        river_basin = None
        for d in d_list[7:]:
            if d[0]:
                if not d[0].startswith('('):
                    river_basin = d[0]
                continue

            if not d[1]:
                continue

            unit = d[3]
            unit_k = 1
            if unit == 'ft':
                unit_k = 0.3048

            def to_height(s):
                return parse_float(s) * unit_k

            rwl = RiverWaterLevel(
                ut=ut,
                river_basin=river_basin,
                river=d[1],
                station=d[2],
                alert_level=to_height(d[4]),
                minor_flood_level=to_height(d[5]),
                major_flood_level=to_height(d[6]),
                ut_water_level_1=ut_water_level_1,
                ut_water_level_2=ut_water_level_2,
                water_level_1=to_height(d[7]),
                water_level_2=to_height(d[8]),
                remarks=d[9],
                remarks_rising=d[10],
                ut_rainfall_end=ut_rainfall_end,
                rainfall_duration=rainfall_duration,
                rainfall=parse_float(d[12]),
            )

            rwl_list.append(rwl)

        time_id = TimeFormat.TIME_ID.format(Time(ut))
        if not os.path.exists(RiverWaterLevel.DIR_PARSED_DATA):
            os.makedirs(RiverWaterLevel.DIR_PARSED_DATA)
        data_path = RiverWaterLevel.get_data_path_from_time_id(time_id)
        JSONFile(data_path).write([rwl.to_dict() for rwl in rwl_list])
        log.info(f'Wrote {data_path}')
        return rwl_list

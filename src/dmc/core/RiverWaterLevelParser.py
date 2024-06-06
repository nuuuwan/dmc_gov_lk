import os
import re

import camelot
from utils import JSONFile, Log, Time, TimeFormat, TimeUnit

log = Log('RiverWaterLevelParser')


def parse_float(s):
    s = s.split(' ')[0]
    if s == '-':
        return 0
    if s == '':
        return 0
    if s == 'NA':
        return 0
    return float(s)


def clean(x):
    x = x.replace('\n', ' ')
    x = re.sub(r'\s+', ' ', x)
    x = x.strip()
    return x


class RiverWaterLevelParser:
    @staticmethod
    def parse_ut(date_id: str, time_str: str) -> int:
        time_str = (
            time_str.lower()
            .replace('noon', '12:00 pm')
            .replace('midnight', '12:00 am')
        )
        time_str = time_str.replace('.', ':')
        time_str = time_str.replace("12:00 12:00", '12:00')
        time_str = time_str.replace('p:m:', 'pm')
        time_str = time_str.replace('p:m', 'pm')
        ut = TimeFormat('%Y%m%d %I:%M %p').parse(f'{date_id} {time_str}').ut

        ut_date = TimeFormat.DATE_ID.parse(date_id).ut
        if ut > ut_date:
            ut -= TimeUnit.SECONDS_IN.DAY
        return ut

    @staticmethod
    def parse_rainfall_time(d_list, date_id, ut):
        rainfall_duration = int(
            d_list[0][-1].split(' ')[0].lower().replace('hr', '')
        )
        rainfall_end_time = (
            d_list[0][-1]
            .lower()
            .replace('p.m.', 'pm')
            .replace('p.m', 'pm')
            .replace('\npm', 'pm')
            .split('\n')[-1]
            .replace('mm at ', '')
        )
        log.debug(f'{rainfall_duration=}, {rainfall_end_time=}')
        ut_rainfall_end = RiverWaterLevelParser.get_ut(
            date_id, rainfall_end_time
        )
        log.debug(f'{ut_rainfall_end=}')
        assert ut_rainfall_end <= ut
        return ut_rainfall_end, rainfall_duration
    

    @staticmethod
    def parse_water_level_time_single(d_list, i_level, date_id, ut):
        water_level_time = d_list[0][i_level].split('\n')[-1]
       
        log.debug(f'{water_level_time=}')
        ut_water_level = RiverWaterLevelParser.get_ut(
            date_id, water_level_time
        )

        log.debug(f'{ut_water_level=}')
        assert ut_water_level <= ut
        return ut_water_level

    @staticmethod
    def parse_water_level_time(d_list, date_id, ut):
        ut_water_level_1 = RiverWaterLevelParser.parse_water_level_time_single(
            d_list, 7, date_id, ut
        )
        ut_water_level_2 = RiverWaterLevelParser.parse_water_level_time_single(
            d_list, 8, date_id, ut
        )
        log.debug(f'{ut_water_level_1=}, {ut_water_level_2=}')
        assert ut_water_level_1 <= ut_water_level_2
        assert ut_water_level_2 <= ut
        return ut_water_level_1, ut_water_level_2

    @classmethod
    def parse_river_water_level(
        cls,
        river_basin,
        d,
        ut,
        ut_rainfall_end,
        rainfall_duration,
        ut_water_level_1,
        ut_water_level_2,
    ):
        d = [clean(di) for di in d]
        if d[0]:
            river_basin = d[0]

        if not d[1] and not d[2]:
            return None

        unit = d[3]
        unit_k = 1
        if unit == 'ft':
            unit_k = 0.3048

        def to_height(s):
            return parse_float(s) * unit_k

        rwl = cls(
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
            rainfall=parse_float(d[-1]),
        )
        return rwl, river_basin

    @staticmethod
    def get_d_list(pdf_path):
        log.debug(f'Parsing {pdf_path}')
        tables = camelot.read_pdf(pdf_path, pages='1', flavor='lattice')
        if not tables:
            return []
        table = tables[0]
        df = table.df
        d_list = df.values.tolist()
        return d_list

    @classmethod
    def list_from_pdf(cls, pdf_path):
        pdf_file = os.path.basename(pdf_path)
        log.debug(f'{pdf_file=}')
        ut = TimeFormat('%Y%m%d.%H%M').parse(pdf_file[:13]).ut
        log.debug(f'{ut=}')

        time_id = TimeFormat.TIME_ID.format(Time(ut))
        data_path = cls.get_data_path_from_time_id(time_id)
        if os.path.exists(data_path):
            log.warn(f'{data_path} exists')
            return cls.list_from_time_id(time_id)

        date_id = pdf_file[:8]
        return cls.list_from_pdf_nocache(pdf_path, date_id, ut, data_path)

    @classmethod
    def list_from_pdf_nocache(cls, pdf_path, date_id, ut, data_path):
        d_list = cls.get_d_list(pdf_path)

        ut_rainfall_end, rainfall_duration = cls.parse_rainfall_time(
            d_list, date_id, ut
        )
        ut_water_level_1, ut_water_level_2 = cls.parse_water_level_time(
            d_list, date_id, ut
        )

        rwl_list = []
        river_basin = None
        for d in d_list[2:]:
            rwl, river_basin = cls.parse_river_water_level(
                river_basin,
                d,
                ut,
                ut_rainfall_end,
                rainfall_duration,
                ut_water_level_1,
                ut_water_level_2,
            )
            rwl_list.append(rwl)

        log.debug(rwl_list[0])
        log.debug(rwl_list[-1])
        n = len(rwl_list)

        if not os.path.exists(cls.DIR_PARSED_DATA):
            os.makedirs(cls.DIR_PARSED_DATA)

        JSONFile(data_path).write([rwl.to_dict() for rwl in rwl_list])
        log.info(f'Wrote {n} records to {data_path}')
        return rwl_list

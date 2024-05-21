import os

import camelot
from utils import JSONFile, Log, Time, TimeFormat, TimeUnit

log = Log('RiverWaterLevelParser')


def parse_float(s):
    s = s.split('\n')[0]
    if s == '-':
        return 0
    if s == '':
        return 0
    if s == 'NA':
        return 0
    return float(s)


class RiverWaterLevelParser:


    @classmethod
    def list_from_pdf(cls, pdf_path):
        # parse ut
        pdf_file = os.path.basename(pdf_path)
        log.debug(f'{pdf_file=}')
        ut = TimeFormat('%Y%m%d.%H%M').parse(pdf_file[:13]).ut
        log.debug(f'{ut=}')
        time_id = TimeFormat.TIME_ID.format(Time(ut))
        data_path = cls.get_data_path_from_time_id(time_id)
        if os.path.exists(data_path):
            log.warn(f'{data_path} exists')
            return cls.list_from_time_id(time_id)

        # parse PDF
        log.debug(f'Parsing {pdf_path}')
        tables = camelot.read_pdf(pdf_path, pages='1', flavor='lattice')
        if not tables:
            return []
        table = tables[0]
        df = table.df
        d_list = df.values.tolist()
        for i, d in enumerate(d_list):
            print(i, d)


        date_id = pdf_file[:8]

        def get_ut(time1):
            
            time1 = time1.lower().replace('noon', '12:00 pm').replace('midnight', '12:00 am')
            time1 = time1.replace('.', ':')
            time1 = time1.replace("12:00 12:00", '12:00')
            time1 = time1.replace('p:m:', 'pm')
            time1 = time1.replace('p:m', 'pm')
            ut = (
                TimeFormat('%Y%m%d %I:%M %p').parse(f'{date_id} {time1}').ut
            )

            ut_date = TimeFormat.DATE_ID.parse(date_id).ut
            if ut > ut_date:
                ut -= TimeUnit.SECONDS_IN.DAY
            return ut

        # parse rainfall time
        rainfall_duration = int(
            d_list[0][-1].split(' ')[0].lower().replace('hr', '')
        )
        rainfall_end_time = d_list[0][-1].lower().replace('p.m.', 'pm').replace('p.m', 'pm').replace('\npm', 'pm').split('\n')[-1].replace('mm at ', '')
        log.debug(f'{rainfall_duration=}, {rainfall_end_time=}')
        ut_rainfall_end = get_ut(rainfall_end_time)
        log.debug(f'{ut_rainfall_end=}')
        assert ut_rainfall_end <= ut

        # parse water level time
        water_level_time_1 = d_list[0][7].split('\n')[-1]
        water_leveL_time_2 = d_list[0][8].split('\n')[-1]

        log.debug(f'{water_level_time_1=}, {water_leveL_time_2=}')
        ut_water_level_1 = get_ut(water_level_time_1)
        ut_water_level_2 = get_ut(water_leveL_time_2)
        log.debug(f'{ut_water_level_1=}, {ut_water_level_2=}')
        assert ut_water_level_1 <= ut_water_level_2
        assert ut_water_level_2 <= ut

        rwl_list = []
        river_basin = None
        for d in d_list[2:]:

            if d[0]:
                river_basin = d[0]

            if not d[1] and not d[2]:
                continue

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

            rwl_list.append(rwl)

        log.debug(rwl_list[0])
        log.debug(rwl_list[-1])
        n = len(rwl_list)
        
        
        if not os.path.exists(cls.DIR_PARSED_DATA):
            os.makedirs(cls.DIR_PARSED_DATA)
        
        JSONFile(data_path).write([rwl.to_dict() for rwl in rwl_list])
        log.info(f'Wrote {n} records to {data_path}')
        return rwl_list

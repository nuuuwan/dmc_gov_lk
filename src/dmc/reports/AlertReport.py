from utils import Log, Time, TimeFormat

from dmc.core import RiverWaterLevel
from utils_future import Markdown

log = Log('AlertReport')


class AlertReport:
    def __init__(self):
        self.rwl_list = RiverWaterLevel.list_from_latest()

    @property
    def alert_path(self):
        return 'ALERTS.md'

    def get_sorted_rwl_list(self, alert_mode):
        rwl_list = [
            rwl
            for rwl in self.rwl_list
            if (alert_mode and rwl.level > 0)
            or (not alert_mode and rwl.level == 0)
        ]
        rwl_list.sort(
            key=lambda rwl: (
                -rwl.level,
                rwl.time_to_alert,
                rwl.river_basin,
                rwl.river,
                rwl.station,
            ),
        )
        return rwl_list

    def get_data_list(self, alert_mode):
        rwl_list = self.get_sorted_rwl_list(alert_mode)

        data_list = [
            dict(
                level=f'{rwl.alert_emoji} {rwl.level_text}',
                station=rwl.station,
                river=rwl.river,
                basin=rwl.river_basin,
                rising_rate=f'{rwl.rising_rate_mm_per_hr:.0f}'
                + f' {rwl.rising_rate_emoji}',
                level_m=f'{rwl.water_level_2:.1f}',
                alert_level_m=f'{rwl.alert_level:.1f}',
                minor_flood_level_m=f'{rwl.minor_flood_level_m:.1f}',
                major_flood_level_m=f'{rwl.major_flood_level_m:.1f}',

            )
            for rwl in rwl_list
        ]

        return data_list

    def get_md_river_water_level(self, alert_mode):
        data_list = self.get_data_list(alert_mode)
        key_to_label = {
            'level': 'Level',
            'station': 'Station',
            'river': 'River',
            'basin': 'Basin',
            'rising_rate': 'Rising Rate (mm/hr)',
            'level_m': 'Level (m)',
            'alert_level_m': 'Alert Level (m)',
            'minor_flood_level_m': 'Minor Flood Level (m)',
            'major_flood_level_m': 'Major Flood Level (m)',

        }
        md = Markdown()
        title = 'Alerts' if alert_mode else 'Other Stations'
        n = len(data_list)
        md.h2(f'{title} ({n:,})')
        md.table(
            data_list,
            key_to_label,
        )
        return md

    @property
    def md(self):
        ut = self.rwl_list[0].ut
        time_str = TimeFormat.TIME.format(Time(ut))
        log.debug(f'{time_str=}')

        md = Markdown()

        md.h1('River Water Levels :sri_lanka:')
        md.p(
            'As posted ' + md.link('https://www.dmc.gov.lk'),
        )
        md.p('Last updated ' + md.bold(time_str) + '.')
        md.div(
            'river-water-level-map',
            [md.image('images/river-water-level-map.png')],
        )
        md += self.get_md_river_water_level(True)
        md += self.get_md_river_water_level(False)

        return md

    def build(self):
        self.md.save(self.alert_path)

from utils import File, Log, Time, TimeFormat

from dmc.core import RiverWaterLevel

log = Log('AlertReport')


class AlertReport:
    def __init__(self):
        self.rwl_list = RiverWaterLevel.list_from_latest()

    @property
    def alert_path(self):
        return 'ALERTS.md'

    def get_lines_river_water_level(self, alert_mode):
        title = 'Alerts' if alert_mode else 'Other Stations'

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

        n = len(rwl_list)

        lines = [f'## {title} ({n:,})', '']

        lines.extend(
            [
                '| Level | Basin | River | Station'
                + ' | Rising Rate (mm/hr)'
                + ' | Level (m) | Alert Level (m) |'
                + (' Time to Alert |' if not alert_mode else ''),
                '|---|---|---|---'
                + '|--:'
                + ' |--:|--:|'
                + ('---|' if not alert_mode else ''),
            ]
        )

        for rwl in rwl_list:
            lines.append(
                f'| {rwl.alert_emoji} {rwl.level_text} | {rwl.river_basin}'
                + f' | {rwl.river} | {rwl.station}'
                + f' | {rwl.rising_rate_mm_per_hr:.0f} {rwl.rising_rate_emoji}'
                + f' | {rwl.water_level_2:.1f} | {rwl.alert_level:.1f} |'
                + (f' {rwl.time_to_alert_str} |' if not alert_mode else ''),
            )
        lines.append('')
        return lines

    @property
    def lines(self):
        ut = self.rwl_list[0].ut
        time_str = TimeFormat.TIME.format(Time(ut))
        log.debug(f'{time_str=}')

        return (
            [
                '# River Water Levels :sri_lanka:',
                '',
                '*As posted on [https://www.dmc.gov.lk](https://www.dmc.gov.lk)*',
                '',
                f'Last updated **{time_str}**.',
                '',
            ]
            + [
                '',
                '<div id="river-water-level-map">',
                '',
                '![River Water Level Map](images/river-water-level-map.png)',
                '',
                '</div>',
                '',
            ]
            + self.get_lines_river_water_level(True)
            + self.get_lines_river_water_level(False)
            + ['']
        )

    def build(self):
        File(self.alert_path).write_lines(self.lines)
        log.info(f'Wrote {self.alert_path}')

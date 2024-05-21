from utils import File, Log, Time, TimeFormat

from dmc.core import RiverWaterLevel

log = Log('AlertReport')


class AlertReport:
    @property
    def alert_path(self):
        return 'ALERTS.md'

    @property
    def lines_river_water_level(self):
        lines = ['## River Water Level :sri_lanka:', '']

        rwl_list = RiverWaterLevel.list_from_latest()
        rwl_list.sort(
            key=lambda rwl: (
                -rwl.level,
                rwl.time_to_alert,
                rwl.river_basin,
                rwl.river,
                rwl.station,
            ),
        )

        ut = rwl_list[0].ut
        time_str = TimeFormat.TIME.format(Time(ut))
        log.debug(f'{time_str=}')

        lines.extend([f'Last updated **{time_str}**.', ''])

        lines.extend(
            [
                '| Level | Basin | River | Station'
                + ' | Rising Rate (mm/hr)'
                + ' | Level (m) | Alert Level (m) | Time to Alert (hrs) |',
                '|---|---|---|---' + '|--:' + ' |--:|--:|--:|',
            ]
        )

        for rwl in rwl_list:
            lines.append(
                f'| {rwl.alert_emoji} {rwl.level_text} | {rwl.river_basin}'
                + f' | {rwl.river} | {rwl.station}'
                + f' | {rwl.rising_rate_mm_per_hr:.0f} {rwl.rising_rate_emoji}'
                + f' | {rwl.water_level_2:.1f} | {rwl.alert_level:.1f} | {rwl.time_to_alert_str}'
                + ' |'
            )
        lines.append('')
        return lines

    @property
    def lines(self):
        return [
            '# Alerts',
            '',
            '*As posted on [https://www.dmc.gov.lk](https://www.dmc.gov.lk)*',
            '',
        ] + self.lines_river_water_level

    def build(self):
        File(self.alert_path).write_lines(self.lines)
        log.info(f'Wrote {self.alert_path}')

from utils import File, Log, TimeFormat

from dmc.core import RiverWaterLevel

log = Log('AlertReport')


class AlertReport:
    @property
    def alert_path(self):
        return 'ALERTS.md'

    @property
    def lines_river_water_level(self):
        lines = ['## River Water Level', '']

        rwl_list = RiverWaterLevel.list_from_latest()
        rwl_list.sort(
            key=lambda rwl: (rwl.level,),
            reverse=True,
        )

        ut = rwl_list[0].ut
        time_str = TimeFormat.TIME.format(ut)
        
        lines.extend([f'Last updated **{time_str}**.', ''])

        lines.extend(
            [
                '| Level | Basin | River | Station |',
                '|-------|-------|-------|---------|',
            ]
        )

        for rwl in rwl_list:
            lines.append(
                f'| {rwl.emoji} {rwl.level_text} | {rwl.river_basin} '
                + f'| {rwl.river} | {rwl.station} |'
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

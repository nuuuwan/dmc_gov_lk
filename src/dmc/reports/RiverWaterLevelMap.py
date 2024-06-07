import os

import matplotlib.pyplot as plt
from gig import Ent, EntType
from matplotlib import collections as mc
from matplotlib.font_manager import FontProperties
from utils import Log, Time, TimeFormat

from dmc.core import RiverWaterLevel, Station
from utils_future import RunMode

log = Log('RiverWaterLevelMap')

FONT = FontProperties(fname=os.path.join('fonts', 'font.ttf'))


class RiverWaterLevelMap:
    ENT_TYPE = EntType.DISTRICT
    CIRCLE_RADIUS = 0.03

    @property
    def image_path(self):
        if not os.path.exists('images'):
            os.makedirs('images')
        return os.path.join(
            'images',
            'river-water-level-map.png',
        )

    @staticmethod
    def draw_river_lines():
        lines = []
        for station_names in Station.RIVERS.values():
            line = []

            prev_point = None
            for station_name in station_names:
                station = Station.from_name(station_name)
                point = [station.latLng.lng, station.latLng.lat]

                if prev_point:
                    x1, y1 = prev_point
                    x2, y2 = point
                    dx, dy = x2 - x1, y2 - y1
                    if abs(dx) < abs(dy):
                        x_mid = x1 + dx
                        y_mid = y1 + abs(dx) * dy / abs(dy)
                    else:
                        x_mid = x1 + abs(dy) * dx / abs(dx)
                        y_mid = y1 + dy
                    line.append([x_mid, y_mid])

                line.append(point)
                prev_point = point
            lines.append(line)

        lc = mc.LineCollection(lines, colors='#0888', linewidths=4)
        lc.set_zorder(2)
        ax = plt.gca()
        ax.add_collection(lc)

    @staticmethod
    def draw_river_labels():
        for river in Station.RIVERS:
            station0 = Station.from_name(Station.RIVERS[river][0])
            station1 = Station.from_name(Station.RIVERS[river][1])
            if not station0 or not station1:
                continue

            k = 1
            lng = station0.latLng.lng * k + station1.latLng.lng * (1 - k)
            lat = station0.latLng.lat * k + station1.latLng.lat * (1 - k)
            text = river.upper()
            plt.text(
                lng,
                lat,
                text,
                fontsize=3,
                horizontalalignment='center',
                fontstyle='italic',
                fontproperties=FONT,
            )

    @staticmethod
    def draw_district_geos(rwl_list):
        ax = plt.gca()
        ents = Ent.list_from_type(RiverWaterLevelMap.ENT_TYPE)
        for ent in ents:
            max_level = 0
            no_stations = True
            for rwl in rwl_list:
                station = Station.from_name(rwl.station)
                if not station:
                    continue
                if ent.id not in station.district_id:
                    continue
                no_stations = False
                max_level = max(max_level, rwl.level)

            if no_stations:
                color = '#8888'
            else:
                color = ['#080', '#ff0', '#f80', '#f00'][max_level]
                color = color + '8'

            geo = ent.geo()
            geo.plot(ax=ax, color=color, edgecolor='#fff')

    @staticmethod
    def draw_stations(rwl_list):
        ax = plt.gca()
        for rwl in rwl_list:
            station = Station.from_name(rwl.station)
            if not station:
                continue

            color = ['#080', '#ff0', '#f80', '#f00'][rwl.level]
            circle = plt.Circle(
                (station.latLng.lng, station.latLng.lat),
                RiverWaterLevelMap.CIRCLE_RADIUS,
                facecolor=color,
                edgecolor="black",
            )
            circle.set_zorder(2)
            ax.add_patch(circle)
            label = station.name.split('(')[0]
            plt.text(
                station.latLng.lng + 0.05,
                station.latLng.lat - 0.015,
                label,
                fontsize=5,
                fontproperties=FONT,
            )

    @staticmethod
    def draw_legend():
        ax = plt.gca()
        for level in range(0, 4):
            lng = 81
            lat = 9.5 - 0.1 * level
            color = ['#080', '#ff0', '#f80', '#f00'][level]
            circle = plt.Circle(
                (lng, lat),
                RiverWaterLevelMap.CIRCLE_RADIUS,
                facecolor=color,
                edgecolor="black",
            )
            ax.add_patch(circle)
            label = ['Normal', 'Alert', 'Minor Flood', "Major Flood"][level]
            plt.text(
                lng + 0.05,
                lat - 0.015,
                label,
                fontsize=5,
                fontproperties=FONT,
            )

    def draw(self):
        rwl_list = RiverWaterLevel.list_from_latest()

        fig, ax = plt.subplots()
        fig.set_size_inches(8, 8)

        RiverWaterLevelMap.draw_river_lines()
        RiverWaterLevelMap.draw_river_labels()
        RiverWaterLevelMap.draw_district_geos(rwl_list)
        RiverWaterLevelMap.draw_stations(rwl_list)
        RiverWaterLevelMap.draw_legend()

        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.text(
            0.5,
            1.05,
            'River Water Levels',
            transform=ax.transAxes,
            fontsize=10,
            horizontalalignment='center',
            fontproperties=FONT,
        )

        ut = rwl_list[0].ut
        time_str = TimeFormat.TIME.format(Time(ut))
        log.debug(f'{time_str=}')
        plt.text(
            0.5,
            0.99,
            time_str,
            transform=ax.transAxes,
            fontsize=20,
            horizontalalignment='center',
            fontproperties=FONT,
        )

        plt.savefig(self.image_path, dpi=600)
        plt.close()
        log.info(f'Wrote {self.image_path}')
        if RunMode.is_test():
            os.startfile(self.image_path)

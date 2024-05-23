import os

import matplotlib.pyplot as plt
from gig import Ent, EntType
from utils import Log, Time, TimeFormat

from dmc.core import RiverWaterLevel, Station

log = Log('RiverWaterLevelMap')


class RiverWaterLevelMap:
    ENT_TYPE = EntType.DISTRICT

    @property
    def image_path(self):
        if not os.path.exists('images'):
            os.makedirs('images')
        return os.path.join(
            'images',
            'river-water-level-map.png',
        )

    def draw(self):
        ents = Ent.list_from_type(self.ENT_TYPE)
        rwl_list = RiverWaterLevel.list_from_latest()

        
        fig, ax = plt.subplots()
        fig.set_size_inches(4.5, 8)
        plt.tight_layout()
        
        
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
            ax.grid(False)

        for level in range(0, 4):
            for rwl in rwl_list:
                station = Station.from_name(rwl.station)
                if not station:
                    continue
                if rwl.level != level:
                    continue
                color = ['#080', '#ff0', '#f80', '#f00'][rwl.level]
                circle = plt.Circle(
                    (station.latLng.lng, station.latLng.lat), 0.03, facecolor=color,edgecolor="black"
                )
                ax.add_patch(circle)
                plt.text(
                    station.latLng.lng+0.05,
                    station.latLng.lat-0.015,
                    station.name,
                    fontsize=5,
                )

        for level in range(0, 4):
            lng = 81
            lat = 9.5 - 0.1 * level
            color = ['#080', '#ff0', '#f80', '#f00'][level]
            circle = plt.Circle(
                (lng, lat), 0.03, facecolor=color,edgecolor="black"
            )
            ax.add_patch(circle)
            label = ['Normal', 'Alert', 'Minor Flood', "Major Flood"][level]
            plt.text(
                lng+0.05, lat-0.015,
                label,
                fontsize=5,
            )    
        

        ax.set_xticks([])
        ax.set_yticks([])

        ut = rwl_list[0].ut
        time_str = TimeFormat.TIME.format(Time(ut))
        log.debug(f'{time_str=}')

        plt.title(f'River Water Levels ({time_str})')
        plt.savefig(self.image_path, dpi=600)
        plt.close()
        log.info(f'Wrote {self.image_path}')
        if os.name == 'nt':
            os.startfile(self.image_path)

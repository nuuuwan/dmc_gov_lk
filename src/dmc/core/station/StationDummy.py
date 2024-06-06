from utils_future import LatLng
from utils import JSONFile
import os

class StationDummy:
    @classmethod
    def list_all_dummy(cls):
        idx = JSONFile(os.path.join('data-static', 'station-dummy.json')).read()
        return [cls.dummy(k, LatLng(v[0], v[1])) for k, v in idx.items()]

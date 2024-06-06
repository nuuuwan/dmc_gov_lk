import os

from utils import JSONFile


class StationDistrictData:
    NAME_TO_DISTRICT_ID = JSONFile(
        os.path.join('data-static', 'name-to-district-id.json')
    ).read()

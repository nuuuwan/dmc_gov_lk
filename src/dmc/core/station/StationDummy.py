from utils_future import LatLng


class StationDummy:
    @classmethod
    def list_all_dummy(cls):
        return [
            cls.dummy(
                'Colombo', LatLng(6.979094803911703, 79.86979574279339)
            ),
            cls.dummy(
                'Kalutara', LatLng(6.586233701047157, 79.95717564003346)
            ),
            cls.dummy(
                'Trincomalee', LatLng(8.53304284725816, 81.26385044889133)
            ),
            cls.dummy('Gintota', LatLng(6.06281446318493, 80.17408845037367)),
            cls.dummy('Matara', LatLng(5.94125560680328, 80.53812578991025)),
            cls.dummy(
                'Ambalantota', LatLng(6.107647576360852, 81.05029286051283)
            ),
            cls.dummy(
                'Kirinda', LatLng(6.194772632777804, 81.29341879397064)
            ),
            cls.dummy('Yala', LatLng(6.364615249121397, 81.53804157548875)),
            cls.dummy(
                'Arugam Bay', LatLng(6.81607800117203, 81.8232377069113)
            ),
            cls.dummy(
                'Kalkudah', LatLng(7.940520517524321, 81.55139931294406)
            ),
            cls.dummy(
                'Pulmoddai', LatLng(8.918316148045907, 81.01609289069512)
            ),
            cls.dummy(
                'Vankalai',
                LatLng(8.802644113443238, 79.91839691571735),
            ),
            cls.dummy(
                'Chilaw',
                LatLng(7.613447600108512, 79.7982666610457),
            ),
            cls.dummy(
                'Kochchikade',
                LatLng(7.272648499907399, 79.84288403277398),
            ),
            cls.dummy(
                'Negombo',
                LatLng(7.206810419406433, 79.82769525874056),
            ),
            cls.dummy(
                'Puttalam',
                LatLng(8.101974738017296, 79.81546247103633),
            ),
            cls.dummy(
                'Kokkilai',
                LatLng(9.016296922963633, 80.88567631969876),
            ),
        ]

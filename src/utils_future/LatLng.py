from dataclasses import dataclass


@dataclass
class LatLng:
    lat: float
    lng: float

    def to_tuple(self):
        return (self.lat, self.lng)

    @staticmethod
    def from_tuple(tuple):
        return LatLng(*tuple)

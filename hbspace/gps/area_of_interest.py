from .distance import GeodesicDistance

import numpy as np

class AreaOfInterest:
    def __init__(self, name, lat, lon, radius, distance = GeodesicDistance()):
        self.name = name
        self.lat  = lat
        self.lon = lon
        self.radius = radius
        self.distance = distance
        
    def is_within(self, lats, lons):
        d = self.distance.compute_distances_from_o(lats, lons, self.lat, self.lon)
        
        is_in = np.zeros_like(lats, dtype=np.int)
        is_in[d < self.radius] = 1
        
        return is_in
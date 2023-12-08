from .distance import GeodesicDistance

import numpy as np
import csv

import pandas as pd
import typing

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
    
def parse_areas_of_interest(fname: str, varnames: typing.List[str]) -> typing.Dict[str, AreaOfInterest]:
    """
    varname[0]: area_id
    varname[1]: latitude
    varname[2]: longitude
    varname[3]: radius
    """
    aoi = {}
    var_area_id = varnames[0]
    with open(fname, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data = [row[k] for k in varnames[1:]]
            try:
                data_numerics = pd.to_numeric(data, errors='raise')
            except:
                data_numerics = None

            if data_numerics is not None:
                aa = AreaOfInterest(row[var_area_id], *data_numerics)
                aoi[row[var_area_id]] = aa

    return aoi



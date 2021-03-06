# 
# This file is part of the Health Behavior in Space software (https://github.com/dsalvolab/hbspace).
# Copyright (c) 2022 Umberto Villa.
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

# import geopy.distance as gpd
# import numpy as np
# 
# def compute_distances(latitudes1, longitudes1, latitudes2, longitudes2, pad = False):
#     d = [gpd.distance((lat1, lon1), (lat2, lon2)).meters
#                          for (lat1,lon1,lat2, lon2) in zip(latitudes1, longitudes1,
#                                                             latitudes2, longitudes2) ]
#     if pad:
#         d.insert(0, 0.)
#     
#     return np.array(d)        
# 
#     
# def compute_distance(coords1, coords2):
#     return gpd.distance(coords1, coords2).meters


import geopy.distance as gpd
import numpy as np


try:
    from pyproj import Geod
    has_pyproj = True
except:
    has_pyproj = False


if has_pyproj:  
    class GeodesicDistancePyproj:
        def __init__(self, ellps = 'WGS84'):
            self.g = Geod(ellps=ellps)
        
        def compute_distances(self, latitudes1, longitudes1, latitudes2, longitudes2, pad = False):
            d = [self.compute_distance(lat1,lon1,lat2, lon2)
                             for (lat1,lon1,lat2, lon2) in zip(latitudes1, longitudes1,
                                                                latitudes2, longitudes2) ]
            if pad:
                d.insert(0, 0.)
        
            return np.array(d)        
    
        
        def compute_distance(self, lat1, lon1, lat2, lon2):
            d = self.g.inv(lat1, lon1, lat2, lon2)[2]
            if(np.isnan(d)):
                d = 0.
                
            return d
    
class GeodesicDistanceGeopy:
    def __init__(self, ellps = 'WGS84'):
        #self.g = Geod(ellps=ellps)
        pass
    
    def compute_distances(self, latitudes1, longitudes1, latitudes2, longitudes2, pad = False):
        d = [self.compute_distance(lat1,lon1,lat2, lon2)
                         for (lat1,lon1,lat2, lon2) in zip(latitudes1, longitudes1,
                                                            latitudes2, longitudes2) ]
        if pad:
            d.insert(0, 0.)
    
        return np.array(d)        

    
    def compute_distance(self, lat1, lon1, lat2, lon2):
        coords1 = (lat1, lon1)
        coords2 = (lat2, lon2)
        d = gpd.distance(coords1, coords2).meters

        if(np.isnan(d)):
            d = 0.
            
        return d
    
    def compute_distance_t(self, coords1, coords2):
        d = gpd.distance(coords1, coords2).meters

        if(np.isnan(d)):
            d = 0.
            
        return d
    
GeodesicDistance = GeodesicDistanceGeopy

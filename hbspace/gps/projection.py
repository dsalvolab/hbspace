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

import numpy as np

try:
    from pyproj import Proj
    has_pyproj = True
except:
    has_pyproj = False

if has_pyproj:
    def get_zone(ref_long):
        """
        ref_long is measured in degrees
        ref_long is positive if EAST
        ref_long is negative if WEST
        """
        return ((ref_long + 180)//6 % 60) + 1

    class UTMprojection:
        def __init__(self, zone, ellps='WGS84'):
            self.p = Proj(proj='utm',zone=zone,ellps=ellps)
        
        def get_xy(self, lat, lon):
            return self.p(lat, lon)
    
        def get_xys(self, lats, lons):
            npoints = lats.shape[0]
        
            x = np.zeros_like(lats)
            y = np.zeros_like(lats)
        
            for i in np.arange(npoints):
                x[i], y[i] = self.p(lats[i], lons[i])
            
            return x,y
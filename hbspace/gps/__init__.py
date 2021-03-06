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

from .gpsData import GPSData
from .trip import Trip
from .location import Visit, Location
from .rawGpsData import RawGPSData

from .parameter import invalidFixesDefaults, \
                       locationDetectionDefaults, \
                       tripDetectionDefaults, \
                       speedCutoffDefaults, \
                       defaultParameters
                       
from .distance import GeodesicDistance

#from .projection import  UTMprojection

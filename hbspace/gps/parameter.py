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

from ..common import ParameterList

def invalidFixesDefaults():
    parameters = ParameterList()
    parameters.add_param("filter",     True, "Filter invalid fixes")
    parameters.add_param("max_speed",   130., "Maximum speed (KM/hour)")
    parameters.add_param("max_d_elev",  125., "Maximum change in elevation (meters)")
    parameters.add_param("max_dist",   5000., "Maximum distance between fixes (meters)")
    parameters.add_param("min_dist",      1., "Minimum distance between fixes (meters)")
    parameters.add_param("max_sloss",   600., "Max loss of signal allowed (seconds)" )
    parameters.add_param("rm_lone",    True, "Remove lone fixes between SLOSSes")
    parameters.add_param("rm_sparse",    True, "Remove short intervals <3 min between SLOSSes")
    return parameters
    
def locationDetectionDefaults():
    parameters = ParameterList()
    parameters.add_param("pause",    True, "Include trip pause locations")
    parameters.add_param("trap",    False, "Trap points within locations")
    parameters.add_param("radius",    30., "Cluster radius (meters)")
    parameters.add_param("min_time", 300., "Minimum time at location (seconds)")
    return parameters
    
def tripDetectionDefaults():
    parameters = ParameterList() 
    parameters.add_param("min_dist",      10, "Minimum distance traveled over 1 minute (meters)")
    parameters.add_param("min_length",   100, "Minimum trip length (meters)")
    parameters.add_param("radius",       30., "Cluster radius (meters)")
    parameters.add_param("min_dur",      180, "Minimum trip duration (seconds)")
    parameters.add_param("min_pause",    180, "Minimum pause time (seconds)")
    parameters.add_param("max_pause",    300, "Maximum pause time (seconds)")
    parameters.add_param("min_avg_speed",1.5, "Minimum avg speed (Km/h)")   #ADDED
    parameters.add_param("single_loc", False, "Allow trips within a single location") #UNUSED!
    return parameters

def speedCutoffDefaults():
    parameters = ParameterList() 
    parameters.add_param("vehicle",   [200., 200.],   "Vehicle speed cutoff value (mean, max) (Km/hour)")
    parameters.add_param("bike",      [ 25., 35. ], "Bicycle speed cutoff value (mean, max) (Km/hour)")
    parameters.add_param("walk",      [ 10., 15. ],  "Walk speed cutoff value (mean, max)   (Km/hour)")
    #parameters.add_param("slow_walk", [ 0., 1.  ],  "Sedentary speed cutoff value (Km/hour)") #REMOVED!
    return parameters 

def defaultParameters():
    parameters = ParameterList() 
    parameters.add_param("invalid_fixes", invalidFixesDefaults(), "Filter invalid values")
    parameters.add_param("location", locationDetectionDefaults(), "Location detection")
    parameters.add_param("trip", tripDetectionDefaults(), "Trip detection")
    parameters.add_param("speed", speedCutoffDefaults(), "Speed cutoff values")
    return parameters
    
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

def plot_map_by_trip(data, plt):
    """
    plt matplotlib object
    """
    x,y = data.proj.get_xys(data.latitudes, data.longitudes)
    x = x*1e-3
    y = y*1e-3
    x = x[data.trip_marker >= 0]
    y = y[data.trip_marker >= 0]
    trip_marker = data.trip_marker[data.trip_marker >= 0 ]
    colors = np.arange(len(data.trips))
    np.random.shuffle(colors)
    
    for i in range(trip_marker.shape[0]):
        trip_marker[i] = colors[ trip_marker[i] ]
    
    plt.scatter(x,y, c=trip_marker)
    plt.title("xy map")
    plt.xlabel("Eastings (Km)")
    plt.ylabel("Northings (Km)")  
    
def plt_locations(data,plt):
    x,y = data.proj.get_xys(data.latitudes, data.longitudes)   
    x = x*1e-3
    y = y*1e-3
    x = x[data.trip_marker < 0]
    y = y[data.trip_marker < 0]
    
    plt.scatter(x,y)
    plt.title("Locations")
    plt.xlabel("Eastings (Km)")
    plt.ylabel("Northings (Km)")  

def plot_cumdist_by_trip(data,plt):
    
    reftime = data.timestamps[0]
    days = (data.timestamps  - reftime)/(24.*3600.)
    for trip in data.trips:
        trip_id = trip.id
        plt.plot(days[data.trip_marker==trip_id],
                 1e-3*(data.cumdist[data.trip_marker==trip_id] - data.cumdist[trip.start_index]) )
        
    #plt.plot(days[data.trip_marker==-1], 1e-3*data.cumdist[data.trip_marker==-1], 'ok', markersize=1)
    
    plt.title("Cumulative distance")
    plt.xlabel("Time (days)")
    plt.ylabel("Cumulative distance per trip")
    
def plot_state_by_trip(data,plt):
    
    reftime = data.timestamps[0]
    days = (data.timestamps  - reftime)/(24.*3600.)
    for trip_id in np.arange(len(data.trips)):
        plt.plot(days[data.trip_marker==trip_id], data.state[data.trip_marker==trip_id], "s", markersize=1)
        
    plt.plot(days[data.trip_marker==-1], data.state[data.trip_marker==-1], 'ok', markersize=1)
    
    plt.title("State: Stationary, Motion, Paused")
    plt.xlabel("Time (days)")
    plt.ylabel("State")
        
        
    
    


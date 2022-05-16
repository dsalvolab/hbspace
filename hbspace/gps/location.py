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
import scipy.stats as sstats
from .trip import trip_mode

class Visit:
    def __init__(self, id, cm_lat, cm_lon, radius, duration, first_index, stop):
        self.duration = duration
        self.cm_lat   = cm_lat
        self.cm_lon   = cm_lon
        self.radius   = radius
        
        self.first_index = first_index
        self.stop  = stop
        
        self.id = id
        
        self.locationId = None
        self.is_valid   = None
        
        self.is_home        = None
        self.store_id       = None
        self.store_marker   = None
        
        self.dist_from_home = None
        
    def distanceFromHome(self, data):
        if data.is_home is not None:
            is_home = data.is_home[self.first_index : self.stop]
            if( np.mean(is_home)>0.5 ) or data.is_home[self.first_index] or data.is_home[self.stop-1]:
                self.is_home = 1
            else:
                self.is_home = 0
                
        data.is_home[self.first_index : self.stop] = self.is_home
        if self.is_home == 1:
            self.dist_from_home = 0.
        else:
            cm_coords = (self.cm_lat, self.cm_lon)
            self.dist_from_home = data.g.compute_distance_t(cm_coords, data.home_coords)
            
    def distanceFromStore(self, data):
        if data.store_id is not None:
            store_id = data.store_id[self.first_index : self.stop]
            mode = sstats.mode(store_id, axis=None)
            my_store = mode[0][0]
            if my_store > -1 and np.mean(store_id == store_id)>0.5:
                self.store_id = my_store
                self.store_marker = data.store_maps_coords[my_store][2]
            else:
                self.store_id=""
                self.store_marker=""
                
    def _didArrivingTripDepartedHome(self, data):
        arrival_trip_id = data.trip_marker[ self.first_index ]
        if arrival_trip_id == -1:
            return ""
        
        for t in data.trips:
            if t.id == arrival_trip_id:
                return t.departedHome(data)
            
        raise
    
    def _didDepartingTripArrivedHome(self, data):
        dept_trip_id = data.trip_marker[ self.stop - 1 ]
        if dept_trip_id == -1:
            return ""
        
        for t in data.trips:
            if t.id == dept_trip_id:
                return t.arrivedHome(data)
            
        raise
                
        
        
    def getInfo(self, data):
        """
        data --> GPSData
        out --> list of Dictionaries
        """
        out = {}
        out["partid"]      = data.id
        assert self.locationId is not None
        out["locationid"]  = self.locationId+1
        out["visitid"]      = self.id + 1
        out["latitude"]     = self.cm_lat
        out["longitude"]    = self.cm_lon
        out["radius"]       = self.radius
        out["duration"]     = self.duration/60.
        out["visit_start_date"]  = data.local_datetime[self.first_index].strftime('%Y-%m-%d')
        out["visit_start_time"]  = data.local_datetime[self.first_index].strftime('%H:%M:%S')
        out["visit_end_date"]    = data.local_datetime[self.stop-1].strftime('%Y-%m-%d')
        out["visit_end_time"]    = data.local_datetime[self.stop-1].strftime('%H:%M:%S')
        out["arrival_mode"] = trip_mode[ data.trip_type[self.first_index ] ]
        if data.trip_marker[ self.first_index ] >= 0:
            out["arrival_trip_id"] = data.trip_marker[ self.first_index ]+1
        else:
            if data.is_first_fix[self.first_index]:
                out["arrival_trip_id"] = -1
            else:
                out["arrival_trip_id"] = "unknown"
        if self.stop < len(data.timestamps):
            out["departure_mode"]    = trip_mode[ data.trip_type[self.stop-1] ]
            if data.trip_marker[ self.stop-1 ] >= 0:
                    out["departure_trip_id"] = data.trip_marker[ self.stop-1 ]+1
            else:
                if data.is_first_fix[self.first_index]:
                    out["departure_trip_id"] = -1
                else:
                    out["departure_trip_id"] = "unknown"
                    
        if self.is_home is not None:
            out["is_home"] = self.is_home
            out["distance_from_home"] = self.dist_from_home
            out["came_from_home"] = self._didArrivingTripDepartedHome(data)
            out["went_home"] = self._didDepartingTripArrivedHome(data)
            
        if self.store_id is not None:
            out["store_id"] = self.store_id
            out["is_fresh_store"] = self.store_marker
            
        return out
        
    @classmethod
    def infoKeys(self):
        return [
                "partid",                 #Participant ID
                "locationid",             #Trip ID
                "visitid",                #visit id
                "latitude",               #Location latitude (N: positive, S: negative)
                "longitude",              #Location longitudine (W: positive, E: negative)
                "radius",                 #Location radius
                "visit_start_date",       #Visit starts date
                "visit_start_time",       #Visit starts time
                "visit_end_date",         #Visit ends date
                "visit_end_time",         #Visit ends time
                "duration",               #Stay at that location (minutes)
                "arrival_mode",           #Mode of arrival: vehicle, bike, walk
                "arrival_trip_id",        # ID of arrival trip 
                "departure_mode",         #Mode of departure: vehicle, bike, walk
                "departure_trip_id"       # ID of departure trip
                ]
        
    @classmethod
    def infoKeysExt(self):
        return [
                "partid",                 #Participant ID
                "locationid",             #Trip ID
                "visitid",                #visit id
                "latitude",               #Location latitude (N: positive, S: negative)
                "longitude",              #Location longitudine (W: positive, E: negative)
                "radius",                 #Location radius
                "visit_start_date",       #Visit starts date
                "visit_start_time",       #Visit starts time
                "visit_end_date",         #Visit ends date
                "visit_end_time",         #Visit ends time 
                "duration",               #Stay at that location (minutes)
                "arrival_mode",           #Mode of arrival: vehicle, bike, walk
                "arrival_trip_id",        # ID of arrival trip 
                "departure_mode",         #Mode of departure: vehicle, bike, walk
                "departure_trip_id",      # ID of departure trip
                "is_home",
                "distance_from_home",
                "store_id",
                "is_fresh_store",
                "came_from_home",
                "went_home"
                ]

class Location:
    def __init__(self, id, visit, data):
        if visit is None:
            return
        else:
            self.id = id
            self.duration = [visit.duration]
#           self.cm_lats = [candidateLocation.cm_lat]
#           self.cm_lons = [candidateLocation.cm_lon]
#           self.radiuses = [candidateLocation.radius]
            self.first_indexes  = [visit.first_index]
            self.stops          = [visit.stop]
            self.visit_ids      = [visit.id]
            self.visit_is_valid = [visit.is_valid]
            
            assert visit.is_valid is not None
        
            self.cm_lat = visit.cm_lat
            self.cm_lon = visit.cm_lon
            self.radius = visit.radius
            self.nvisits = 1
            
            self.is_home        = visit.is_home
            self.store_id       = visit.store_id
            self.store_marker   = visit.store_marker
            self.dist_from_home = visit.dist_from_home
            
            self.ntimes_arriving_trip_originated_from_home = 0
            self.ntimes_departing_trip_arrived_at_home     = 0
            
            if visit._didArrivingTripDepartedHome(data) == 1:
                self.ntimes_arriving_trip_originated_from_home += 1
                
            if visit._didDepartingTripArrivedHome(data) == 1:
                self.ntimes_departing_trip_arrived_at_home += 1
            
            visit.locationId = id
        
    def merge(self, other, data, radius):
        """
        Return True if merge succeded, False otherwise
        """
        
        assert other.locationId is None
        assert other.is_valid is not None
        
        cm_dist = data.g.compute_distance(self.cm_lat, self.cm_lon, other.cm_lat, other.cm_lon)
        
        if cm_dist > radius - .5*(self.radius - other.radius):
            return False #Quick return if locations are far away
        
        if self.is_home != other.is_home:
            return False
        
        if self.store_id  != other.store_id:
            return False
        
        # Do the math
        cum_dur = np.sum(self.duration)
        new_cm_lat = (cum_dur*self.cm_lat + other.duration*other.cm_lat)/(cum_dur + other.duration)
        new_cm_lon = (cum_dur*self.cm_lon + other.duration*other.cm_lon)/(cum_dur + other.duration)
        
        lats = []
        lons = []
        for i in range(self.nvisits):
            [lats.append(lat) for lat in data.latitudes[self.first_indexes[i]:self.stops[i]] ]
            [lons.append(lon) for lon in data.longitudes[self.first_indexes[i]:self.stops[i] ] ]
            
        [lats.append(lat) for lat in data.latitudes[other.first_index:other.stop] ]
        [lons.append(lon) for lon in data.longitudes[other.first_index:other.stop] ]
        
        new_radius = max([data.g.compute_distance(lat, lon, new_cm_lat, new_cm_lon) for (lat,lon) in zip(lats, lons) ] )
        
        if new_radius <= radius:
            self.duration.append(other.duration)
#            self.cm_lats.append(other.cm_lat)
#            self.cm_lons.append(other.cm_lon)
#            self.radiuses.append(other.radius)
            self.first_indexes.append(other.first_index)
            self.stops.append(other.stop)
            self.visit_ids.append(other.id)
            self.visit_is_valid.append(other.is_valid)
            
            self.cm_lat = new_cm_lat
            self.cm_lon = new_cm_lon
            self.radius = new_radius
            
            if other._didArrivingTripDepartedHome(data) == 1:
                self.ntimes_arriving_trip_originated_from_home += 1
                
            if other._didDepartingTripArrivedHome(data) == 1:
                self.ntimes_departing_trip_arrived_at_home += 1
            
            
            self.dist_from_home = (cum_dur*self.dist_from_home + other.duration*self.dist_from_home)/(cum_dur + other.duration)
            
            other.locationId = self.id
        
            self.nvisits +=1
            return True
        else:
            return False
        
        
    def getInfo(self, data):
        """
        data --> GPSData
        out --> Dictionary
        """
        out = {}
        
        out["partid"]     = data.id
        out["locationid"] = self.id+1
        out["nvisits"]    = self.nvisits
        out["nvalidvisits"] = sum( self.visit_is_valid )
        out["latitude"]   = self.cm_lat
        out["longitude"]  = self.cm_lon
        out["radius"]     = self.radius
        out["avg_stay"]   = np.mean(self.duration)/60.
        
        ind_val = np.array(self.visit_is_valid, dtype=np.int)
        duration = np.array(self.duration)
        if np.any(ind_val > 0):
            out["avg_stay_validVisit"]   = np.mean(duration[ind_val > 0])/60.
        else:
            out["avg_stay_validVisit"]   = 0
        
        if self.is_home is not None:
            out["is_home"] = self.is_home
            out["distance_from_home"] = self.dist_from_home
            out["number_of_times_came_from_home"] = self.ntimes_arriving_trip_originated_from_home
            out["number_of_times_went_home"]      = self.ntimes_departing_trip_arrived_at_home
            
        if self.store_id is not None:
            out["store_id"] = self.store_id
            out["is_fresh_store"] = self.store_marker
        
        return out
    
    @classmethod  
    def infoKeys(self):
        return [
                "partid",                 #Participant ID
                "locationid",             #location ID
                "nvisits",                #Number of visits
                "nvalidvisits",
                "latitude",               #Location latitude (N: positive, S: negative)
                "longitude",              #Location longitudine (W: positive, E: negative)
                "radius",                 #Location radius
                "avg_stay",               #Average stay at that location (minutes)
                "avg_stay_validVisit"     #Valid visit only at that location (minutes)
                ]
        
    @classmethod  
    def infoKeysExt(self):
        return [
                "partid",                 #Participant ID
                "locationid",             #location ID
                "nvisits",                #Number of visits
                "nvalidvisits",
                "latitude",               #Location latitude (N: positive, S: negative)
                "longitude",              #Location longitudine (W: positive, E: negative)
                "radius",                 #Location radius
                "avg_stay",               #Average stay at that location (minutes)
                "avg_stay_validVisit",    #Valid visit only at that location (minutes)
                "is_home",
                "distance_from_home",
                "store_id",
                "is_fresh_store",
                "number_of_times_came_from_home",
                "number_of_times_went_home"
                ]
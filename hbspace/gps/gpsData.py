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
from .trip import Trip
from .location import Visit, Location
from .distance import GeodesicDistance
from ..common.conversions import meter_per_second_to_km_per_hour,\
    km_per_hour_to_meter_per_second
    

    
class Fix:
    def __init__(self, tstmp, coords, elev, index):
        self.tstmp  = tstmp
        self.coords = coords
        self.elev   = elev
        self.index  = index
        
    def assign(self, other):
        self.tstmp  = other.tstmp
        self.coords = other.coords
        self.elev   = other.elev
        self.index  = other.index
        
class GPSData:
    
    STATIONARY = 0
    MOTION     = 1
    PAUSE      = 2
    MOTION_NOT_TRIP = -1
    
    def __init__(self, id, fname, proj=None):
        
        self.g = GeodesicDistance()
        self.proj = proj
        
        self.id = id
        self.fname = fname
        
        self.timestamps     = None
        self.local_datetime = None
        self.latitudes      = None
        self.longitudes     = None
        self.elevations     = None
        self.is_first_fix   = None
        self.is_last_fix    = None
        
        self.valid_fixes_id = None
        self.ntotal_fixes   = None
        
        self.speeds      = None
        self.cumdist     = None
        
        self.state           = None
        self.trip_marker     = None
        self.trip_type       = None
        self.location_marker = None
        self.visit_marker    = None
        
        self.is_valid        = None
        
        self.trips = []
        self.locations = []
        self.visits = []
        
        self.locationCounter = 0
        self.tripCounter     = 0
        self.visitCounter    = 0
        
        self.home_coords  = None
        self.is_home      = None
        
        self.store_maps_coords = None
        self.store_id     = None
        self.store_marker = None
        
        self.unordered_source = False
        self.logging = False
        
        
    def compute_dist(self):        
        self.speeds      = np.zeros_like(self.timestamps)
        self.cumdist     = np.zeros_like(self.timestamps)
        
        prev_time    = None
        prev_coords  = None
        rundist     =  0
        
        for i in np.arange(self.timestamps.shape[0]):
            if self.is_first_fix[i]:
                prev_coords  = (self.latitudes[i], self.longitudes[i])
                prev_time    = self.timestamps[i]
                rundist      = 0
                self.cumdist[i]  = 0
                
                next_coords = (self.latitudes[i+1], self.longitudes[i+1])
                next_time  = self.timestamps[i+1]
                
                d =  self.g.compute_distance_t(prev_coords, next_coords)
                
                self.speeds[i]   = d/(next_time - prev_time)
            else:
                cur_coords = (self.latitudes[i], self.longitudes[i])
                cur_time   = self.timestamps[i]
                
                cur_dist   = self.g.compute_distance_t(prev_coords, cur_coords)
                
                assert np.isnan(cur_dist)==False 
                
                rundist += cur_dist
                self.cumdist[i] = rundist
                self.speeds[i]  = meter_per_second_to_km_per_hour( cur_dist / (cur_time - prev_time) )
                
                prev_coords = cur_coords
                prev_time   = cur_time
                
    def measurement_time(self):
        self._fix_first_last_fixes()
        tot_time_hours = (self.timestamps[-1] - self.timestamps[0])/3600.
        tot_valid_time_hours = 0
        
        first_fixes = np.where(self.is_first_fix == 1)[0]
        last_fixes  = np.where(self.is_last_fix == 1)[0]
        
        for (start, last) in zip(first_fixes, last_fixes):
            tot_valid_time_hours += (self.timestamps[last] - self.timestamps[start])/3600.
            
        return tot_time_hours, tot_valid_time_hours, tot_time_hours-tot_valid_time_hours
    
    def mark_home(self, home_coords, radius):
        self.home_coords = home_coords
        self.is_home = np.zeros_like(self.timestamps)
        for i in np.arange(self.timestamps.shape[0]):
            fix = self._getFix(i)
            d = self.g.compute_distance_t(fix.coords, home_coords)
            if d < radius:
                self.is_home[i] = 1
                
    def mark_store(self, store_maps_coords, radius):
        self.store_maps_coords = store_maps_coords
        self.store_id     = -np.ones_like(self.timestamps)
        self.store_marker = -np.ones_like(self.timestamps)
        for i in np.arange(self.timestamps.shape[0]):
            fix = self._getFix(i)
            d = np.inf
            my_ci = None
            for store_id, data in store_maps_coords.items():
                ci = (data[0], data[1])
                marker = data[2]
                di = (fix.coords[0]-ci[0])**2+(fix.coords[1]-ci[1])**2#self.g.compute_distance_t(fix.coords, ci)
                if di < d:
                    d = di
                    self.store_id[i] = store_id
                    self.store_marker[i] = marker
                    my_ci = ci
                    
            d = self.g.compute_distance_t(fix.coords, my_ci)
            if d > radius:
                self.store_id[i]     = -1
                self.store_marker[i] = -1
            

            
        
    def trip_detection(self, trip_parameters):
                
        first_fixes = np.where(self.is_first_fix == 1)[0]
        last_fixes  = np.where(self.is_last_fix == 1)[0]
        if first_fixes.shape[0] != last_fixes.shape[0]:
            print("Error:", first_fixes.shape[0], last_fixes.shape[0])
            raise
        
        self.state       = -np.ones_like(self.timestamps, dtype=np.int)
        self.trip_marker = -np.ones_like(self.timestamps, dtype=np.int)
        
        assert len(self.trips) == 0
                
        for i in np.arange(first_fixes.shape[0]):
            self._define_state(first_fixes[i], last_fixes[i]+1, trip_parameters)
            
        if np.any(self.state==-1):
            print(first_fixes)
            print(np.where(self.state==-1))
            raise
            
        for i in np.arange(first_fixes.shape[0]):
            self._trip_detection(first_fixes[i], last_fixes[i]+1, trip_parameters)
            
        print( "Detected {0} trips".format(len(self.trips)) )
        
        for trip in self.trips:
            self.trip_marker[trip.start_index:trip.end_index+1] = trip.id

                
            
    def classify_trip(self, parameters_speed_cutoff):
        type_count = {}
        for k in parameters_speed_cutoff.keys():
            type_count[k] = 0
            
        for trip in self.trips:
            trip.classify(parameters_speed_cutoff)
            type_count[trip.type] += 1
            
        for k in type_count:
            print(type_count[k], " trips of type ", k)
        
        self.trip_type =  -np.ones_like(self.timestamps, dtype=np.int)
        for trip in self.trips:
            if trip.type=='slow_walk':
                self.trip_type[trip.start_index:trip.end_index+1] = 0
            if trip.type=='walk':
                self.trip_type[trip.start_index:trip.end_index+1] = 1
            elif trip.type=='bike':
                self.trip_type[trip.start_index:trip.end_index+1] = 2
            elif trip.type=='vehicle':
                self.trip_type[trip.start_index:trip.end_index+1] = 3
            
            
    def _trap_points(self, loc_param):
        if False:
            self.state[np.logical_and(self.trip_marker==-1, self.state==self.MOTION) ] = self.MOTION_NOT_TRIP
            store_start = None
            for i in np.arange(1, self.state.shape[0]):
                if self.state[i-1] == self.STATIONARY and self.state[i] == self.MOTION_NOT_TRIP:
                    store_start = i
                if self.state[i-1] == self.MOTION_NOT_TRIP and self.state[i] == self.STATIONARY:
                    if store_start:
                        dist = self.get_distance(i, store_start-1)
                        if dist < loc_param['radius']:
                            self.state[store_start:i] = self.STATIONARY
                            self._log("Change to stationary: ", store_start, i)
                    
            self.state[self.state == self.MOTION_NOT_TRIP] = self.MOTION
        else:
            self.state[np.logical_and(self.trip_marker==-1, self.is_valid)] = self.STATIONARY
            
    
    def location_detection(self, loc_param):
        assert self.trip_marker is not None
        
        self._trap_points(loc_param)
        
        first_fixes = self.is_first_fix.nonzero()[0]
        last_fixes  = self.is_last_fix.nonzero()[0]
        
        self.location_marker = -np.ones_like(self.timestamps, dtype=np.int)
        self.visit_marker = -np.ones_like(self.timestamps, dtype=np.int)
        assert len(self.locations) == 0
        
        assert len(self.visits) == 0
                
        for i in np.arange(first_fixes.shape[0]):
            self._detect_visits(first_fixes[i], last_fixes[i]+1, loc_param, self.visits)
        
        print( "Detected {0} visits".format(len(self.visits)) )
        
        self._merge_visits_into_locations(self.visits, loc_param["radius"])
           
        print( "Detected {0} locations".format(len(self.locations)) )
        
        for location in self.locations:
            for (f,l,visitid) in zip(location.first_indexes, location.stops, location.visit_ids):
                self.location_marker[f:l] = location.id
                self.visit_marker[f:l]    = visitid
            
    def _getFix(self, i):
        if i < self.timestamps.shape[0]:
            return Fix(self.timestamps[i], (self.latitudes[i], self.longitudes[i]), self.elevations[i], i)
        else:
            return None
            
    def _get1MinBeforeFix(self,i, start):
        curr_time = self.timestamps[i]
        for j in np.arange(i-1, start, -1):
            j_time = self.timestamps[j]
            if curr_time - j_time > 60:
                return self._getFix(j)
            
        return self._getFix(start)
            
    def _define_state(self, start, stop, trip_parameters):
      
        min_dist = trip_parameters["min_dist"]
        
        possible_pause = False
        possible_pause_start_index = start
        
        self.state[start] = self.STATIONARY
        
        for i in np.arange(start+1,stop):
            prev_fix = self._get1MinBeforeFix(i, start)
            cur_fix = self._getFix(i)
            dist = self.g.compute_distance_t(prev_fix.coords, cur_fix.coords)
            
            if dist > min_dist:
                self.state[i] = self.MOTION
                if self.state[i-1] == self.STATIONARY and possible_pause:
                    stop_len = cur_fix.tstmp - self.timestamps[possible_pause_start_index]
                    possible_pause = False
                    if stop_len < trip_parameters["min_pause"]:
                        self.state[possible_pause_start_index:i] = self.MOTION
                    elif stop_len < trip_parameters["max_pause"]:
                        self.state[possible_pause_start_index:i] = self.PAUSE
                    else:
                        self.state[possible_pause_start_index:i] = self.STATIONARY
            else:
                self.state[i] = self.STATIONARY
                if self.state[i-1] == self.MOTION:
                    possible_pause = True
                    possible_pause_start_index = i
                    
        if self.state[start+1] == self.MOTION:
            self.state[start] = self.MOTION
                    
    def _trip_detection(self,start, stop, trip_parameters):
        
        self._log("_trip_detection", start, " ", stop)
        trip_start = None
        
        if self.state[start] == self.MOTION:
            trip_start = start
            
        self._log("Trip start: ", trip_start)
        
        for i in np.arange(start+1,stop):
            if self.state[i] == self.MOTION and self.state[i-1] == self.STATIONARY:
                assert trip_start is None
                trip_start = i-1
                self._log("Trip start: ", trip_start)
            elif self.state[i] == self.STATIONARY and self.state[i-1] == self.MOTION:
                self._log("Trip end: ", i)
                trip = self._validateTrip(trip_start, i, trip_parameters)
                trip_start = None
                if trip:
                    self.trips.append( trip )

            elif self.state[i] == self.STATIONARY and self.state[i-1] == self.PAUSE:
                print("Error going from PAUSE to STATIONARY is forbidden")
                raise
            elif self.state[i] == self.PAUSE and self.state[i-1] == self.STATIONARY:
                print("Error going from STATIONARY to PAUSE is forbidden")
                raise
            
        if trip_start is not None:
            self._log("Trip end at end of fix: ", i)
            trip = self._validateTrip(trip_start, stop-1, trip_parameters)
            if trip:
                self.trips.append( trip )
            
    def _validateTrip(self, start, end, trip_parameters):
        
        self._log("_validateTrip", start, " ", end)
        
        incomplete_data = self.is_first_fix[start] or self.is_last_fix[end]
                
        success =  False
        for i in np.arange(start,end):
            my_d = self.get_distance(i+1, start)
            if my_d > trip_parameters["radius"]:
                success = True
                break
            
        if not success and not incomplete_data:
            self._log("From start = {0} to end = {1} the diameter only {2} meters".format(start, end, my_d))
            return None
        
        if not success and incomplete_data:
            self._log("From start = {0} to end = {1} the diameter only {2} meters. Incomplete trip".format(start, end, my_d))
            self.is_valid[start:end] =  0
            return None
        
        duration = self.timestamps[end] - self.timestamps[start]
        distance = self.cumdist[end] - self.cumdist[start]
        trip_is_valid = True
        
        if duration < trip_parameters["min_dur"] and not incomplete_data:
            self._log("From start = {0} to end = {1} is only {2} seconds".format(start, end, duration))
            trip_is_valid = False
            return None
        
        if duration < trip_parameters["min_dur"] and incomplete_data:
            self._log("From start = {0} to end = {1} is only {2} seconds.  Incomplete trip".format(start, end, duration))
            self.is_valid[start:end] =  0
            return None
        
        if distance < trip_parameters["min_length"] and not incomplete_data:
            self._log("From start = {0} to end = {1} the distance traveled is only {2} meters".format(start, end, distance))
            trip_is_valid = False
            return None
        
        if distance < trip_parameters["min_length"] and incomplete_data:
            self._log("From start = {0} to end = {1} the distance traveled is only {2} meters. Incomplete trip".format(start, end, distance))
            self.is_valid[start:end] =  0
            return None
            
        speedAvg = np.mean(self.speeds[start:end+1])
        maxSpeedIndex = np.argmax(self.speeds[start:end+1])
        if maxSpeedIndex == 0:
            speedMax = self.speeds[start + 1]
        elif maxSpeedIndex == end-start:
            speedMax = self.speeds[end - 1]
        else:
            speedMax = .5*(self.speeds[start + maxSpeedIndex + 1] + self.speeds[start + maxSpeedIndex - 1])
        
        
        if speedAvg < trip_parameters["min_avg_speed"] and not incomplete_data:
            self._log("From start = {0} to end = {1} the average speed is only {2} km/hours".format(start, end, speedAvg))
            trip_is_valid = False
            return None
        
        if speedAvg < trip_parameters["min_avg_speed"] and incomplete_data:
            self._log("From start = {0} to end = {1} the average speed is only {2} km/hours. Incomplete trip".format(start, end, speedAvg))
            trip_is_valid = False
            self.is_valid[start:end] =  0
            return None

        
        id = self.tripCounter
        self.tripCounter += 1
        trip = Trip(id, start, end,duration, distance, trip_is_valid)
        
        trip.crowdist = self.g.compute_distance(self.latitudes[start], self.longitudes[start],
                                                self.latitudes[end],   self.longitudes[end]    )
        
        trip.radius = trip.crowdist
        for i in np.arange(start+1, end):
            d1 = self.g.compute_distance(self.latitudes[start], self.longitudes[start],
                                                self.latitudes[i], self.longitudes[i] )
            
            d2 = self.g.compute_distance(self.latitudes[i], self.longitudes[i],
                                         self.latitudes[end], self.longitudes[end] )
            
            trip.radius = max(trip.radius, d1, d2)
            
        trip.speedRMax = speedMax
        
        trip.speedAvg = speedAvg
        
        return trip
        
    def _detect_visits(self, start, stop, location_parameters, visits):
                      
        if self.state[start] == self.STATIONARY:
            location_start = start
        elif self.state[start] == self.MOTION:
            location_start = None
        else:
            raise
        
        if location_parameters["pause"]:
            for i in np.arange(start+1,stop):
                if self.state[i] in [self.STATIONARY, self.PAUSE] and self.state[i-1] in [self.MOTION]:
                    assert location_start is None
                    location_start = i
                elif self.state[i] == self.MOTION and self.state[i-1] in [self.STATIONARY, self.PAUSE]:
                    visit = self._isVisit(location_start, i, location_parameters)
                    location_start = None
                    if visit:
                        visits.append( visit )               
        else:
            for i in np.arange(start+1,stop):
                if self.state[i] in [self.STATIONARY] and self.state[i-1] == self.MOTION:
                    assert location_start is None
                    location_start = i
                elif self.state[i] == self.MOTION and self.state[i-1] in [self.STATIONARY]:
                    visit = self._isVisit(location_start, i, location_parameters)
                    location_start = None
                    if visit:
                        visits.append( visit )
        
        if location_start is not None:
            visit = self._isVisit(location_start, stop, location_parameters)
            if visit:
                visits.append( visit )
                    
    def _isVisit(self, start_index, stop, location_parameters):
        
        if(start_index > stop):
            print("Start index: ", start_index, "Last index: ", stop)
            raise
        
        if self.timestamps[stop-1] < self.timestamps[start_index]:
            print("Start index time: ", self.local_datetime[start_index], start_index)
            print("End index time: ", self.local_datetime[stop-1], stop-1)
        
        incomplete_data = self.is_first_fix[start_index] or self.is_last_fix[stop-1]
        
        duration = self.timestamps[stop-1] - self.timestamps[start_index]

        is_pause = np.all(self.state[start_index:stop] > self.STATIONARY)
        
        if is_pause:
            self._log("Detected pause between {0} and {1} of length {2}".format(start_index, stop, duration))
            
        if duration < location_parameters["min_time"] and is_pause:
            return None
        
        visit_is_valid = True
        if duration < location_parameters["min_time"] and not incomplete_data:
            visit_is_valid = False
            self._log("_isVisit start {0} end {1} duration {2} incomplete data {3}: ".format( 
                  start_index, stop, duration, incomplete_data))
            
        if duration < location_parameters["min_time"] and incomplete_data:
            self.is_valid[start_index:stop] = 0
            return
            
        if duration < 1.:
            duration = 1.
        
        lats = self.latitudes[start_index:stop]
        lons = self.longitudes[start_index:stop]
        cm_lat = np.mean( lats )
        cm_lon = np.mean( lons )
        
        radius = max([self.g.compute_distance(lat, lon, cm_lat, cm_lon) for (lat,lon) in zip(lats, lons) ] )
        if (radius <= location_parameters["radius"]) or True:
            cl = Visit(self.visitCounter, cm_lat, cm_lon, radius, duration, start_index, stop)
            cl.is_valid = visit_is_valid
            cl.distanceFromHome(self)
            cl.distanceFromStore(self)
            self.visitCounter+=1
            return cl
        else:
            if self.g.compute_distance(lats[0], lons[0], cm_lat, cm_lon) > self.g.compute_distance(lats[-1], lons[-1], cm_lat, cm_lon):
                return self._isVisit(start_index+1, stop, location_parameters)
            else:
                return self._isVisit(start_index, stop-1, location_parameters)
            
            
    def _merge_visits_into_locations(self, visits, radius):
        assert len(self.locations) == 0
        
        locationAlreadyVisited = False
        for visit in visits:
            for loc in self.locations:
                locationAlreadyVisited = loc.merge(visit,self,radius)
                if locationAlreadyVisited:
                    break
            if not locationAlreadyVisited:
                self.locations.append(Location(self.locationCounter, visit, self))
                self.locationCounter+=1
                
                
    def get_distance(self,i,j):
        fix_i = self._getFix(i)
        fix_j = self._getFix(j)
        
        return self.g.compute_distance_t(fix_i.coords, fix_j.coords) 

    def _log(self, *args):
        if self.logging:
            print(*args)
            
    def _fix_first_last_fixes(self):
        for i in np.arange(self.is_first_fix.shape[0]-1):
            if self.is_first_fix[i]==1 and self.is_valid[i] == 0:
                self.is_first_fix[i]   = 0
                self.is_first_fix[i+1] = 1
                
        for i in np.arange(self.is_last_fix.shape[0]-1, 1, -1):
            if self.is_last_fix[i]==1 and self.is_valid[i] == 0:
                self.is_last_fix[i] = 0
                self.is_last_fix[i-1] = 1

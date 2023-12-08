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
from .fix import Fix
from .commuteTrip import CommuteTrip
from .distance import GeodesicDistance
from ..common.conversions import meter_per_second_to_km_per_hour,\
    km_per_hour_to_meter_per_second
    
        
class CommuteGPSData:
    
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
        
        self.state                   = None
        self.trip_marker             = None
        self.trip_type               = None
        self.trip_outbound_inbound   = None #indbound is 1 if home to dest (outbound); 2 if dest to home; 0 no commute trip
        self.tripCounter             = 0

        
        self.is_valid        = None
        
        self.trips = []
        
        self.is_home = None
        self.is_dest = None
        
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
    
    def mark_home(self, aoi):
        self.home = aoi
        self.is_home = aoi.is_within(self.latitudes, self.longitudes)

                
    def mark_dest(self, aoi):
        self.dest = aoi
        self.is_dest = aoi.is_within(self.latitudes, self.longitudes)

    def trip_detection(self, trip_parameters):
                
        first_fixes = np.where(self.is_first_fix == 1)[0]
        last_fixes  = np.where(self.is_last_fix == 1)[0]
        if first_fixes.shape[0] != last_fixes.shape[0]:
            print("Error:", first_fixes.shape[0], last_fixes.shape[0])
            raise
        
        self.state                 = -np.ones_like(self.timestamps, dtype=np.int)
        self.trip_marker           = -np.ones_like(self.timestamps, dtype=np.int)
        self.trip_outbound_inbound = -np.ones_like(self.timestamps, dtype=np.int)
        
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
            self.trip_marker[trip.start_index:trip.last_index+1] = trip.id
            self.trip_outbound_inbound[trip.start_index:trip.last_index+1] = trip.Outbound_Inbound(self)

        print( "Detected {0} outbound trips".format( np.sum([trip.Outbound_Inbound(self)==1 for trip in self.trips])) )
        print( "Detected {0} inbound trips".format( np.sum([trip.Outbound_Inbound(self)==2 for trip in self.trips])) )

                
            
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
                self.trip_type[trip.start_index:trip.last_index+1] = 0
            if trip.type=='walk':
                self.trip_type[trip.start_index:trip.last_index+1] = 1
            elif trip.type=='bike':
                self.trip_type[trip.start_index:trip.last_index+1] = 2
            elif trip.type=='vehicle':
                self.trip_type[trip.start_index:trip.last_index+1] = 3
            
            
    def _trap_points(self, loc_param):
        self.state[np.logical_and(self.trip_marker==-1, self.is_valid)] = self.STATIONARY
            
               
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
        trip = CommuteTrip(id, start, end,duration, distance, trip_is_valid)
        
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

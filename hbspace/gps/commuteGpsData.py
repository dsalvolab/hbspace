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
import skimage

from .fix import Fix
from .enum import GPSState, TripDirection
from .commuteTrip import CommuteTrip
from .distance import GeodesicDistance
from ..common.conversions import meter_per_second_to_km_per_hour,\
    km_per_hour_to_meter_per_second
    

class CommuteGPSData:
    
    def __init__(self, id, fname, proj=None):
        
        self.g = GeodesicDistance()
        self.proj = proj
        
        self.id = id
        self.fname = fname
        
        self.utc_timestamps = None
        self.local_timestamps = None
        self.utc_datetime = None
        self.local_datetime = None
        self.latitudes      = None
        self.longitudes     = None
        self.elevations     = None
        self.is_first_fix   = None
        self.is_last_fix    = None
        
        self.ntotal_fixes   = None
        
        self.speeds      = None
        self.cumdist     = None
        
        self.state                   = None

        self.tripCounter             = 0    
        self.trips = []
        
        self.is_home = None
        self.is_dest = None

        self.home = None
        self.dest = None
        
        self.unordered_source = False
        self.logging = False
        
        
    def compute_dist(self):        
        self.speeds      = np.zeros_like(self.utc_timestamps)
        self.cumdist     = np.zeros_like(self.utc_timestamps)
        
        prev_time    = None
        prev_coords  = None
        rundist     =  0
        
        for i in np.arange(self.utc_timestamps.shape[0]):
            if self.is_first_fix[i]:
                prev_coords  = (self.latitudes[i], self.longitudes[i])
                prev_time    = self.utc_timestamps[i]
                rundist      = 0
                self.cumdist[i]  = 0
                
                next_coords = (self.latitudes[i+1], self.longitudes[i+1])
                next_time  = self.utc_timestamps[i+1]
                
                d =  self.g.compute_distance_t(prev_coords, next_coords)
                
                self.speeds[i]   =  meter_per_second_to_km_per_hour( d/(next_time - prev_time) )
            else:
                cur_coords = (self.latitudes[i], self.longitudes[i])
                cur_time   = self.utc_timestamps[i]
                
                cur_dist   = self.g.compute_distance_t(prev_coords, cur_coords)
                
                assert np.isnan(cur_dist)==False 
                
                rundist += cur_dist
                self.cumdist[i] = rundist
                self.speeds[i]  = meter_per_second_to_km_per_hour( cur_dist / (cur_time - prev_time) )
                
                prev_coords = cur_coords
                prev_time   = cur_time
                
    def measurement_time(self):
        tot_time_hours = (self.utc_timestamps[-1] - self.utc_timestamps[0])/3600.
        tot_valid_time_hours = 0
        
        first_fixes = np.where(self.is_first_fix == 1)[0]
        last_fixes  = np.where(self.is_last_fix == 1)[0]
        
        for (start, last) in zip(first_fixes, last_fixes):
            tot_valid_time_hours += (self.utc_timestamps[last] - self.utc_timestamps[start])/3600.
            
        return tot_time_hours, tot_valid_time_hours, tot_time_hours-tot_valid_time_hours
    
    def mark_home(self, aoi):
        self.home = aoi
        self.is_home = aoi.is_within(self.latitudes, self.longitudes)

                
    def mark_dest(self, aoi):
        self.dest = aoi
        self.is_dest = aoi.is_within(self.latitudes, self.longitudes)

    def estimate_trips(self, days, tois):
        estimated_number_of_trips = np.zeros(2, dtype=np.int)
        for d in days:
            estimated_number_of_trips = estimated_number_of_trips + self._estimate_trips(d, tois)

        return estimated_number_of_trips
    
    def _estimate_trips(self, day, tois):
        local_date = np.array([local_dt.date() for local_dt in self.local_datetime])
        indexes = (local_date == day)
        assert( np.sum(indexes) > 0 )
        day_local_dt = self.local_datetime[indexes]
        day_is_home  = self.is_home[indexes]
        day_is_dest  = self.is_dest[indexes]

        hits_percent = {}
        total_fixes  = {}

        hits_percent["at_home_night"], total_fixes["at_home_night"] = self._count_hits_in_tois(day_local_dt, day_is_home, tois["at_home_night"])
        hits_percent["at_school_am"], total_fixes["at_school_am"] = self._count_hits_in_tois(day_local_dt, day_is_dest, tois["at_school_am"])
        hits_percent["at_school_pm"], total_fixes["at_school_pm"] = self._count_hits_in_tois(day_local_dt, day_is_dest, tois["at_school_pm"])

        est_number_trip = np.zeros(2, dtype=np.int)
        if hits_percent["at_home_night"] > 0.1 and hits_percent["at_school_am"] > 0.1:
            est_number_trip[0] = 1

        if  hits_percent["at_school_pm"] > 0.1:
            est_number_trip[1] = 1

        return est_number_trip


    def _count_hits_in_tois(self,day_local_dt, day_marker, toi):
        hits = 0
        misses = 0
        for i, dt in enumerate(day_local_dt):
            if toi.contains(dt):
                if day_marker[i]:
                    hits = hits+1
                else:
                    misses = misses + 1

        total_fixes = hits+misses
        if total_fixes > 0:
            hits_percent = float(hits)/float(total_fixes)
        else:
            hits_percent = 0.

        return hits_percent, total_fixes
    
    def detect_motion(self, trip_parameters):
        first_fixes = np.where(self.is_first_fix == 1)[0]
        last_fixes  = np.where(self.is_last_fix == 1)[0]
        if first_fixes.shape[0] != last_fixes.shape[0]:
            print("Error:", first_fixes.shape[0], last_fixes.shape[0])
            raise
        
        self.state = -np.ones_like(self.utc_timestamps, dtype=np.int)

        for i in np.arange(first_fixes.shape[0]):
            self._define_state(first_fixes[i], last_fixes[i]+1, trip_parameters)
            
        if np.any(self.state==-1):
            print(first_fixes)
            print(np.where(self.state==-1))
            raise

        self._trapHomeDest()
    
    def find_home2dest_trips(self, days, tois):

        if self.state is None:
            print("You must call self.detect_motion first")
            raise

        trip_count = 0
        for d in days:
            trip =  self._find_home2dest_trip(d, tois)
            if trip:
                self.trips.append(trip)
                trip_count = trip_count+1

        return trip_count

    def find_dest2x_trips(self, days, tois):

        if self.state is None:
            print("You must call self.detect_motion first")
            raise

        trip_count = 0
        for d in days:
            trip =  self._find_dest2x_trip(d, tois)
            if trip:
                self.trips.append(trip)
                trip_count = trip_count+1

        return trip_count

    def _find_home2dest_trip(self, day, tois):
        # Step 1: Check the rules to determine if a trip should exists
        local_date = np.array([local_dt.date() for local_dt in self.local_datetime])
        indexes = (local_date == day)
        assert( np.sum(indexes) > 0 )
        day_local_dt = self.local_datetime[indexes]
        day_is_home  = self.is_home[indexes]
        day_is_dest  = self.is_dest[indexes]

        hits_percent = {}
        total_fixes  = {}

        hits_percent["at_home_night"], total_fixes["at_home_night"] = self._count_hits_in_tois(day_local_dt, day_is_home, tois["at_home_night"])
        hits_percent["at_school_am"], total_fixes["at_school_am"] = self._count_hits_in_tois(day_local_dt, day_is_dest, tois["at_school_am"])

        if hits_percent["at_home_night"] > 0.1 and hits_percent["at_school_am"] > 0.1:
            pass
        else:
            return None
        
        # Step 2: A trip should exists. Select when the window to find a trip starts and ends.
        
        tripwindow_day_indexes = tois['trip_h2s'].get_indexes(day_local_dt)
        if np.any(tripwindow_day_indexes) == False:
            return None
        trip_window_starts = np.min( day_local_dt[tripwindow_day_indexes] )
        trip_window_ends   = np.max( day_local_dt[tripwindow_day_indexes] )
        print("Searching for h2s trip in time window: ", trip_window_starts, " ", trip_window_ends)

        # Step 3: this are the indexes of the trip window
        trip_window_indexes = np.logical_and(self.local_datetime >= trip_window_starts, 
                                             self.local_datetime <= trip_window_ends).astype(int)
        # Find the last fix home and first fix at school within the window
        is_home_in_window_indexes = np.nonzero(self.is_home*trip_window_indexes)[0]
        if is_home_in_window_indexes.shape[0] == 0:
            return None
        trip_start_index = is_home_in_window_indexes[-1]
        is_dest_in_window_indexes = np.nonzero(self.is_dest*trip_window_indexes)[0]
        if is_dest_in_window_indexes.shape[0]==0:
            return None
        trip_last_index = is_dest_in_window_indexes[0]
        print("Last fix at home: ", self.local_datetime[trip_start_index])
        print("First fix at school:  ", self.local_datetime[trip_last_index])
        assert self.local_datetime[trip_start_index] < self.local_datetime[trip_last_index]
        # Extend the window based on the state (MOTION vs STATIONARY vs PAUSE) up to 2 minutes
        original_time = self.local_datetime[trip_start_index]
        self.state[trip_start_index] = GPSState.MOTION
        while self.state[trip_start_index-1] != GPSState.STATIONARY:
            new_time = self.local_datetime[trip_start_index-1]
            assert (original_time - new_time).total_seconds() >= 0.
            if (original_time - new_time).total_seconds() > 120:
                break
            trip_start_index = trip_start_index - 1
            if trip_start_index == 0:
                break
        while self.state[trip_start_index+1] != GPSState.MOTION: 
            trip_start_index = trip_start_index + 1
            if trip_start_index == self.state.shape[0]-1:
                break

        original_time = self.local_datetime[trip_last_index]
        while self.state[trip_last_index+1] != GPSState.STATIONARY:
            new_time = self.local_datetime[trip_last_index+1]
            assert (new_time - original_time).total_seconds() >= 0.
            if(new_time - original_time).total_seconds() > 120:
                break
            trip_last_index = trip_last_index + 1
            if trip_last_index == self.state.shape[0]-1:
                 break
            
        while self.state[trip_last_index] != GPSState.MOTION:
            trip_last_index = trip_last_index - 1
            if trip_last_index == 0:
                break

        trip_end_index = trip_last_index+1
        print("h2s trip detected between: ", self.local_datetime[trip_start_index],
                                             " and ", 
                                              self.local_datetime[trip_last_index])
        assert self.local_datetime[trip_start_index] < self.local_datetime[trip_last_index]

        trip = CommuteTrip(partid = self.id,
                           id=self.tripCounter, start_index=trip_start_index,
                           end_index=trip_end_index, direction=TripDirection.H2D)
        
        trip.computeInfoFromGPS(self)
        self.tripCounter = self.tripCounter+1

        return trip
    
    def _find_dest2x_trip(self, day, tois):
        # Step 1: Check the rules to determine if a trip should exists
        local_date = np.array([local_dt.date() for local_dt in self.local_datetime])
        indexes = (local_date == day)
        assert( np.sum(indexes) > 0 )
        day_local_dt = self.local_datetime[indexes]
        day_is_dest  = self.is_dest[indexes]

        hits_percent = {}
        total_fixes  = {}

        hits_percent["at_school_pm"], total_fixes["at_school_pm"] = self._count_hits_in_tois(day_local_dt, day_is_dest, tois["at_school_pm"])

        if  hits_percent["at_school_pm"] > 0.1:
            pass
        else:
            return None
        
        # Step 2: A trip should exists. Select when the window to find a trip starts and ends.
        
        tripwindow_day_indexes = tois['trip_s2x'].get_indexes(day_local_dt)
        if np.any(tripwindow_day_indexes) == False:
            return None
        trip_window_starts = np.min( day_local_dt[tripwindow_day_indexes] )
        trip_window_ends   = np.max( day_local_dt[tripwindow_day_indexes] )
        print("Searching for s2x trip in time window: ", trip_window_starts, " ", trip_window_ends)

        # Step 3: this are the indexes of the trip window
        trip_window_indexes = np.logical_and(self.local_datetime >= trip_window_starts, 
                                             self.local_datetime <= trip_window_ends).astype(int)
        # Find the last fix school
        is_dest_in_window_indexes = np.nonzero(self.is_dest*trip_window_indexes)[0]
        if is_dest_in_window_indexes.shape[0] == 0:
            return None
        trip_start_index = is_dest_in_window_indexes[-1]
        print("Last fix at school: ", self.local_datetime[trip_start_index])

        # Extend the window based on the state (MOTION vs STATIONARY vs PAUSE) up to 2 minutes
        original_time = self.local_datetime[trip_start_index]
        self.state[trip_start_index] = GPSState.MOTION
        while self.state[trip_start_index-1] != GPSState.STATIONARY:
            new_time = self.local_datetime[trip_start_index-1]
            assert (original_time - new_time).total_seconds() >= 0.
            if (original_time - new_time).total_seconds() > 120:
                break
            trip_start_index = trip_start_index - 1
            if trip_start_index == 0:
                break
        while self.state[trip_start_index+1] != GPSState.MOTION: 
            trip_start_index = trip_start_index + 1
            if trip_start_index == self.state.shape[0]-1:
                break

        if trip_start_index == self.state.shape[0]-1:
            return None

        trip_last_index = trip_start_index
        while self.state[trip_last_index+1] != GPSState.STATIONARY:
            trip_last_index = trip_last_index + 1
            if trip_last_index == self.state.shape[0]-1:
                break
        while self.state[trip_last_index] != GPSState.MOTION:
            trip_last_index = trip_last_index - 1
            if trip_last_index == 0:
                break
        trip_end_index = trip_last_index + 1

        print("d2x trip detected between: ", self.local_datetime[trip_start_index],
                                             " and ", 
                                              self.local_datetime[trip_last_index])
        print("Number of fixes in trip: ", trip_end_index-trip_start_index)
        assert self.local_datetime[trip_start_index] < self.local_datetime[trip_last_index]

        trip_direction = TripDirection.D2X
        if self.is_home[trip_last_index]:
            trip_direction = TripDirection.D2H
        if trip_end_index < self.is_home.shape[0] and self.is_home[trip_end_index]:
            trip_direction = TripDirection.D2H

        trip = CommuteTrip(partid = self.id,
                           id=self.tripCounter, start_index=trip_start_index,
                           end_index=trip_end_index, direction=trip_direction)
        
        trip.computeInfoFromGPS(self)
        self.tripCounter = self.tripCounter+1

        return trip


    def findLocation(self,days, toi):
        out = []
        for day in days:
            out_i = self._findLocation(day, toi)
            if out_i is not None:
                out.append(out_i)

        return out

    def _findLocation(self, day, toi):
        local_date = np.array([local_dt.date() for local_dt in self.local_datetime])
        indexes = (local_date == day)
        if np.sum(indexes) == 0:
            return None
        
        local_dt = self.local_datetime[indexes]
        is_home  = self.is_home[indexes]
        is_dest  = self.is_dest[indexes]
        lat      = self.latitudes[indexes]
        lon      = self.longitudes[indexes]

        window_indexes = toi.get_indexes(local_dt)
        if np.sum(window_indexes) == 0:
            return None
        window_is_home = is_home[window_indexes]
        window_is_dest = is_dest[window_indexes]
        window_lat     = lat[window_indexes]
        window_lon     = lon[window_indexes]

        out = {}
        out['part_id'] = self.id
        out['school_id'] = self.dest.name
        out['date'] = day.strftime('%Y-%m-%d')
        if np.mean(window_is_home) > 0.1 and np.mean(window_is_home) > np.mean(window_is_dest):
            #I am at home
            out['lat'] = self.home.lat
            out['lon'] = self.home.lon
            out['is_home'] = 1
            out['is_school'] = 0
            out['distance_from_home'] = 0.
            out['distance_from_school'] = self.g.compute_distance(self.home.lat, self.home.lon,
                                                                  self.dest.lat, self.dest.lon)
        elif np.mean(window_is_dest) > 0.1:
            #I am at destination
            out['lat'] = self.dest.lat
            out['lon'] = self.dest.lon
            out['is_home'] = 0
            out['is_school'] = 1
            out['distance_from_home'] = self.g.compute_distance(self.home.lat, self.home.lon,
                                                                  self.dest.lat, self.dest.lon)
            out['distance_from_school'] = 0.
        else:
            #I am elsewhere
            mylat = np.mean(window_lat)
            mylon = np.mean(window_lon)
            print("Mean lat = ", mylat)
            print("Mean lon = ", mylon)
            out['lat'] = mylat
            out['lon'] = mylon
            out['is_home'] = 0
            out['is_school'] = 0
            out['distance_from_home'] = self.g.compute_distance(self.home.lat, self.home.lon,
                                                                  mylat, mylon)
            out['distance_from_school'] = self.g.compute_distance(mylat, mylon,
                                                                  self.dest.lat, self.dest.lon)


        return out
    



  
                
            
    def classify_trip(self, parameters_speed_cutoff):
        type_count = {}
        for k in parameters_speed_cutoff.keys():
            type_count[k] = 0
            
        for trip in self.trips:
            trip.classify(parameters_speed_cutoff)
            type_count[trip.type] += 1
            
        for k in type_count:
            print(type_count[k], " trips of type ", k)
        
        self.trip_type =  -np.ones_like(self.utc_timestamps, dtype=np.int)
        for trip in self.trips:
            if trip.type=='slow_walk':
                self.trip_type[trip.start_index:trip.last_index+1] = 0
            if trip.type=='walk':
                self.trip_type[trip.start_index:trip.last_index+1] = 1
            elif trip.type=='bike':
                self.trip_type[trip.start_index:trip.last_index+1] = 2
            elif trip.type=='vehicle':
                self.trip_type[trip.start_index:trip.last_index+1] = 3
            
            
    def _trapHomeDest(self):
        is_stationary =  self.state==GPSState.STATIONARY
        first_fixes = self.is_first_fix.nonzero()[0]
        last_fixes  = self.is_last_fix.nonzero()[0]

        for i in np.arange(first_fixes.shape[0]):
            is_stat = is_stationary[first_fixes[i]:last_fixes[i]+1]
            stays, nstays = skimage.measure.label(is_stat, return_num=True)
            for stay_index in np.arange(1,nstays+1):
                indexes = first_fixes[i] + np.where(stays==stay_index)[0]
                nfix = np.sum(stays==stay_index)
                xhomefix = np.sum(self.is_home[indexes])
                if xhomefix / nfix  > 0.4:
                    self.is_home[indexes] = 1

                xdestfix = np.sum(self.is_dest[indexes])
                if xdestfix / nfix  > 0.4:
                    self.is_dest[indexes] = 1


               
    def _getFix(self, i):
        if i < self.utc_timestamps.shape[0]:
            return Fix(self.utc_timestamps[i], (self.latitudes[i], self.longitudes[i]), self.elevations[i], i)
        else:
            return None
            
    def _get1MinBeforeFix(self,i, start):
        curr_time = self.utc_timestamps[i]
        for j in np.arange(i-1, start, -1):
            j_time = self.utc_timestamps[j]
            if curr_time - j_time > 60:
                return self._getFix(j)
            
        return self._getFix(start)
            
    def _define_state(self, start, stop, trip_parameters):
      
        min_dist = trip_parameters["min_dist"]
        
        possible_pause = False
        possible_pause_start_index = start
        
        self.state[start] = GPSState.STATIONARY
        
        for i in np.arange(start+1,stop):
            prev_fix = self._get1MinBeforeFix(i, start)
            cur_fix = self._getFix(i)
            dist = self.g.compute_distance_t(prev_fix.coords, cur_fix.coords)
            
            if dist > min_dist:
                self.state[i] = GPSState.MOTION
                if self.state[i-1] == GPSState.STATIONARY and possible_pause:
                    stop_len = cur_fix.tstmp - self.utc_timestamps[possible_pause_start_index]
                    possible_pause = False
                    if stop_len < trip_parameters["min_pause"]:
                        self.state[possible_pause_start_index:i] = GPSState.MOTION
                    elif stop_len < trip_parameters["max_pause"]:
                        self.state[possible_pause_start_index:i] = GPSState.PAUSE
                    else:
                        self.state[possible_pause_start_index:i] = GPSState.STATIONARY
            else:
                self.state[i] = GPSState.STATIONARY
                if self.state[i-1] == GPSState.MOTION:
                    possible_pause = True
                    possible_pause_start_index = i
                    
        if self.state[start+1] == GPSState.MOTION:
            self.state[start] = GPSState.MOTION
                    
 
                     
    def get_distance(self,i,j):
        fix_i = self._getFix(i)
        fix_j = self._getFix(j)
        
        return self.g.compute_distance_t(fix_i.coords, fix_j.coords) 

    def _log(self, *args):
        if self.logging:
            print(*args)
            

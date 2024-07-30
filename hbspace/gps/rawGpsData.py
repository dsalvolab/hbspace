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

import os

import pandas
import numpy as np
from .distance import GeodesicDistance
from ..common.conversions import meter_per_second_to_km_per_hour,\
    km_per_hour_to_meter_per_second
    
from .fix import Fix

import datetime

def my_date_parser(strdate, strtime):
    assert hasattr(strdate, 'shape')
    out = np.empty(strdate.shape, dtype = datetime.datetime)
    for ii in np.arange(strdate.shape[0]):
        str_datetime = strdate[ii] + " " + strtime[ii]
        out_ii = None
        if ii == 0:
            print("[my_data_parser]: first date: ", str_datetime)
        try:
            out_ii = datetime.datetime.strptime(str_datetime, "%Y/%m/%d %H:%M:%S")
        except:
            try:
                out_ii = datetime.datetime.strptime(str_datetime, "%m/%d/%Y %H:%M:%S")
            except:
                out_ii = datetime.datetime.strptime(str_datetime, "%m%/%d/%y %H:%M:%S")

        if out_ii is not None:
            out[ii] = out_ii
        else:
            print("[my_date_paser]: Error in parsing ", str_datetime)
            raise

    
    return out
    

class RawGPSData:
    def __init__(self, fname, id=None, logging=False, years_of_collection = []):
        """
        Years of collection are needed to fix the GPS date roll over issue:
        https://en.wikipedia.org/wiki/GPS_week_number_rollover
        """
        self.logging = logging
        self.fname = fname
        self.years_of_collection = years_of_collection
        if id is None:
            self.id = os.path.splitext( os.path.basename(fname) )[0]
        else:
            self.id = id

        self.latitudes        = None
        self.longitudes       = None
        self.speeds           = None #"km/h"
        self.elevations       = None #"meters"
        self.headings         = None
        self.timestamps       = None
        self.local_timestamps = None
        self.local_datetime   = None
        self.utc_timestamps   = None
        self.utc_datetime     = None

        self.unordered_source = False

    def read_legacy(self, tryfix=True):
        colnames_1 = ['INDEX', 'TRACK_ID', 'VALID', 'UTC_DATE', 'UTC_TIME', 'LOCAL_DATE', 'LOCAL_TIME',
                    'MS',    'LATITUDE',   'N_S', 'LONGITUDE',     'E_W',   'ALTITUDE', 'SPEED',
                    'HEADING', 'G-X', 'G-Y', 'G-Z']
        
        colnames_2 = ['INDEX', 'RCR', 'UTC DATE', 'UTC TIME', 'LOCAL DATE', 'LOCAL TIME', 'MS', 'VALID', 
                      'LATITUDE', 'N_S', 'LONGITUDE', 'E_W', 'HEIGHT', 'SPEED', 'HEADING', 
                      'PDOP', 'HDOP', 'VDOP', 'NSAT(USED/VIEW)', 'SAT INFO (SID-ELE-AZI-SNR)']
        
        with open(self.fname, 'r') as fid:
            headers = fid.readline().split(",")
            if len(headers) == len(colnames_1):
                ftype = 1
            elif len(headers) == len(colnames_2):
                ftype = 2
            else:
                raise InputError()
        
        
        if ftype == 1:
            colnames = colnames_1
            parse_dates={"utc_datetime": [3,4], "local_datetime": [5,6]}
            print("Type 1")
        else:
            colnames = colnames_2
            parse_dates={"utc_datetime": [2,3], "local_datetime": [4,5]}
            print("Type 2")
            
        colnames = [name.lower() for name in colnames]
        data = pandas.read_csv(self.fname, names=colnames, parse_dates=parse_dates, date_parser=my_date_parser, header=0)

        self.setDatesTimeStamps(data)
        
        self.latitudes  = np.array([self._parselatitude(lat, n_s)
                                    for (lat, n_s) in zip(data.latitude, data.n_s)])
        self.longitudes  = np.array([self._parselongitude(lon, e_w) 
                                    for (lon, e_w) in zip(data.longitude, data.e_w) ])
        
        if ftype == 1:
            self.elevations = np.array(data.altitude.tolist() )
            self.speeds     = np.array(data.speed.tolist() )
        else:
            self.elevations = np.array( [float(elev[:-2]) for elev in data.height] )
            self.speeds     = np.array( [float(speed[:-5]) for speed in data.speed] )
        
        self.headings   = np.array(data.heading.tolist() )
        
        success = 0
        if tryfix:
            self._ensure_sorted()
            self._ensure_no_duplicates()
            success = 1
        else:
            success = self.isSorted()
        
        self.is_valid   = np.ones_like(self.utc_timestamps)
        
        self.is_first_fix = np.zeros_like(self.utc_timestamps)
        self.is_first_fix[0] = 1
        
        self.is_last_fix = np.zeros_like(self.utc_timestamps)
        self.is_last_fix[-1] = 1

        return success

    def read_fromQTravel(self, tryfix=True):
        colnames = ['INDEX', 'RCR', 'UTC DATE', 'UTC TIME', 'LOCAL DATE', 'LOCAL TIME',
                    'MS',   'VALID', 'LATITUDE',   'N/S', 'LONGITUDE',     'E/W', 
                    'HEIGHT', 'SPEED', 'HEADING',
                    'PDOP', 'HDOP', 'VDOP', 
                    'NSAT(USED/VIEW)', 'SAT INFO (SID-ELE-AZI-SNR)', 'DISTANCE']
        
        
        with open(self.fname, 'r') as fid:
            headers = [h.strip() for h in fid.readline().split(",")]
            if len(headers) != len(colnames):
                print(headers)
                return 0
            for h,c in zip(headers, colnames):
                if h != c:
                    print(headers)
                    return 0
        
        parse_dates={"utc_datetime": [2,3], "local_datetime": [4,5]}

            
        colnames = [name.lower().replace(" ", "_").replace("/", "_") for name in colnames]
        data = pandas.read_csv(self.fname, names=colnames, parse_dates=parse_dates, date_parser=my_date_parser, header=0, skipinitialspace=True)

        self.setDatesTimeStamps(data)
                
        self.latitudes  = np.array([self._parselatitude(lat, n_s)
                                    for (lat, n_s) in zip(data.latitude, data.n_s)])
        self.longitudes  = np.array([self._parselongitude(lon, e_w) 
                                    for (lon, e_w) in zip(data.longitude, data.e_w) ])
        
        self.elevations = np.array( [float(elev[:-2]) for elev in data.height] )
        self.speeds     = np.array( [float(speed[:-5]) for speed in data.speed] )
        
        self.headings   = np.array(data.heading.tolist() )
        
        self.is_missing = None
        
        self.is_valid   = np.ones_like(self.utc_timestamps)
        
        self.is_first_fix = np.zeros_like(self.utc_timestamps)
        self.is_first_fix[0] = 1
        
        self.is_last_fix = np.zeros_like(self.utc_timestamps)
        self.is_last_fix[-1] = 1

        success = 1
        return success
    
    def sort_times(self):
        if self.isSorted() == 0:
            self._ensure_sorted()
            self._ensure_no_duplicates()

        return self.isSorted()


    def setDatesTimeStamps(self, data):
        self.local_datetime = np.array([ self._fixGPSweekNumberRollOver(date) for date in  data.local_datetime ], dtype=datetime.datetime)
        self.utc_datetime = np.array([ self._fixGPSweekNumberRollOver(date)  for date in  data.utc_datetime ], dtype=datetime.datetime)

        self.utc_timestamps = np.array([ date.timestamp() for date in  self.utc_datetime ])
        self.local_timestamps = np.array([ date.timestamp() for date in  self.local_datetime ])

    def _fixGPSweekNumberRollOver(self, date):
        rollover = datetime.timedelta(weeks=1024)
        while date.year < self.years_of_collection[0]:
            date = date + rollover

        if date.year < self.years_of_collection[0] or date.year > self.years_of_collection[1]:
            print("Invalid datetime: ", date)
            raise

        return date
    
    def isSorted(self):
        jumps = np.where( np.diff(self.utc_timestamps) < 0. )[0]
        if jumps.shape[0] > 0:
            self.unordered_source = True
            print("Participant ", self.id, " has unsorted timestamps.")
            return 0
        return 1


        
    def _ensure_sorted(self):
        jumps = np.where( np.diff(self.utc_timestamps) < 0. )[0]
        if jumps.shape[0] > 0:
            self.unordered_source = True
            print("Participant ", self.id, " has unsorted timestamps.")
            self._sortme()
            
    def _sortme(self):
        indexes = np.argsort(self.utc_timestamps, 0)
        self.utc_timestamps = self.utc_timestamps[indexes]
        self.local_timestamps = self.local_timestamps[indexes]
        self.utc_datetime = self.utc_datetime[indexes]
        self.local_datetime = self.local_datetime[indexes]
        self.latitudes  = self.latitudes[indexes]
        self.longitudes = self.longitudes[indexes]
        self.elevations = self.elevations[indexes]
        self.speeds     = self.speeds[indexes]
        self.headings   = self.headings[indexes]
        
    def _ensure_no_duplicates(self):
        duplicates = np.where( np.diff(self.utc_timestamps) == 0. )[0]
        if duplicates.shape[0] > 0:
            self.unordered_source = True
            print("Participant ", self.id, " has duplicated timestamps.")
            self._remove_duplicates()
            
    def _remove_duplicates(self):
        unique_timestamps = []
        my_udt      = [] 
        my_lts      = []
        my_ldt      = []
        my_lat      = []
        my_lon      = []
        my_elev     = []
        my_speed    = []
        my_headings = []
        
        current_timestamp = -1
        
        for i in np.arange(self.utc_timestamps.shape[0]):
            if current_timestamp == self.utc_timestamps[i]:
                assert np.isclose(my_lat[-1], self.latitudes[i])
                assert np.isclose(my_lon[-1], self.longitudes[i])
                assert np.isclose(my_elev[-1], self.elevations[i], rtol=1e-1, atol=1)
            else:
                unique_timestamps += [self.utc_timestamps[i]]
                my_udt            += [self.utc_datetime[i]]
                my_lts            += [self.local_timestamps[i]]
                my_ldt            += [self.local_datetime[i]]
                my_lat            += [self.latitudes[i]]
                my_lon            += [self.longitudes[i]]
                my_elev           += [self.elevations[i]]
                my_speed          += [self.speeds[i]]
                my_headings       += [self.headings[i]]
                current_timestamp = self.utc_timestamps[i]
                
        self.utc_timestamps = np.array(unique_timestamps)
        self.utc_datetime   = np.array(my_udt)
        self.local_datetime = np.array(my_ldt)
        self.local_timestamps  = np.array(my_lts)
        self.latitudes = np.array(my_lat)
        self.longitudes = np.array(my_lon)
        self.elevations = np.array(my_elev)
        self.speeds     = np.array(my_speed)
        self.headings   = np.array(my_headings)
        
        
    def _parselatitude(self, lat, n_s):
        n_s = n_s.strip(" ")
        if n_s.lower() not in ['n', 's']:
            print("n_s", n_s)
            raise ValueError()
        
        if n_s.lower() == 's':
            return -lat
        else:
            return lat
        
    def _parselongitude(self, lon, e_w):
        e_w = e_w.strip(" ")
        assert e_w.lower() in ['e', 'w']
        if e_w.lower() == 'e':
            return lon
        else:
            return -lon
        
    def _getFix(self, i):
        if i < self.utc_timestamps.shape[0]:
            return Fix(self.utc_timestamps[i], (self.latitudes[i], self.longitudes[i]), self.elevations[i], i)
        else:
            return None
        
    def _log(self, *args):
        if self.logging:
            print(*args)
        
    def filter(self, parameters):
        g = GeodesicDistance()
        prev_fix = self._getFix(0)
        max_speed_ms = km_per_hour_to_meter_per_second(parameters["max_speed"])
        for i in np.arange(0, self.utc_timestamps.shape[0]):
            
            curr_fix = self._getFix(i)
            
            if curr_fix.tstmp - prev_fix.tstmp > parameters["max_sloss"]:
                self._log("Current Fix", i, " has timestamp", curr_fix.tstmp, "Previous fix", prev_fix.index, 
                          "has timestamp", prev_fix.tstmp, "Mark it as first fix" )
                self.is_first_fix[i] = 1
                self.is_last_fix[prev_fix.index] = 1
                #assert self.is_last_fix[prev_fix.index] == 1, "Error for fix {0}".format(i)
                
            if self.is_first_fix[i] and i == self.utc_timestamps.shape[0]-1:
                self.is_valid[i] = 0
                self.is_first_fix[i] = 0
                continue

            if self.is_first_fix[i] and i < self.utc_timestamps.shape[0]-1:
                self._log("Fix", i, " was marked as first fix")
                # Let's do a check forward:
                next_fix = self._getFix(i+1)
                nnext_fix = self._getFix(i+2)
                distance = g.compute_distance(*curr_fix.coords, *next_fix.coords)
                if nnext_fix:
                    distance2 = g.compute_distance(*curr_fix.coords, *nnext_fix.coords)
                    dt2 = nnext_fix.tstmp - curr_fix.tstmp
                    d_elev2 = np.abs(curr_fix.elev - nnext_fix.elev)
                else:
                    distance2 = np.inf
                    dt2 = 1.
                    d_elev2 = np.inf
                    
                if distance > parameters["max_dist"] and distance2 > parameters["max_dist"]:
                    self._log("First fix", i, "is invalid (max_dist)")
                    self.is_valid[i]       = 0
                    self.is_first_fix[i]   = 0
                    self.is_first_fix[i+1] = 1
                    continue
                
                dt = next_fix.tstmp - curr_fix.tstmp
                speed = distance/dt
                speed2 = distance2/dt2
                if speed > max_speed_ms and speed2 > max_speed_ms:
                    self._log("First fix", i, "is invalid (max_speed)")
                    self.is_valid[i] = 0
                    self.is_first_fix[i]   = 0
                    self.is_first_fix[i+1] = 1
                    continue
                
                d_elev = np.abs(curr_fix.elev - next_fix.elev)
                if d_elev > parameters["max_d_elev"] and d_elev2 > parameters["max_d_elev"]:
                    self._log("First fix", i, "is invalid (max_d_elev)")
                    self.is_valid[i] = 0
                    self.is_first_fix[i]   = 0
                    self.is_first_fix[i+1] = 1
                    continue
                
                if dt > parameters["max_sloss"]:
                    self._log("Fix", i, "is a lone fix")
                    self.is_last_fix[i]    = 1
                    self.is_first_fix[i+1] = 1
                
                prev_fix.assign(curr_fix)
                continue
            
            # If distance wrt previous fix is larger than max dist mark fix as invalid  
            distance = g.compute_distance(*prev_fix.coords, *curr_fix.coords)
            if distance > parameters["max_dist"]:
                self._log("Fix", i, " was marked as invalid (max_dist)")
                self.is_valid[i] = 0
                continue
            
            # If average speed wrt previos fix is larger than max speed mark fix as invalid
            dt = curr_fix.tstmp - prev_fix.tstmp
            speed = distance/dt
            if speed > max_speed_ms:
                self._log("Fix", i, " was marked as invalid (max_speed)")
                self.is_valid[i] = 0
                continue
            
            # If elevation change wrt previos fix is larger than max elevation change mark fix as invalid
            d_elev = np.abs(curr_fix.elev - prev_fix.elev)
            if d_elev > parameters["max_d_elev"]:
                self._log("Fix", i, " was marked as invalid (max_d_elev)")
                self.is_valid[i] = 0
                continue
            
            # If this is not the last fix
            if i < self.utc_timestamps.shape[0] - 1:
                next_fix = self._getFix(i+1)
                # Check if this is last fix (i.e. we have a loss of signal)
                dt_fwd = next_fix.tstmp - curr_fix.tstmp
                if dt_fwd > parameters["max_sloss"]:
                    #Mark this as last fix and next as first fix
                    self._log("Fix", i, " was marked as last fix")
                    self.is_last_fix[i]    = 1
                    self.is_first_fix[i+1] = 1
                else:
                    #We did not lost signal, check 3 points distance
                    dd_dist = g.compute_distance(*next_fix.coords, *prev_fix.coords)
                    if distance > parameters["min_dist"] and dd_dist < parameters["min_dist"]:
                        self._log("Fix", i, " was marked as invalid (min_dist)")
                        self.is_valid[i] = 0
                        continue
                    
            # If I am here it means that the fix is valid, so we can move to the next
            prev_fix.assign(curr_fix)
         
        if parameters["rm_lone"]:
            lone_points = (self.is_last_fix*self.is_first_fix)==1
            self._log("Remove lone points: ", np.where(lone_points)[0])
            self.is_valid[ lone_points ] = 0
            self.is_first_fix[lone_points] = 0
            self.is_last_fix[lone_points] = 0
            
        if parameters["rm_sparse"]:
            first_fixes = np.where(self.is_first_fix==1)[0]
            last_fixes = np.where(self.is_last_fix==1)[0]
            if first_fixes.shape[0] != last_fixes.shape[0]:
                print("Unmatched first/last fixes: ". first_fixes.shape[0], " ", last_fixes.shape[0])
                raise Exception("Unmatched first/last fixes")
            for i in np.arange(first_fixes.shape[0]):
                if self.utc_timestamps[last_fixes[i]] - self.utc_timestamps[first_fixes[i]] <= 180:
                    self._log("Remove sparse points: ", first_fixes[i], last_fixes[i])
                    self.is_valid[ first_fixes[i]:last_fixes[i]+1 ] = 0
                    self.is_first_fix[first_fixes[i]:last_fixes[i]+1] = 0
                    self.is_last_fix[first_fixes[i]:last_fixes[i]+1] = 0

    def trim(self, start_date, end_date) -> int:
        is_selected = np.logical_and( self.local_datetime >= start_date,
                                      self.local_datetime <= end_date)

        indexes = np.where(is_selected==1)[0]

        if(indexes.shape[0]==0):
            print("No fixes found in time frame")
            return -1

        self.utc_timestamps = self.utc_timestamps[indexes]
        self.local_timestamps = self.local_timestamps[indexes]
        self.local_datetime = self.local_datetime[indexes]
        self.utc_datetime = self.utc_datetime[indexes]
        self.latitudes  = self.latitudes[indexes]
        self.longitudes = self.longitudes[indexes]
        self.elevations = self.elevations[indexes]
        self.speeds     = self.speeds[indexes]
        self.headings   = self.headings[indexes]

        self.is_valid   = self.is_valid[indexes]
        self.is_first_fix = self.is_first_fix[indexes]
        self.is_first_fix[0] = 1
        
        self.is_last_fix = self.is_last_fix[indexes]
        self.is_last_fix[-1] = 1

        return 1

    def selectTimeFrames(self, time_frame) -> int:
        is_selected = np.zeros_like(self.utc_timestamps)
        for ii in np.arange(self.utc_timestamps.shape[0]):
            if time_frame.contains(self.local_datetime[ii]):
                is_selected[ii] = 1
            else:
                is_selected[ii] = 0

        indexes = np.where(is_selected==1)[0]

        if(indexes.shape[0]==0):
            print("No fixes found in time frame")
            return -1

        self.utc_timestamps = self.utc_timestamps[indexes]
        self.local_timestamps = self.local_timestamps[indexes]
        self.local_datetime = self.local_datetime[indexes]
        self.utc_datetime = self.utc_datetime[indexes]
        self.latitudes  = self.latitudes[indexes]
        self.longitudes = self.longitudes[indexes]
        self.elevations = self.elevations[indexes]
        self.speeds     = self.speeds[indexes]
        self.headings   = self.headings[indexes]

        self.is_valid   = self.is_valid[indexes]
        self.is_first_fix = self.is_first_fix[indexes]
        self.is_first_fix[0] = 1
        
        self.is_last_fix = self.is_last_fix[indexes]
        self.is_last_fix[-1] = 1

        return 1
            
    def getCleanData(self, filter_parameters, GPSData):
        self.filter(filter_parameters)
        out = GPSData(self.id, self.fname)
        out.unordered_source = self.unordered_source
        out.utc_timestamps = self.utc_timestamps[self.is_valid==1]
        out.local_timestamps = self.local_timestamps[self.is_valid==1]
        out.local_datetime = self.local_datetime[self.is_valid==1]
        out.latitudes  = self.latitudes[self.is_valid==1 ]
        out.longitudes = self.longitudes[self.is_valid==1]
        out.elevations = self.elevations[self.is_valid==1]
        out.is_first_fix = self.is_first_fix[self.is_valid==1 ]
        out.is_last_fix  = self.is_last_fix[self.is_valid==1 ]
        
        out.is_first_fix[0] = 1
        out.is_last_fix[-1] = 1
        
        out.valid_fixes_id = np.arange(self.utc_timestamps.shape[0])[self.is_valid==1]
        out.ntotal_fixes = self.utc_timestamps.shape[0]
        
        out.logging = self.logging
        out.compute_dist()
        
        return out

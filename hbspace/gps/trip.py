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


trip_mode = {-1: "unknown", 0: "slow_walk", 1: "walk", 2: "bike", 3: "vehicle"}


class Trip:
    def __init__(self, id=None, start_index=None, end_index=None, duration=None, distance=None, isValid=None):
        self.id = id
        self.start_index = start_index
        self.end_index = end_index
        self.duration = duration
        self.distance = distance
        self.is_valid = isValid
        
        self.radius   = None
        self.crowdist = None
        self.speedRMax = None
        self.speedAvg = None
        
        self.type = None
        
    def classify(self, parameters):
        if self.speedAvg < parameters["walk"][0] and self.speedRMax < parameters["walk"][1]:
            self.type = "walk"
        elif self.speedAvg < parameters["bike"][0] and self.speedRMax < parameters["bike"][1]:
            self.type = "bike"
        elif self.speedAvg < parameters["vehicle"][0] and self.speedRMax < parameters["vehicle"][1]:
            self.type = "vehicle"
        else:
            self.type = "unknown"
            
    def departedHome(self, data):
        if data.is_first_fix[self.start_index]:
            return ""
        else:
            return data.is_home[self.start_index]
    
    def arrivedHome(self, data):
        if data.is_last_fix[self.end_index]:
            return ""
        else:
            return data.is_home[self.end_index]

        
    def showMe(self):
        print("Start index", self.start_index)
        print("End index", self.end_index)
        print("Duration", self.duration)
        print("Distance", self.distance)
        print("Radius", self.radius)
        print("Crow distance", self.crowdist)
        print("Speed 90p", self.speed90p)
        print("Trip type", self.type)
        print("Trip is valid", self.is_valid)
        
    def getInfo(self, data):
        """
        data --> GPSData
        out --> Dictionary
        """
        out = {}
        
        out["partid"] = data.id
        out["tripid"] = self.id+1
        out['trip_is_valid'] = self.is_valid
        
        out["trip_start_date"]      = data.local_datetime[self.start_index].strftime('%Y-%m-%d')
        out["trip_start_time"]      = data.local_datetime[self.start_index].strftime('%H:%M:%S')
        out["trip_start_lat"]       = data.latitudes[self.start_index]
        out["trip_start_lon"]       = data.longitudes[self.start_index]
        out["trip_end_date"]        = data.local_datetime[self.end_index].strftime('%Y-%m-%d')
        out["trip_end_time"]        = data.local_datetime[self.end_index].strftime('%H:%M:%S')
        out["trip_end_lat"]         = data.latitudes[self.end_index]
        out["trip_end_lon"]         = data.longitudes[self.end_index]
        out["trip_duration"]        = self.duration/60.0      #Minutes
        out["trip_dist_traveled"]   = self.distance*1.e-3     #Km
        out["trip_dist_crowflight"] = self.crowdist*1.e-3     #Km
        out["trip_max_speed"]       = self.speedRMax           #Km/h
        out["trip_average_speed"]   = self.speedAvg           #Km/h
        out["trip_type"]            = self.type
        
        if data.is_home is not None:
            out["is_trip_start_home"] = self.departedHome(data)
            out["is_trip_end_home"] = self.arrivedHome(data)
            
        if data.store_id is not None:
            if data.store_id[self.start_index] > -1:
                out["trip_start_store_id"] = data.store_id[self.start_index]
                out["is_fresh_trip_start"]  = data.store_marker[self.start_index]
            if data.store_id[self.end_index] > -1:
                out["trip_end_store_id"] = data.store_id[self.end_index]
                out["is_fresh_trip_end"]  = data.store_marker[self.end_index]
            
        
        return out
        
    @classmethod
    def infoKeys(self):
        return [
                "partid",                 #Participant ID
                "tripid",                 #Trip ID
                "trip_is_valid",
                "trip_start_date",        #Trip Start date (YYYY-MM-DD)
                "trip_start_time",        #Trip Start time (HH:MM:SS)
                "trip_start_lat",         #Trip Start latitude (N: positive, S: negative)
                "trip_start_lon",         #Trip Start longitudine (W: positive, E: negative)
                "trip_end_date",          #Trip End date (YYYY-MM-DD)
                "trip_end_time",          #Trip End time (HH:MM:SS)
                "trip_end_lat",           #Trip End latitude (N: positive, S: negative)
                "trip_end_lon",           #Trip End longitudine (W: positive, E: negative)
                "trip_duration",          #Trip duration (minutes)
                "trip_dist_traveled",     #Distance traveled for this trip (Km)
                "trip_dist_crowflight",   #Crowflight distance between origin and destistantion (Km)
                "trip_max_speed",         # Robust max speed (km/h)
                "trip_average_speed",     # Average speed
                "trip_type"               # Trip type: Walk, Bike, Vehicle
                ]
        
    @classmethod
    def infoKeysExt(self):
        return [
                "partid",                 #Participant ID
                "tripid",                 #Trip ID
                "trip_is_valid",
                "trip_start_date",        #Trip Start date (YYYY-MM-DD)
                "trip_start_time",        #Trip Start time (HH:MM:SS)
                "trip_start_lat",         #Trip Start latitude (N: positive, S: negative)
                "trip_start_lon",         #Trip Start longitudine (W: positive, E: negative)
                "is_trip_start_home",     #Trip starts at home
                "trip_start_store_id",   #If trip starts at store report store ID
                "is_fresh_trip_start",    #If trip starts at store, is the store a Fresh store?    
                "trip_end_date",          #Trip End date (YYYY-MM-DD)
                "trip_end_time",          #Trip End time (HH:MM:SS)
                "trip_end_lat",           #Trip End latitude (N: positive, S: negative)
                "trip_end_lon",           #Trip End longitudine (W: positive, E: negative)
                "is_trip_end_home",       #Trip ends at home
                "trip_end_store_id",     #If trip ends at store report store ID
                "is_fresh_trip_end",      #If trip ends at store, is the store a Fresh store? 
                "trip_duration",          #Trip duration (minutes)
                "trip_dist_traveled",     #Distance traveled for this trip (Km)
                "trip_dist_crowflight",   #Crowflight distance between origin and destistantion (Km)
                "trip_max_speed",         # Robust max speed (km/h)
                "trip_average_speed",     # Average speed
                "trip_type"               # Trip type: Walk, Bike, Vehicle
                ]
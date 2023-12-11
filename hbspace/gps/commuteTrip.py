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

import csv

trip_mode = {-1: "unknown", 0: "slow_walk", 1: "walk", 2: "bike", 3: "vehicle"}

class CommuteTrip:
    def __init__(self, id=None, start_index=None, last_index=None, duration=None, distance=None, isValid=None):
        self.id = id
        self.start_index = start_index
        self.last_index = last_index
        self.duration = duration
        self.distance = distance
        self.is_valid = isValid
        
        self.radius   = None
        self.crowdist = None
        self.speedRMax = None
        self.speedAvg = None
        self.speed90p = None
        
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
        return data.is_home[self.start_index]
    
    def arrivedHome(self, data):
        return data.is_home[self.last_index]
        
    def departedDest(self, data):
        return data.is_dest[self.start_index]
    
    def arrivedDest(self, data):
        return data.is_dest[self.last_index]
        
    def isInbound(self, data):
        return data.is_dest[self.start_index] * data.is_home[self.last_index]
    
    def isOutbound(self, data):
        return data.is_home[self.start_index] * data.is_dest[self.last_index]
    
    def Outbound_Inbound(self, data):
        if self.isOutbound(data):
            return 1
        elif self.isInbound(data):
            return 2
        else:
            return 0

    
    def isCommute(self, data):
        if self.Outbound_Inbound(data) == 0:
            return 0
        else:
            return 1

        
    def showMe(self):
        print("Start index", self.start_index)
        print("Last index", self.last_index)
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
        out['trip_is_commute'] = self.isCommute(data)
        out['Outbound_inbound'] = self.Outbound_Inbound(data)

        
        out["trip_start_date"]      = data.local_datetime[self.start_index].strftime('%Y-%m-%d')
        out["trip_start_time"]      = data.local_datetime[self.start_index].strftime('%H:%M:%S')
        if self.departedHome(data):
            out["trip_start_lat"]       = data.home.lat
            out["trip_start_lon"]       = data.home.lon
        elif self.departedDest(data):
            out["trip_start_lat"]       = data.dest.lat
            out["trip_start_lon"]       = data.dest.lon
        else:
            out["trip_start_lat"]       = data.latitudes[self.start_index]
            out["trip_start_lon"]       = data.longitudes[self.start_index]
        out["trip_end_date"]        = data.local_datetime[self.last_index].strftime('%Y-%m-%d')
        out["trip_end_time"]        = data.local_datetime[self.last_index].strftime('%H:%M:%S')
        if self.arrivedHome(data):
            out["trip_end_lat"]         = data.home.lat
            out["trip_end_lon"]         = data.home.lon
        elif self.arrivedDest(data):
            out["trip_end_lat"]         = data.dest.lat
            out["trip_end_lon"]         = data.dest.lon
        else:
            out["trip_end_lat"]         = data.latitudes[self.last_index]
            out["trip_end_lon"]         = data.longitudes[self.last_index]

        out["trip_duration"]        = self.duration/60.0      #Minutes
        out["trip_dist_traveled"]   = self.distance*1.e-3     #Km
        out["trip_dist_crowflight"] = self.crowdist*1.e-3     #Km
        out["trip_90p_speed"]       = self.speed90p           #Km/h
        out["trip_average_speed"]   = self.speedAvg           #Km/h
        out["trip_type"]            = self.type
            
        return out
    
    def appendAccInfo(self, gpsData, accData, cp, out):
        time_interval = [gpsData.local_datetime[self.start_index],
                         gpsData.local_datetime[self.last_index]]
        tot, avg, perc = accData.getCountsStatsInterval(time_interval)
        out['trip_acc_counts_total']   = tot
        out['trip_acc_avg_counts_min'] = avg
        out['trip_acc_90p_counts_min'] = perc

        median, perc, minutes = accData.getIntensityStatsInterval(cp, time_interval)
        out['trip_acc_intensity_median'] = median
        out['trip_acc_intensity_90p'] = perc
        for int_level in cp.levels:
            ll = int_level.decode()
            out['trip_acc_{0:s}_min'.format(ll)] = minutes[int_level] 

        
    @classmethod
    def infoKeys(cls):
        return [
                "partid",                 #Participant ID
                "tripid",                 #Trip ID
                "trip_is_valid",
                'trip_is_commute',
                'Outbound_inbound',
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
                "trip_90p_speed",         # Robust max speed (km/h)
                "trip_average_speed",     # Average speed
                "trip_type"               # Trip type: Walk, Bike, Vehicle
                ]
    
    @classmethod
    def infoKeysAcc(cls):
        out = cls.infoKeys()
        acc = ['trip_acc_counts_total',
               'trip_acc_avg_counts_min',
               'trip_acc_90p_counts_min',
               'trip_acc_intensity_median',
               'trip_acc_intensity_90p',
               'trip_acc_SED_min',
               'trip_acc_LPA_min',
               'trip_acc_MPA_min',
               'trip_acc_VPA_min']
        
        out.extend(acc)

        return out
        
    
def Triplog_writer_commuter(gpsData, fname_out):
    fieldnames = CommuteTrip.infoKeys()
        
    with open(fname_out, "w", newline='') as fid:
        writer = csv.DictWriter(fid, fieldnames)
        writer.writeheader()
        for trip in gpsData.trips:
            data = trip.getInfo(gpsData)
            writer.writerow(data)

def TriplogAcc_writer_commuter(gpsData, accData, activities_cp, fname_out):
    fieldnames = CommuteTrip.infoKeysAcc()
        
    with open(fname_out, "w", newline='') as fid:
        writer = csv.DictWriter(fid, fieldnames)
        writer.writeheader()
        for trip in gpsData.trips:
            data = trip.getInfo(gpsData)
            trip.appendAccInfo(gpsData, accData,  activities_cp, data)
            writer.writerow(data)

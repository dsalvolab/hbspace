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
from .enum import TripDirection, GPSState
import skimage
import numpy as np


trip_mode = {-1: "unknown", 0: "slow_walk", 1: "walk", 2: "bike", 3: "vehicle"}

class CommuteTrip:
    __slots__ = ['partid',
                 'id',
                 'start_index',
                 'end_index',
                 'direction',
                 'start_datetime',
                 'end_datetime',
                 'start_coordinates', #(lat, lon)
                 'end_coordinates', #(lat, lon)
                 'duration_including_stops_in_min',
                 'duration_excluding_stops_in_min',
                 'number_of_stops',
                 'total_duration_of_stops_in_min',
                 'number_of_pauses',
                 'total_duration_of_pauses_in_min',
                 'distance_traveled_in_km',
                 'distance_crowflight_in_km',
                 'radius_in_km',
                 'speeds_excluding_stops_in_km_h'
                 ]
    
    percentiles = [0, 10, 25, 50, 75, 90, 100]
    
    def __init__(self, partid=None, id=None, start_index=None, end_index=None, direction=None):
        self.partid = partid
        self.id = id
        self.start_index = start_index
        self.end_index = end_index
        self.direction = direction

    @property
    def departedHome(self):
        return self.direction in [TripDirection.H2D, TripDirection.H2X]
    
    @property
    def arrivedHome(self):
        return self.direction in [TripDirection.D2H, TripDirection.X2H]
    
    @property
    def departedDest(self):
        return self.direction in [TripDirection.D2H, TripDirection.D2X]
    
    @property
    def arrivedDest(self):
        return self.direction in [TripDirection.H2D, TripDirection.X2D]

    def computeInfoFromGPS(self, gps_data):
        self.start_datetime = gps_data.local_datetime[self.start_index]
        self.end_datetime = gps_data.local_datetime[self.end_index-1]

        if self.departedHome:
            self.start_coordinates = (gps_data.home.lat, gps_data.home.lon)
        elif self.departedDest:
            self.start_coordinates = (gps_data.dest.lat, gps_data.dest.lon)
        else:
            self.start_coordinates = (gps_data.latitudes[self.start_index], gps_data.longitutes[self.start_index])

        if self.arrivedHome:
            self.end_coordinates = (gps_data.home.lat, gps_data.home.lon)
        elif self.arrivedDest:
            self.end_coordinates = (gps_data.dest.lat, gps_data.dest.lon)
        else:
            self.end_coordinates = (gps_data.latitudes[self.end_index-1], gps_data.longitudes[self.end_index-1])

        self.duration_including_stops_in_min = (self.end_datetime-self.start_datetime).total_seconds()/60.0
        
        # Extraxct local infos
        trip_lats   = gps_data.latitudes[self.start_index:self.end_index]
        trip_lons   = gps_data.longitudes[self.start_index:self.end_index]
        trip_states = gps_data.state[self.start_index:self.end_index]
        trip_speeds = gps_data.speeds[self.start_index:self.end_index]
        trip_datetime = gps_data.local_datetime[self.start_index:self.end_index]

        #COUNT NUMBER OF STOPS AND THEIR DURATION
        stop_marker = (trip_states == GPSState.STATIONARY)
        stops, nstops = skimage.measure.label(stop_marker, return_num=True)
        self.number_of_stops = nstops
        self.total_duration_of_stops_in_min = 0.
        for istop in range(1,nstops+1):
            istop_indexes = np.nonzero(stops==istop)[0]
            stop_start_index = istop_indexes[0]
            stop_end_index =  istop_indexes[-1]+1
            stop_start = trip_datetime[stop_start_index]
            stop_end = trip_datetime[stop_end_index]
            stop_duration_in_minutes = (stop_end-stop_start).total_seconds()/60.
            self.total_duration_of_stops_in_min = self.total_duration_of_stops_in_min+stop_duration_in_minutes

        del stop_marker, stops, nstops

        self.duration_excluding_stops_in_min = self.duration_including_stops_in_min - self.total_duration_of_stops_in_min

        #COUNT NUMBER OF PAUSES AND THEIR DURATION
        pause_marker = (trip_states == GPSState.PAUSE)
        pauses, npauses = skimage.measure.label(pause_marker, return_num=True)
        self.number_of_pauses = npauses
        self.total_duration_of_pauses_in_min = 0.
        for ipause in range(1,npauses+1):
            ipause_indexes = np.nonzero(pauses==ipause)[0]
            pause_start_index = ipause_indexes[0]
            pause_end_index =  ipause_indexes[-1]+1
            pause_start = trip_datetime[pause_start_index]
            pause_end = trip_datetime[pause_end_index]
            pause_duration_in_minutes = (pause_end-pause_start).total_seconds()/60.
            self.total_duration_of_pauses_in_min = self.total_duration_of_pauses_in_min+pause_duration_in_minutes


        # Compute distance traveled
        self.distance_traveled_in_km = gps_data.g.compute_traveled_distance(trip_lats, trip_lons)*1e-3
        self.distance_crowflight_in_km = gps_data.g.compute_distance_t(self.start_coordinates, self.end_coordinates)*1e-3
        self.radius_in_km = gps_data.g.compute_radius( trip_lats, trip_lons)*1e-3

        self.speeds_excluding_stops_in_km_h = trip_speeds[trip_states==GPSState.MOTION]

      
    def classify(self, parameters):
        if self.speedAvg < parameters["walk"][0] and self.speedRMax < parameters["walk"][1]:
            self.type = "walk"
        elif self.speedAvg < parameters["bike"][0] and self.speedRMax < parameters["bike"][1]:
            self.type = "bike"
        elif self.speedAvg < parameters["vehicle"][0] and self.speedRMax < parameters["vehicle"][1]:
            self.type = "vehicle"
        else:
            self.type = "unknown"
                

    def showMe(self):
        print("Start index", self.start_index)
        print("Last index", self.end_index)
        print("direction", self.direction)
        print("duration including stops [minutes]", self.duration_including_stops_in_min)
        print("Traveled distance km", self.distance_traveled_in_km)
        print("Crowflight distance km", self.distance_crowflight_in_km)

        
    def getInfo(self):
        """
        data --> GPSData
        out --> Dictionary
        """
        out = {}
        
        out["partid"] = self.partid
        out["tripid"] = self.id+1
        out["unique_id"] = self.partid + "_{0:03d}".format(self.id+1)
        out['trip_direction'] = self.direction

        out["trip_start_date"] = self.start_datetime.strftime('%Y-%m-%d')
        out["trip_start_time"] = self.start_datetime.strftime('%H:%M:%S')
        out["trip_end_date"]   = self.end_datetime.strftime('%Y-%m-%d')
        out["trip_end_time"]   = self.end_datetime.strftime('%H:%M:%S')

        out['departed_home'] = self.departedHome
        out['departed_dest'] = self.departedDest
        out['arrived_home']  = self.arrivedHome
        out['arrived_dest']  = self.arrivedDest

        out["trip_start_lat"] = self.start_coordinates[0]
        out["trip_start_lon"] = self.start_coordinates[1]
        out["trip_end_lat"]   = self.end_coordinates[0]
        out["trip_end_lon"]   = self.end_coordinates[1]

        out["trip_duration_including_stops"] = self.duration_including_stops_in_min
        out["trip_duration_excluding_stops"] = self.duration_excluding_stops_in_min
        out["trip_total_duration_of_stops"] = self.total_duration_of_stops_in_min
        out["trip_total_duration_of_pauses"] = self.total_duration_of_pauses_in_min
        out["trip_number_of_stops"] = self.number_of_stops
        out["trip_number_of_pauses"] = self.number_of_pauses
        out["trip_dist_traveled"]   = self.distance_traveled_in_km
        out["trip_dist_crowflight"] = self.distance_crowflight_in_km
        out["trip_radius"]          = self.radius_in_km
        speed_percentiles = np.percentile(self.speeds_excluding_stops_in_km_h, self.percentiles)
        for i, p in enumerate(self.percentiles):
            out["trip_{0:d}p_speed".format(p)]  = speed_percentiles[i]
        out["trip_average_speed"]   = np.mean(self.speeds_excluding_stops_in_km_h)
            
        return out
    
    def getCountsStats(self, accData):
        time_interval = [self.start_datetime, self.end_datetime]
        return accData.getCountsStatsInterval(time_interval)

    
    def getAccInfo(self, accData, cp):
        out = {}
        time_interval = [self.start_datetime, self.end_datetime]
        tot, avg, perc = accData.getCountsStatsInterval(time_interval)
        out['trip_acc_counts_total']   = tot
        out['trip_acc_avg_counts_min'] = avg
        out['trip_acc_90p_counts_min'] = perc

        median, perc, minutes = accData.getIntensityStatsInterval(cp, time_interval)
        out['trip_acc_intensity_median'] = median
        out['trip_acc_intensity_90p'] = perc
        for int_level in cp.levels:
            out['trip_acc_{0:s}_min'.format(int_level)] = minutes[int_level] 

        return out

        
    @classmethod
    def infoKeys(cls):
        keys =  [
                "partid",          # Participant ID
                "tripid",          # Trip ID
                "unique_id",       # ParticipantID_TripID
                'trip_direction',  # 0=X2X, etc
                "trip_start_date", # format '%Y-%m-%d'
                "trip_start_time", # format '%H:%M:%S'
                "trip_end_date",   # format '%Y-%m-%d'
                "trip_end_time",   # format '%H:%M:%S'
                'departed_home', 
                'departed_dest',
                'arrived_home',
                'arrived_dest',
                "trip_start_lat", #Trip Start latitude (N: positive, S: negative)
                "trip_start_lon", #Trip Start longitudine (W: positive, E: negative)
                "trip_end_lat", #Trip End latitude (N: positive, S: negative)
                "trip_end_lon", #Trip End longitudine (W: positive, E: negative)
                "trip_duration_including_stops", # Trip duration in minutes
                "trip_duration_excluding_stops", # Trip duration in minutes
                "trip_total_duration_of_stops",
                "trip_total_duration_of_pauses",
                "trip_number_of_stops",
                "trip_number_of_pauses",
                "trip_dist_traveled", #Distance traveled in km
                "trip_dist_crowflight", #Distance crowflight in km
                "trip_radius"
            ]
        
        for p in cls.percentiles:
            keys.append("trip_{0:d}p_speed".format(p))
        keys.append("trip_average_speed")

        return keys
    
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
        
    
def Triplog_writer_commuter(trips, writer):
    for trip in trips:
        data = trip.getInfo()
        writer.writerow(data)

def TriplogAcc_writer_commuter(trips, accData, activities_cp, writer):
    for trip in trips:
        info = trip.getInfo()
        info_acc = trip.getAccInfo(accData,  activities_cp)
        info.update(info_acc)
        writer.writerow(info)

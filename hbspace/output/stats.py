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

def trip_stats_headers():
    out = ["partid",                 # PARTICIPANT ID
           "start_date",             # FIRST DAY OF DATA COLLECTION
           "start_time",             # TIME WHEN DATA COLLECTION STARTED
           "end_date",               # LAST DAY OF DATA COLLECTION
           "end_time",               # TIME WHEN DATA COLLECTION ENDED
           "number_of_days",         # NUMBER OF DAYS (defined as 24h periods, since the time data collection started)
           "total_hours",            # Total hours of data collection
           "valid_hours",            # Total hours with valid GPS signal
           "sloss_hours",            # Total hours without GPS signal
           "tot_number_of_trips",    # TOTAL NUMBER OF TRIPS
           "tot_number_of_valid_trips", #  TOTAL NUMBER OF VALID TRIPS
           "average_trip_duration",  # AVERAGE TRIP DURATION (minutes) 
           "average_trip_distance",  # AVERAGE DISTANCE TRAVELED (in km)
           "average_trip_crowdist",  # AVERAGE DISTANCE FROM STARTING POINT to DESTINATION (in Km)
           "std_trip_duration",      # STD TRIP DURATION (minutes) 
           "std_trip_distance",      # STD DISTANCE TRAVELED (in km)
           "std_trip_crowdist",      # STD DISTANCE FROM STARTING POINT to DESTINATION (in Km)
           "min_trip_duration",      # MIN TRIP DURATION (minutes) 
           "min_trip_distance",      # MIN DISTANCE TRAVELED (in km)
           "min_trip_crowdist",      # MIN DISTANCE FROM STARTING POINT to DESTINATION (in Km)
           "max_trip_duration",      # MAX TRIP DURATION (minutes) 
           "max_trip_distance",      # MAX DISTANCE TRAVELED (in km)
           "max_trip_crowdist",      # MAX DISTANCE FROM STARTING POINT to DESTINATION (in Km)
           "p25_trip_duration",      # 25th percentile TRIP DURATION (minutes) 
           "p25_trip_distance",      # 25th percentile DISTANCE TRAVELED (in km)
           "p25_trip_crowdist",      # 25th percentile DISTANCE FROM STARTING POINT to DESTINATION (in Km)
           "p50_trip_duration",      # 50th percentile TRIP DURATION (minutes) 
           "p50_trip_distance",      # 50th percentile DISTANCE TRAVELED (in km)
           "p50_trip_crowdist",      # 50th percentile DISTANCE FROM STARTING POINT to DESTINATION (in Km)
           "p75_trip_duration",      # 75th percentile TRIP DURATION (minutes) 
           "p75_trip_distance",      # 75th percentile DISTANCE TRAVELED (in km)
           "p75_trip_crowdist",      # 75th percentile DISTANCE FROM STARTING POINT to DESTINATION (in Km)
           "tot_visits_to_store",    # Total number of visits to store
           "tot_visits_to_fresh_store", # Total number of visits to fresh store
           "tot_trips_originated_from_home", # Total number of trips originated from home
           "tot_trips_arrived_at_home",      # Total number of trips arrived at home
           ]
    
    for type in ["walk", "bike", "vehicle"]:
        out.append("tot_number_of_"+type+"_trips")
        out.append("average_"+type+"_trip_duration")
        out.append("average_"+type+"_trip_distance")
        out.append("average_"+type+"_trip_crowdist")
        out.append("std_"+type+"_trip_duration")
        out.append("std_"+type+"_trip_distance")
        out.append("std_"+type+"_trip_crowdist")
        out.append("min_"+type+"_trip_duration")
        out.append("min_"+type+"_trip_distance")
        out.append("min_"+type+"_trip_crowdist")
        out.append("max_"+type+"_trip_duration")
        out.append("max_"+type+"_trip_distance")
        out.append("max_"+type+"_trip_crowdist")
        out.append("p25_"+type+"_trip_duration")
        out.append("p25_"+type+"_trip_distance")
        out.append("p25_"+type+"_trip_crowdist")
        out.append("p50_"+type+"_trip_duration")
        out.append("p50_"+type+"_trip_distance")
        out.append("p50_"+type+"_trip_crowdist")
        out.append("p75_"+type+"_trip_duration")
        out.append("p75_"+type+"_trip_distance")
        out.append("p75_"+type+"_trip_crowdist")
    return out

def trip_stats(data):
    out = {}
    out["partid"]     = data.id
    out["start_date"] = data.local_datetime[0].strftime('%Y-%m-%d')
    out["start_time"] = data.local_datetime[0].strftime('%H:%M:%S')
    out["end_date"]   = data.local_datetime[-1].strftime('%Y-%m-%d')
    out["end_time"]   = data.local_datetime[-1].strftime('%H:%M:%S')
    tot_hours, valid_hours, sloss_hours = data.measurement_time()
    out["number_of_days"] = np.ceil( tot_hours/24. )
    out["total_hours"] = tot_hours
    out["valid_hours"] = valid_hours
    out["sloss_hours"] = sloss_hours
        
    out["tot_number_of_trips"] = len(data.trips)
    
    valid_trips = [trip for trip in data.trips if trip.is_valid]
    
    out["tot_number_of_valid_trips"] = len(valid_trips)
    
    durations = [trip.duration/60.   for trip in valid_trips]
    distances = [trip.distance*1.e-3 for trip in valid_trips]
    crowdists = [trip.crowdist*1.e-3 for trip in valid_trips]
    
    out["average_trip_duration"] = np.mean(durations)
    out["average_trip_distance"] = np.mean(distances)
    out["average_trip_crowdist"] = np.mean(crowdists)
    out["std_trip_duration"]     = np.std(durations)
    out["std_trip_distance"]     = np.std(distances)
    out["std_trip_crowdist"]     = np.std(crowdists)
    out["min_trip_duration"]     = np.min(durations)
    out["min_trip_distance"]     = np.min(distances)
    out["min_trip_crowdist"]     = np.min(crowdists)
    out["max_trip_duration"]     = np.max(durations)
    out["max_trip_distance"]     = np.max(distances)
    out["max_trip_crowdist"]     = np.max(crowdists)
    
    duration_percentiles = np.percentile(durations, [25,50,75])
    distance_percentiles = np.percentile(distances, [25,50,75])
    crowdist_percentiles = np.percentile(crowdists, [25,50,75])
    
    out["p25_trip_duration"] = duration_percentiles[0]
    out["p25_trip_distance"] = distance_percentiles[0]
    out["p25_trip_crowdist"] = crowdist_percentiles[0]
    out["p50_trip_duration"] = duration_percentiles[1]
    out["p50_trip_distance"] = distance_percentiles[1]
    out["p50_trip_crowdist"] = crowdist_percentiles[1]
    out["p75_trip_duration"] = duration_percentiles[2]
    out["p75_trip_distance"] = distance_percentiles[2]
    out["p75_trip_crowdist"] = crowdist_percentiles[2]
        
    for type in ["walk", "bike", "vehicle"]:
        trips = [trip for trip in valid_trips if trip.type == type]
        ntrips = len(trips)
        out["tot_number_of_"+type+"_trips"]   = ntrips
        if ntrips > 0:
            durations = [trip.duration/60. for trip in trips]
            distances = [trip.distance*1.e-3 for trip in trips]
            crowdists = [trip.crowdist*1.e-3 for trip in trips]
            
            out["average_"+type+"_trip_duration"] = np.mean(durations)
            out["average_"+type+"_trip_distance"] = np.mean(distances)
            out["average_"+type+"_trip_crowdist"] = np.mean(crowdists)
            out["std_"+type+"_trip_duration"]     = np.std(durations)
            out["std_"+type+"_trip_distance"]     = np.std(distances)
            out["std_"+type+"_trip_crowdist"]     = np.std(crowdists)
            out["min_"+type+"_trip_duration"]     = np.min(durations)
            out["min_"+type+"_trip_distance"]     = np.min(distances)
            out["min_"+type+"_trip_crowdist"]     = np.min(crowdists)
            out["max_"+type+"_trip_duration"]     = np.max(durations)
            out["max_"+type+"_trip_distance"]     = np.max(distances)
            out["max_"+type+"_trip_crowdist"]     = np.max(crowdists)
            
            duration_percentiles = np.percentile(durations, [25,50,75])
            distance_percentiles = np.percentile(distances, [25,50,75])
            crowdist_percentiles = np.percentile(crowdists, [25,50,75])
            
            out["p25_"+type+"_trip_duration"] = duration_percentiles[0]
            out["p25_"+type+"_trip_distance"] = distance_percentiles[0]
            out["p25_"+type+"_trip_crowdist"] = crowdist_percentiles[0]
            out["p50_"+type+"_trip_duration"] = duration_percentiles[1]
            out["p50_"+type+"_trip_distance"] = distance_percentiles[1]
            out["p50_"+type+"_trip_crowdist"] = crowdist_percentiles[1]
            out["p75_"+type+"_trip_duration"] = duration_percentiles[2]
            out["p75_"+type+"_trip_distance"] = distance_percentiles[2]
            out["p75_"+type+"_trip_crowdist"] = crowdist_percentiles[2]
            
    tot_visits_to_store = 0
    tot_visits_to_fresh_store = 0
    for v in data.visits:
        if v.store_id not in [None, ""]:
            tot_visits_to_store+=1
        if v.store_marker == 1:
            tot_visits_to_fresh_store += 1
            
    out["tot_visits_to_store"] = tot_visits_to_store
    out["tot_visits_to_fresh_store"] = tot_visits_to_fresh_store
    
    tot_trips_originated_from_home = 0
    tot_trips_arrived_at_home      = 0
    for t in trips:
        if t.departedHome(data) == 1:
            tot_trips_originated_from_home += 1
        if t.arrivedHome(data) == 1:
            tot_trips_arrived_at_home += 1
            
    out["tot_trips_originated_from_home"] = tot_trips_originated_from_home
    out["tot_trips_arrived_at_home"] = tot_trips_arrived_at_home
            
    return out
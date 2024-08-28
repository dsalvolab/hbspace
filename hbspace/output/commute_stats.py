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
from ..gps.enum import TripDirection

def commute_trip_stats_headers(cp):
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
           "tot_number_of_commute_trips", #  TOTAL NUMBER OF VALID TRIPS to from school
           "tot_number_of_outbound_trips", #  TOTAL NUMBER OF VALID TRIPS from home to school
           "tot_number_of_inbound_trips", #  TOTAL NUMBER OF VALID TRIPS from school to home
           "average_trip_duration",  # AVERAGE TRIP to/from school DURATION (minutes) 
           "average_trip_distance",  # AVERAGE DISTANCE TRAVELED to/from school (in km)
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
           "avg_acc_avg_counts_min", # Average average acc counts per minute
           "std_acc_avg_counts_min", # Std average acc counts per minute
           "min_acc_avg_counts_min", # Min average acc counts per minute
           "max_acc_avg_counts_min", # Min average acc counts per minute
           "p25_acc_avg_counts_min", # 25th percentile average acc counts per minute
           "p50_acc_avg_counts_min", # 50th percentile average acc counts per minute
           "p75_acc_avg_counts_min", # 75th percentile average acc counts per minute
           ]
    
    for level in cp.levels:
        out.append("avg_trip_acc_{0:s}_min".format(level))
        out.append("std_trip_acc_{0:s}_min".format(level))
        out.append("min_trip_acc_{0:s}_min".format(level))
        out.append("max_trip_acc_{0:s}_min".format(level))
        out.append("p25_trip_acc_{0:s}_min".format(level))
        out.append("p50_trip_acc_{0:s}_min".format(level))
        out.append("p75_trip_acc_{0:s}_min".format(level))
    
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
        out.append("avg_"+type+"_acc_avg_counts_min") 
        out.append("std_"+type+"_acc_avg_counts_min")
        out.append("min_"+type+"_acc_avg_counts_min")
        out.append("max_"+type+"_acc_avg_counts_min")
        out.append("p25_"+type+"_acc_avg_counts_min")
        out.append("p50_"+type+"_acc_avg_counts_min")
        out.append("p75_"+type+"_acc_avg_counts_min")
        for level in cp.levels:
            out.append("avg_"+type+"_trip_acc_{0:s}_min".format(level))
            out.append("std_"+type+"_trip_acc_{0:s}_min".format(level))
            out.append("min_"+type+"_trip_acc_{0:s}_min".format(level))
            out.append("max_"+type+"_trip_acc_{0:s}_min".format(level))
            out.append("p25_"+type+"_trip_acc_{0:s}_min".format(level))
            out.append("p50_"+type+"_trip_acc_{0:s}_min".format(level))
            out.append("p75_"+type+"_trip_acc_{0:s}_min".format(level))
    return out

def commute_trip_stats(dataGPS, dataAcc, cp):
    out = {}
    out["partid"]     = dataGPS.id
    out["start_date"] = dataGPS.local_datetime[0].strftime('%Y-%m-%d')
    out["start_time"] = dataGPS.local_datetime[0].strftime('%H:%M:%S')
    out["end_date"]   = dataGPS.local_datetime[-1].strftime('%Y-%m-%d')
    out["end_time"]   = dataGPS.local_datetime[-1].strftime('%H:%M:%S')
    tot_hours, valid_hours, sloss_hours = dataGPS.measurement_time()
    out["number_of_days"] = np.ceil( tot_hours/24. )
    out["total_hours"] = tot_hours
    out["valid_hours"] = valid_hours
    out["sloss_hours"] = sloss_hours
        
    out["tot_number_of_trips"] = len(dataGPS.trips)
    
    valid_trips = [trip for trip in dataGPS.trips if trip.is_valid]
    out["tot_number_of_valid_trips"] = len(valid_trips)

    commute_trips = [trip for trip in valid_trips if trip.isCommute(dataGPS)]
    out["tot_number_of_commute_trips"] = len(commute_trips)


    outbound_inbound = np.array([trip.Outbound_Inbound(dataGPS) for trip in commute_trips])
    out["tot_number_of_outbound_trips"] = sum(outbound_inbound ==  CommuteDirection.OUTBOUND)
    out["tot_number_of_inbound_trips"] = sum(outbound_inbound == CommuteDirection.INBOUND)

    if len(commute_trips) == 0:
        return out
    
    durations = [trip.duration/60.   for trip in commute_trips]
    distances = [trip.distance*1.e-3 for trip in commute_trips]
    crowdists = [trip.crowdist*1.e-3 for trip in commute_trips]
    
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

    if dataAcc is not None:
        acc_avg_counts_min = [trip.getCountsStats(dataGPS, dataAcc)[1] for trip in commute_trips]
        acc_avg_counts_min = [a for a in acc_avg_counts_min if a!='']
        if len(acc_avg_counts_min) > 0:
            out["avg_acc_avg_counts_min"] = np.mean(acc_avg_counts_min)
            out["std_acc_avg_counts_min"] = np.std(acc_avg_counts_min)
            out["min_acc_avg_counts_min"] = np.min(acc_avg_counts_min)
            out["max_acc_avg_counts_min"] = np.max(acc_avg_counts_min)

            acc_avg_counts_min_percentiles = np.percentile(acc_avg_counts_min, [25,50,75])
            out["p25_acc_avg_counts_min"] = acc_avg_counts_min_percentiles[0]
            out["p50_acc_avg_counts_min"] = acc_avg_counts_min_percentiles[1]
            out["p75_acc_avg_counts_min"] = acc_avg_counts_min_percentiles[2]

        activity_info = [trip.getAccInfo(dataGPS, dataAcc, cp) for trip in commute_trips]
        for level in cp.levels:
            minutes = [info['trip_acc_{0:s}_min'.format(level)] for info in activity_info]
            minutes = [m for m in minutes if m!='']
            if len(minutes) > 0:
                out["avg_trip_acc_{0:s}_min".format(level)] = np.mean(minutes)
                out["std_trip_acc_{0:s}_min".format(level)] = np.std(minutes)
                out["min_trip_acc_{0:s}_min".format(level)] = np.min(minutes)
                out["max_trip_acc_{0:s}_min".format(level)] = np.max(minutes)

                minutes_percentiles = np.percentile(minutes, [25,50,75])
                out["p25_trip_acc_{0:s}_min".format(level)] = minutes_percentiles[0]
                out["p50_trip_acc_{0:s}_min".format(level)] = minutes_percentiles[1]
                out["p75_trip_acc_{0:s}_min".format(level)] = minutes_percentiles[2]

        
    for type in ["walk", "bike", "vehicle"]:
        trips = [trip for trip in commute_trips if trip.type == type]
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

            if dataAcc is not None:
                acc_avg_counts_min = [trip.getCountsStats(dataGPS, dataAcc)[1] for trip in trips]
                acc_avg_counts_min = [a for a in acc_avg_counts_min if a!='']
                if len( acc_avg_counts_min ) > 0:
                    out["avg_"+type+"_acc_avg_counts_min"] = np.mean(acc_avg_counts_min)
                    out["std_"+type+"_acc_avg_counts_min"] = np.std(acc_avg_counts_min)
                    out["min_"+type+"_acc_avg_counts_min"] = np.min(acc_avg_counts_min)
                    out["max_"+type+"_acc_avg_counts_min"] = np.max(acc_avg_counts_min)

                    acc_avg_counts_min_percentiles = np.percentile(acc_avg_counts_min, [25,50,75])
                    out["p25_"+type+"_acc_avg_counts_min"] = acc_avg_counts_min_percentiles[0]
                    out["p50_"+type+"_acc_avg_counts_min"] = acc_avg_counts_min_percentiles[1]
                    out["p75_"+type+"_acc_avg_counts_min"] = acc_avg_counts_min_percentiles[2]

                activity_info = [trip.getAccInfo(dataGPS, dataAcc, cp) for trip in trips]
                for level in cp.levels:
                    minutes = [info['trip_acc_{0:s}_min'.format(level)] for info in activity_info]
                    minutes = [m for m in minutes if m!='']
                    if len(minutes) > 0:
                        out["avg_"+type+"_trip_acc_{0:s}_min".format(level)] = np.mean(minutes)
                        out["std_"+type+"_trip_acc_{0:s}_min".format(level)] = np.std(minutes)
                        out["min_"+type+"_trip_acc_{0:s}_min".format(level)] = np.min(minutes)
                        out["max_"+type+"_trip_acc_{0:s}_min".format(level)] = np.max(minutes)

                        minutes_percentiles = np.percentile(minutes, [25,50,75])
                        out["p25_"+type+"_trip_acc_{0:s}_min".format(level)] = minutes_percentiles[0]
                        out["p50_"+type+"_trip_acc_{0:s}_min".format(level)] = minutes_percentiles[1]
                        out["p75_"+type+"_trip_acc_{0:s}_min".format(level)] = minutes_percentiles[2]
            
    return out
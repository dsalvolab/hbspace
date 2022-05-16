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

from hbspace import *

import matplotlib
matplotlib.use('WebAgg')

import os 
import csv


import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    
    parameters = defaultParameters()
    #fname = 'data/GPS/T1_002_GPS.csv'
    #fname = 'data/GPS/T1_056_GPS.csv'
    #fname = 'data/GPS/T1_005_GPS.csv'
    fname = 'data/GPS/T1_004_GPS.csv'
    #fname = 'data/GPS/T1_055_GPS.csv'
    #fname= 'data/GPS/T1_066_GPS.csv'
    fname = 'data/GPS/T1_012_GPS.csv'
    rawdata = RawGPSData(fname, logging=True)
    print("Data ", rawdata.id)
        
    data = rawdata.getCleanData(parameters["invalid_fixes"])
    data.trip_detection(parameters["trip"])
    data.classify_trip(parameters["speed"])
    data.location_detection(parameters["location"])
    tot_time_hours, tot_valid_time_hours, tot_invalid_time_hours = data.measurement_time()
    print("Tot time: {0}, Valid time: {1}, Invalid time: {2}".format(tot_time_hours, tot_valid_time_hours, tot_invalid_time_hours) )
    print("Fixes", rawdata.is_valid.shape[0], "Invalid fixes ratio", 1.- np.sum(rawdata.is_valid)/rawdata.is_valid.shape[0])
    print("Lone fixes", np.sum(rawdata.is_first_fix*rawdata.is_last_fix))
    print("N First fixes", np.sum(data.is_first_fix))
    print("N Last fixes", np.sum(data.is_last_fix))
    print("First fixes", np.where(data.is_first_fix)[0])
    print("Last fixes", np.where(data.is_last_fix)[0])
    ufixes = np.where( (data.trip_marker==-1) * (data.location_marker==-1) * (data.is_valid==1) )
    print("UnassignedFix", ufixes)
    print("UnassignedFixState", data.state[ufixes])
    print("\n")
    
    print( len(data.trip_type) )
    print( data.timestamps.shape[0])
    
    GISlog_writer(data, fname, './')
    
    summary_fname = "summary.csv"
    summary_fid = open(summary_fname, "w", newline='')
    summary = csv.DictWriter(summary_fid, trip_stats_headers())
    summary.writeheader()
    summary.writerow(trip_stats(data))
        
    trips_fname = "trips_long.csv"
    trips_fid   = open(trips_fname, "w", newline='')
    trips_out       = csv.DictWriter(trips_fid, Trip.infoKeys())
    trips_out.writeheader()
    [ trips_out.writerow(trip.getInfo(data)) for trip in data.trips ] 

    locations_fname = "locations_long.csv"
    locations_fid   = open(locations_fname, "w", newline='')
    locations_out       = csv.DictWriter(locations_fid, Location.infoKeys())
    locations_out.writeheader()
    [ locations_out.writerow(location.getInfo(data)) for location in data.locations ]
    
    visit_fname = "visits_long.csv"
    visit_fid   = open(visit_fname, "w", newline='')
    visit_out       = csv.DictWriter(visit_fid, Visit.infoKeys())
    visit_out.writeheader()
    [ visit_out.writerow(visit.getInfo(data)) for visit in data.visits]
    
    plt.figure()
    plt.hist(data.speeds, log=True)
    plt.figure()
    plt.plot(data.timestamps, data.cumdist)
    #plt.figure()
    #plt.plot(data.timestamps, data.crowdist)
    plt.show()

    

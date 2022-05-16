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
import os 

import csv

if __name__ == '__main__':
    
    home_addresses = homeAddresses('data/FRESH_HomeAddress_XY.csv')
    store_addresses = storeAddresses('data/FRESH_FoodStores_XY.csv')
    
    folder = "data/GPS"
    fnames =  [os.path.join(folder, f) for f in os.listdir(folder) if os.path.splitext( f )[1] == ".csv"]
    
    fnames = sorted(fnames)
    
    folder_out = "data/out"
    
    parameters = defaultParameters()
    
    invalid_fixes_ratio = np.zeros(len(fnames))
    lone_fixes           = np.zeros(len(fnames))
    first_fixes          = np.zeros(len(fnames))
    tot_hours            = np.zeros(len(fnames))
    valid_hours          = np.zeros(len(fnames))
    sloss_hours          = np.zeros(len(fnames))
    
    #zone = 22
    #proj = UTMprojection(zone=zone)
    
    counter = 0
    
    summary_fname = "summary.csv"
    summary_fid = open(summary_fname, "w", newline='')
    summary = csv.DictWriter(summary_fid, trip_stats_headers())
    summary.writeheader()
    
    trips_fname = "trips_long.csv"
    trips_fid   = open(trips_fname, "w", newline='')
    trips_out       = csv.DictWriter(trips_fid, Trip.infoKeysExt())
    trips_out.writeheader()
    
    locations_fname = "locations_long.csv"
    locations_fid   = open(locations_fname, "w", newline='')
    locations_out       = csv.DictWriter(locations_fid, Location.infoKeysExt())
    locations_out.writeheader()
    
    visit_fname = "visits_long.csv"
    visit_fid   = open(visit_fname, "w", newline='')
    visit_out       = csv.DictWriter(visit_fid, Visit.infoKeysExt())
    visit_out.writeheader()
    
    tripCounter     = 0
    locationCounter = 0
    visitCounter    = 0
         
    for fname in fnames:
        print(fname)
        
        partId = filename2partId(fname)
        
        rawdata = RawGPSData(fname)
                
        print("Data ", rawdata.id)
        data = rawdata.getCleanData(parameters["invalid_fixes"])
        data.tripCounter     = tripCounter
        data.locationCounter = locationCounter
        data.visitCounter    = visitCounter
        print("Total fix {0}, Valid fix {1}".format(rawdata.is_valid.shape[0], np.sum(rawdata.is_valid==1)))
        data.id = partId
        data.mark_home(home_addresses[partId], radius=50)
        data.mark_store(store_addresses, radius=50)
        data.trip_detection(parameters["trip"])
        data.classify_trip(parameters["speed"])
        data.location_detection(parameters["location"])
        #data.proj = proj
        
        tripCounter = data.tripCounter 
        locationCounter = data.locationCounter
        visitCounter = data.visitCounter 
        
        GISlog_writer(data, fname, folder_out)
        if len(data.trips):
            summary.writerow(trip_stats(data))
        [ trips_out.writerow(trip.getInfo(data)) for trip in data.trips ]
        if len(data.locations):
            [ locations_out.writerow(location.getInfo(data)) for location in data.locations ]
        if len(data.visits):
            [ visit_out.writerow(visit.getInfo(data)) for visit in data.visits]
        
        invalid_fixes_ratio[counter] = 1.- data.valid_fixes_id.shape[0]/float(data.ntotal_fixes)
        lone_fixes[counter]          = np.sum(data.is_first_fix*data.is_last_fix)
        first_fixes[counter]         = np.sum(data.is_first_fix)
        tot_hours[counter], valid_hours[counter], sloss_hours[counter] = data.measurement_time()
        
        unassignedFixes = np.sum( (data.trip_marker==-1) * (data.location_marker==-1)*(data.is_valid==1) )
        unassignedFixes_ratio = unassignedFixes/float(data.trip_marker.shape[0])
        
        
        print("Total time (hours)", tot_hours[counter], "Valid time (hours)", valid_hours[counter],
               "SLOSS time (hours)", sloss_hours[counter])
        print("Fixes", rawdata.is_valid.shape[0], "Invalid fixes proportion", invalid_fixes_ratio[counter])
        print("Lone fixes", lone_fixes[counter] )
        print("First fixes", first_fixes[counter])
        print("UnassignedFixes: ", unassignedFixes, "Ratio: ", unassignedFixes_ratio)
        if(len(data.visits)):
            print("Max radius location: ", max([v.radius for v in data.visits]))
        if(len(data.trips)):
            print("Min trip duration: ", min([t.duration for t in data.trips]))
            print("Min trip distance traveled: ", min([t.distance for t in data.trips]))
        print("\n")
        counter+=1
        
        
    print("Minimum and maximum proportion of invalid fixes", invalid_fixes_ratio.min(), invalid_fixes_ratio.max())
    print("Minimum and maximum number of lone fixes", lone_fixes.min(), lone_fixes.max())
    print("Minimum and maximum number loss of signal", first_fixes.min()-1, first_fixes.max()-1)
    print("Minimum and maximum total time (hours)", tot_hours.min(), tot_hours.max())
    print("Minimum and maximum valid time (hours)", valid_hours.min(), valid_hours.max())
    print("Minimum and maximum SLOSS ratio", (sloss_hours/tot_hours).min(), (sloss_hours/tot_hours).max())
    
    summary_fid.close()
    trips_fid.close()
    locations_fid.close()


    

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
import csv
import numpy as np
from ..gps.trip import trip_mode
import datetime

def GISlog_writer(gpsData, fname_in, folder_out):
    if gpsData.unordered_source:
        GISlog_writer_unordered(gpsData, fname_in, folder_out)
    else:
        GISlog_writer_ordered(gpsData, fname_in, folder_out)

        
def GISlog_writer_ordered(gpsData, fname_in, folder_out):
    fname_out = os.path.join( folder_out, os.path.basename(fname_in) )
    
    data = []
    
    with open(fname_in, "rU") as fid:
        reader = csv.DictReader(fid)
        counter = 0
        valid_counter = 0
        is_valid = np.zeros(gpsData.ntotal_fixes, dtype=np.int)
        valid_fixes_id = gpsData.valid_fixes_id[gpsData.is_valid==1]
        is_valid[valid_fixes_id] = 1
        
        state = gpsData.state[gpsData.is_valid==1]
        trip_marker = gpsData.trip_marker[gpsData.is_valid==1]
        trip_type = gpsData.trip_type[gpsData.is_valid==1]
        location_marker = gpsData.location_marker[gpsData.is_valid==1]
        visit_marker = gpsData.visit_marker[gpsData.is_valid==1]
        speeds = gpsData.speeds[gpsData.is_valid==1]
        is_first_fix = gpsData.is_first_fix[gpsData.is_valid==1]
        is_last_fix = gpsData.is_last_fix[gpsData.is_valid==1]
        
        is_home = None
        if gpsData.is_home is not None:
            is_home = gpsData.is_home[gpsData.is_valid==1]
            
        store_id = None
        store_marker = None
        if gpsData.store_id is not None:
            store_id = gpsData.store_id[gpsData.is_valid==1]
            store_marker = gpsData.store_marker[gpsData.is_valid==1]
        
        for row in reader:
            row["State"] = ""
            row["Trip_ID"] = ""
            row["Location_ID"] = ""
            row["Trip_Type"] = ""
            row["Visit_ID"] = ""
            row["FixType"] = ""
            if is_home is not None:
                row["IsHome"] = ""
            if store_id is not None:
                row["StoreId"] = ""
                row["IsFreshStore"] = ""
            if is_valid[counter] == 1:
                row["State"] = state[valid_counter]
                if trip_marker[valid_counter] > -1:
                    row["Trip_ID"] = trip_marker[valid_counter]+1
                    row["Trip_Type"] = trip_mode[trip_type[valid_counter]]
                if location_marker[valid_counter] > -1:
                    row["Location_ID"] = location_marker[valid_counter]+1
                    row["Visit_ID"]    = visit_marker[valid_counter]+1
                if is_first_fix[valid_counter]:
                    row["FixType"] = "f"
                if is_last_fix[valid_counter]:
                    row["FixType"] = "l"
                    
                if is_home is not None:
                    row["IsHome"] = is_home[valid_counter]
                    
                if store_id is not None:
                    if store_id[valid_counter] > -1:
                        row["StoreId"]      = store_id[valid_counter]
                        row["IsFreshStore"] = store_marker[valid_counter]
                                        
                row["SPEED"] = speeds[valid_counter]

                data.append(row)
                valid_counter +=1
            counter += 1
    
    with open(fname_out, "w", newline='') as fid:
        writer = csv.DictWriter(fid, row.keys())
        
        writer.writeheader()
        
        for d in data:
            writer.writerow(d)

def GISlog_writer_commuter(gpsData, fname_out):

    fieldnames = ['partid', 'tripid', 'Outbound_inbound',
                  'trip_type', 'fixid', 'fixdate', 'fixtime',
                  'fixlat', 'fixlon', 'speed']

    partid = gpsData.id

    with open(fname_out, "w", newline='') as fid:
        writer = csv.DictWriter(fid, fieldnames)
        writer.writeheader()
        for trip in gpsData.trips:
            tripid = trip.id
            triptype = trip.type
            outbound_inbound = trip.Outbound_Inbound(gpsData)
            for index in np.arange(trip.start_index, trip.last_index+1):
                row = {}
                row['partid'] = partid
                row['tripid'] = tripid
                row['Outbound_inbound'] = outbound_inbound
                row['trip_type'] = triptype
                row['fixid']   = index
                row['fixdate'] = gpsData.local_datetime[index].strftime('%Y-%m-%d')
                row['fixtime'] = gpsData.local_datetime[index].strftime('%H:%M:%S')
                row['fixlat']  = gpsData.latitudes[index]
                row['fixlon']  = gpsData.longitudes[index]
                row['speed']   = gpsData.speeds[index]

                writer.writerow(row)

def GISlog_writer_commuter2(gpsData, fname_out):

    fieldnames = ['partid', 'fixid', 'fixdate', 'fixtime', 'fixlat','fixlon', 'speed',
                  'fixstate', 'is_home', 'is_dest',
                  'tripid', 'Outbound_inbound', 'trip_type']

    partid = gpsData.id

    with open(fname_out, "w", newline='') as fid:
        writer = csv.DictWriter(fid, fieldnames)
        writer.writeheader()

        for index in np.arange(gpsData.latitudes.shape[0]):
            row = {}
            row['partid'] = partid
            row['fixid']   = index
            row['fixdate'] = gpsData.local_datetime[index].strftime('%Y-%m-%d')
            row['fixtime'] = gpsData.local_datetime[index].strftime('%H:%M:%S')
            row['fixlat']  = gpsData.latitudes[index]
            row['fixlon']  = gpsData.longitudes[index]
            row['speed']   = gpsData.speeds[index]
            row['fixstate']= gpsData.state[index]
            row['is_home'] = gpsData.is_home[index]
            row['is_dest'] = gpsData.is_dest[index]
            if gpsData.trip_marker[index] > -1:
                row["tripid"] = gpsData.trip_marker[index]+1
                row["trip_type"] = trip_mode[gpsData.trip_type[index]]
                row['Outbound_inbound'] = gpsData.trip_outbound_inbound[index]
            else:
                row["tripid"] = ''
                row["trip_type"] = ''
                row['Outbound_inbound'] = ''

            writer.writerow(row)

            
def get_datetime_std(datestr, timestr):
    datetime_str = datestr + " " + timestr
    
    formats = ("%Y/%m/%d %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%m/%d/%y %H:%M:%S")
    
    for f in formats:
        try:
            return datetime.datetime.strptime(datetime_str,f).strftime("%Y-%m-%d %H:%M:%S")
            break
        except:
            pass
        
    raise
            
def GISlog_writer_unordered(gpsData, fname_in, folder_out):
    fname_out = os.path.join( folder_out, os.path.basename(fname_in) )
    
    data = {}
    
    with open(fname_in, "rU") as fid:
        reader = csv.DictReader(fid)
                
        for row in reader:
            if "LOCAL_DATE" in row.keys():
                date_num =get_datetime_std(row["LOCAL_DATE"], row["LOCAL_TIME"])
            else:
                date_num = get_datetime_std(row["LOCAL DATE"], row["LOCAL TIME"])
            if date_num not in data.keys():
                data[date_num] = row
    
    row["State"] = ""
    row["Trip_ID"] = ""
    row["Location_ID"] = ""
    row["Trip_Type"] = ""
    row["Visit_ID"] = ""
    row["FixType"]  = ""
    if gpsData.is_home is not None:
        row["IsHome"] = ""
    if gpsData.store_id is not None:
        row["StoreId"] = ""
        row["IsFreshStore"] = ""
         
    keywords = row.keys()    
    with open(fname_out, "w", newline='') as fid:
        writer = csv.DictWriter(fid, keywords)
        writer.writeheader()
        for gps_counter in np.arange(gpsData.timestamps.shape[0]):
            if gpsData.is_valid[gps_counter]==0:
                continue
            key = gpsData.local_datetime[gps_counter].strftime("%Y-%m-%d %H:%M:%S")
                            
            row = data[key]
            row["State"] = gpsData.state[gps_counter]
            row["Trip_ID"] = ""
            row["Location_ID"] = ""
            row["Trip_Type"] = ""
            row["Visit_ID"] = ""
            row["FixType"]  = ""
            if gpsData.is_home is not None:
                row["IsHome"] = ""
            if gpsData.store_id is not None:
                row["StoreId"] = ""
                row["IsFreshStore"] = ""

            if gpsData.trip_marker[gps_counter] > -1:
                row["Trip_ID"] = gpsData.trip_marker[gps_counter]+1
                row["Trip_Type"] = trip_mode[gpsData.trip_type[gps_counter]]
            if gpsData.location_marker[gps_counter] > -1:
                row["Location_ID"] = gpsData.location_marker[gps_counter]+1
                row["Visit_ID"]    = gpsData.visit_marker[gps_counter]+1
            if gpsData.is_first_fix[gps_counter] == 1:
                row["FixType"] = "f"
            if gpsData.is_last_fix[gps_counter] == 1:
                row["FixType"] = "l"
                
            if gpsData.is_home is not None:
                row["IsHome"] = gpsData.is_home[gps_counter]
                    
                if gpsData.store_id is not None:
                    if gpsData.store_id[gps_counter] > -1:
                        row["StoreId"]      = gpsData.store_id[gps_counter]
                        row["IsFreshStore"] = gpsData.store_marker[gps_counter]
                                        
            row["SPEED"] = gpsData.speeds[gps_counter]

            writer.writerow(row)
                
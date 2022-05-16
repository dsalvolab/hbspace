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
import os

def storeAddresses(fname):
    store_addresses = {}
    with open(fname, 'r') as fid:
        reader = csv.DictReader(fid)
        for row in reader:
            storeId   = int(row['STORE_ID'])
            latitude  = float(row['Y'])
            longitude = float(row['X'])
            isFresh   = int(row['FreshForLess'])
            
            store_addresses[storeId] = (latitude, longitude, isFresh)
        
    return store_addresses
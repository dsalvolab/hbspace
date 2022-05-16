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

def filename2partId(fname):
    base = os.path.basename(fname)
    partId = int(base[3:6])
    return partId

def homeAddresses(fname):
    home_addresses = {}
    with open(fname, 'r') as fid:
        reader = csv.DictReader(fid)
        for row in reader:
            partId    = int(row['FRESHID'])
            latitude  = float(row['Y'])
            longitude = float(row['X'])
            home_addresses[partId] = (latitude, longitude)
        
    return home_addresses
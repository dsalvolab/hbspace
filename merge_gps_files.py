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
    
    folder = "data/out"
    fnames =  [os.path.join(folder, f) for f in os.listdir(folder) if os.path.splitext( f )[1] == ".csv"]
    
    fnames = sorted(fnames)
    
    with open(fnames[0], 'r') as fid:
        reader = csv.DictReader(fid)
        fieldnames = ['PartId'] + reader.fieldnames
        
    fout = open('gps_all.csv', "w", newline='')
    writer = csv.DictWriter(fout, fieldnames)
    writer.writeheader()
         
    for fname in fnames:
        print(fname)
        with open(fnames[0], 'r') as fid:
            reader = csv.DictReader(fid)
            for row in reader:
                row['PartId'] = filename2partId(fname)
                writer.writerow(row)
        


    

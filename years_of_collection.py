from hbspace import *
import os 
import csv
import datetime
import numpy as np
import pathlib


if __name__ == '__main__':
    fname = '../STREETS_main.csv'
    years = {}
    with open(fname, newline='') as fid:
        reader = csv.DictReader(fid)
        for info in reader:
            pid = info['part_id']
            print('Read', pid)

            if info['GPS_data_avail'] == 0:
                print("SKIP: Participant {0:s} - no GPS data available".format(pid))
                continue

            if info['GPS_filename'] == '':
                print("SKIP: Participant {0:s} - no GPS filename is empty".format(pid))
                continue
                
            raw_gps = RawGPSData(info['GPS_filename'], pid, filtered=True)
            dft = raw_gps.local_datetime[0].astype(datetime.datetime)

            if dft.year in years:
                years[dft.year]= years[dft.year]+1
            else:
                years[dft.year] = 1

    for y, count in years.items():
        print('{0:d}: {0:d}'.format(y, count))



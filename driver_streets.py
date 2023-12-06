from hbspace import *
import os 
import csv
import datatime
import numpy as np

if __name__ == '__main__':
    fname = '../STREETS_main.csv'

    weekdays = np.ones(7)
    weekdays[5:6] = 0
    inbound_start = datatime.time(hour=6, minute=30, second=0)
    inbound_end = datatime.time(hour=8, minute=0, second=0)
    outbound_start = datatime.time(hour=14, minute=30, second=0)
    outbound_end = datatime.time(hour=18, minute=30, second=0)
    inbound_toi  = TimeOfInterest(inbound_start, inbound_end, weekdays)
    outbound_toi = TimeOfInterest(outbound_start, outbound_end, weekdays)

    with open(fname, newline='') as fid:
        reader = csv.DictReader(fid)
        for r in reader:
            analyze_participant(r)


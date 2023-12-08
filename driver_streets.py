from hbspace import *
import os 
import csv
import datetime
import numpy as np
import pathlib
import typing

class STATUS:
    success      = 1
    noGPSfile    = -1
    GPSunsorted  = -2


def analyze_participant(info, toi, schools, parameters, outfiles) -> typing.Dict[str, typing.Any]:
    #,x_part,y_part,school_id,x_sch,y_sch,GPS_data_avail,GPS_filename,ACC_data_avail,ACC_filename,Everbike
    pid = info['part_id']
    school_id = info['school_id']
    print('Analysing participant {0:s} from school {1:s}'.format(pid, school_id))
    print('Home: {0:f}, {1:f}'.format(float(info['x_part']), float(info['y_part'])))
    home = AreaOfInterest('home', float(info['y_part']), float(info['x_part']), 30.)
    school = schools[school_id]

    if info['GPS_data_avail'] in ['0', 0]:
        print("SKIP: Participant {0:s} - no GPS data available".format(pid))
        return {'part_id': pid, 'status': STATUS.noGPSfile}

    raw_gps = RawGPSData(info['GPS_filename'], pid, years_of_collection = [2018, 2022])
    success = raw_gps.read_fromQTravel(tryfix=False)

    if success == 0:
        print("SKIP: Participant {0:s} - GPS data not sorted".format(pid))
        return {'part_id': pid, 'status': STATUS.GPSunsorted}

    raw_gps.selectTimeFrames(toi)
    gps = raw_gps.getCleanData(parameters["invalid_fixes"], CommuteGPSData)
    gps.mark_home(home)
    print('Percentage of fixes at home: ', gps.is_home.mean())
    gps.mark_dest(school)
    print('Percentage of fixes at destination: ', gps.is_dest.mean())
    gps.trip_detection(parameters["trip"])
    if info['Everbike'] == 0:
        gps.classify_trip(parameters["speed_no_bike"])
    else:
        gps.classify_trip(parameters["speed"])

    GISlog_writer_commuter(gps, outfiles.gis_log_fname(pid))
    Triplog_writer_commuter(gps, outfiles.trip_log_fname(pid))

    return {'part_id': pid, 'status': STATUS.success} 
    

class Outfiles:
    def __init__(self):
        self.gis_log_fname_ = '../gis_log/log_{0:s}.csv'
        self.trip_log_fname_ = '../trip_log/trip_{0:s}.csv'
        pathlib.Path('../gis_log').mkdir(parents=False, exist_ok=True)
        pathlib.Path('../trip_log').mkdir(parents=False, exist_ok=True)

    def gis_log_fname(self, part_id):
        return self.gis_log_fname_.format(part_id)
    
    def trip_log_fname(self, part_id):
        return self.trip_log_fname_.format(part_id)


if __name__ == '__main__':
    fname = '../STREETS_main.csv'
    school_fname = '../STREETS_schools_ER.csv'
    outfiles = Outfiles()

    parameters = defaultParameters()

    weekdays = np.ones(7)
    weekdays[5:6] = 0
    inbound_start = datetime.time(hour=6, minute=30, second=0)
    inbound_end = datetime.time(hour=8, minute=0, second=0)
    outbound_start = datetime.time(hour=14, minute=30, second=0)
    outbound_end = datetime.time(hour=18, minute=30, second=0)
    inbound_toi  = TimeFrameWindow(inbound_start, inbound_end, weekdays)
    outbound_toi = TimeFrameWindow(outbound_start, outbound_end, weekdays)
    toi = TimeFrame([inbound_toi,outbound_toi])

    schools = parse_areas_of_interest(school_fname, ['school_id','y_sch','x_sch','radius_m'])

    report_fid = open('report.csv', 'w', newline='')
    reportWriter = csv.DictWriter(report_fid, fieldnames=['part_id', 'status'])
    reportWriter.writeheader()

    with open(fname, newline='') as fid:
        reader = csv.DictReader(fid)
        for r in reader:
            status = analyze_participant(r, toi, schools, parameters, outfiles)
            reportWriter.writerow(status)



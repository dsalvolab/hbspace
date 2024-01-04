from hbspace import *
import os 
import csv
import datetime
import numpy as np
import pathlib
import typing

class STATUS:
    success         = 1
    noGPSfile       = -1
    GPSunsorted     = -2
    GPS_no_fixes    = -3
    excluded_school = -4
    noHomeAddress   = -5
    unknown_parsing_error  = -101
    unknown_cleaning_error = -102


def analyze_participant(info, toi, schools, paddresses, cut_points_intensity, parameters, outfiles, summaryWriter) -> typing.Dict[str, typing.Any]:
    #,x_part,y_part,school_id,x_sch,y_sch,GPS_data_avail,GPS_filename,ACC_data_avail,ACC_filename,Everbike
    pid = info['part_id']
    school_id = info['school_id']
    if school_id == '246913114':
        print('School ID 246913114 was excluded by design')
        return {'part_id': pid, 'status': STATUS.noGPSfile}
    
    print('Analysing participant {0:s} from school {1:s}'.format(pid, school_id))
    if pid not in paddresses:
        print("SKIP: Participant {0:s} - no home address available".format(pid))
        return {'part_id': pid, 'status': STATUS.noHomeAddress}
    
    home = paddresses[pid]
    if home.radius < 30:
        home.radius = 30.
    school = schools[school_id]

    if info['GPS_data_avail'] in ['0', 0]:
        print("SKIP: Participant {0:s} - no GPS data available".format(pid))
        return {'part_id': pid, 'status': STATUS.noGPSfile}

    raw_gps = RawGPSData(info['GPS_filename'], pid, years_of_collection = [2018, 2022])

    try:
        success = raw_gps.read_fromQTravel(tryfix=False)
    except:
        print("SKIP: Participant {0:s} - Unknown exception".format(pid))
        return {'part_id': pid, 'status': STATUS.unknown_parsing_error}

    if success == 0:
        print("SKIP: Participant {0:s} - GPS data not sorted".format(pid))
        return {'part_id': pid, 'status': STATUS.GPSunsorted}

    status = raw_gps.selectTimeFrames(toi)
    if status == -1:
        print("SKIP: Participant {0:s} - No fixes in window".format(pid))
        return {'part_id': pid, 'status': STATUS.GPS_no_fixes}
    
    try:
        gps = raw_gps.getCleanData(parameters["invalid_fixes"], CommuteGPSData)
    except Exception:
        print("SKIP: Participant {0:s} - Unknown cleaning exception".format(pid))
        return {'part_id': pid, 'status': STATUS.unknown_cleaning_error}
    tdiff = gps.local_datetime[-1] - gps.local_datetime[0]
    print('Days: ', tdiff.days+1)
    gps.mark_home(home)
    print('Percentage of fixes at home: ', gps.is_home.mean())
    gps.mark_dest(school)
    print('Percentage of fixes at destination: ', gps.is_dest.mean())
    gps.trip_detection(parameters["trip"])
    if info['Everbike'] == 0:
        gps.classify_trip(parameters["speed_no_bike"])
    else:
        gps.classify_trip(parameters["speed_kid"])

    print('Percentage of fixes at home (after trapping): ', gps.is_home.mean())
    print('Percentage of fixes at destination (after trapping): ', gps.is_dest.mean())

    if info['ACC_data_avail'] in ['0', 0]:
        acc = None
    else:
        acc = AccelerometerData.fromMatFile(info['ACC_filename'], pid)

    GISlog_writer_commuter2(gps, outfiles.gis_log_fname(pid))

    if info['ACC_data_avail'] in ['0', 0]:
        Triplog_writer_commuter(gps, outfiles.trip_log_fname(pid))
    else:
        TriplogAcc_writer_commuter(gps, acc, cut_points_intensity, outfiles.trip_log_fname(pid))

    summary_stats = commute_trip_stats(gps, acc, cut_points_intensity)
    summaryWriter.writerow(summary_stats)


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
    address_fname = '../STREETS_cohort_participant_addresses_FIXED_12-21-2023.csv'

    cut_points_intensity = CutPoints.Evenson()

    outfiles = Outfiles()

    parameters = defaultParameters()

    weekdays = np.ones(7)
    weekdays[5:6] = 0
    inbound_start = datetime.time(hour=6, minute=30, second=0)
    inbound_end = datetime.time(hour=9, minute=0, second=0)
    outbound_start = datetime.time(hour=14, minute=30, second=0)
    outbound_end = datetime.time(hour=18, minute=30, second=0)
    inbound_toi  = TimeFrameWindow(inbound_start, inbound_end, weekdays)
    outbound_toi = TimeFrameWindow(outbound_start, outbound_end, weekdays)
    toi = TimeFrame([inbound_toi,outbound_toi])

    schools = parse_areas_of_interest(school_fname, ['school_id','y_sch','x_sch','radius_m'])
    part_addresses = parse_areas_of_interest(address_fname, ['participant_id', 'y_latitude', 'x_longitude', 'Radius_m'])

    report_fid = open('report.csv', 'w', newline='')
    reportWriter = csv.DictWriter(report_fid, fieldnames=['part_id', 'status'])
    reportWriter.writeheader()

    summary_fid = open('summary.csv', 'w', newline='')
    summaryWriter = csv.DictWriter(report_fid, fieldnames=commute_trip_stats_headers(cut_points_intensity))
    summaryWriter.writeheader()

    with open(fname, newline='') as fid:
        reader = csv.DictReader(fid)
        for r in reader:
            status = analyze_participant(r, toi, schools, part_addresses, cut_points_intensity, parameters, outfiles, summaryWriter)
            reportWriter.writerow(status)



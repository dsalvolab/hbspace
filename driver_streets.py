from hbspace import *
import os 
import csv
import datetime
import numpy as np
import pathlib
import typing

class STATUS:
    success                     = 1
    excluded_school             = -1
    missing_school              = -2
    home_too_close_to_school    = -3
    home_too_far_from_school    = -4
    noACCfile                   = -100
    noGPSfile                   = -200
    GPSunsorted                 = -201
    GPS_no_fixes                = -202
    GPS_no_fixes_after_cleaning = -203
    GPS_incorrect_headers       = -204
    GPS_empty                   = -205 
    unknown_GPS_sorting_error   = -206
    unknown_GPS_cleaning_error  = -207

def report_keys():
    return ['part_id', 'status', 'home2school_distance',
            'days', 'weekdays',
            'fraction_fixes_home', 'fraction_fixes_school',
            'estimated_h2s_trips', 'estimated_s2x_trips']


def analyze_participant(info, schools, tois, cut_points_intensity, parameters, outfiles, summaryWriter) -> typing.Dict[str, typing.Any]:
    years_of_collection = [2018, 2022]
    # Participant ID
    pid = info['participant_id']

    ret_val = {k: '' for k in report_keys()}
    ret_val['part_id'] = pid
    ret_val['status'] = STATUS.success

    # Get school information
    school_id = info['school_id']

    if school_id == '':
        print('Missing school info for participant ', pid)
        ret_val['status'] = STATUS.missing_school
        return ret_val


    if school_id == '246913114':
        print('School ID 246913114 was excluded by design')
        ret_val['status'] = STATUS.excluded_school
        return ret_val
    
    print('Analysing participant {0:s} from school {1:s}'.format(pid, school_id))

    try:
        school = schools[school_id]
    except:
        print('School ID {school_id} was not found')
        ret_val['status'] = STATUS.excluded_school
        return ret_val
    
    if school.radius < 30:
        school.radius = 30.
   
    # Home address
    home = AreaOfInterest("home", float(info["y_latitude"]), 
                                  float(info["x_longitude"]), 
                                  float(info["Radius_m"]))
    if home.radius < 30:
        home.radius = 30.

    h2s_distance, intersects = home.intersects(school)
    ret_val['home2school_distance'] = h2s_distance

    if intersects:
        print("SKIP: Participant {0:s} - home too close to school".format(pid))
        ret_val['status'] = STATUS.home_too_close_to_school
        return ret_val
    
    if h2s_distance > 2000:
        print("SKIP: Participant {0:s} - home too far from school: {1:f} meters".format(pid, h2s_distance))
        ret_val['status'] = STATUS.home_too_far_from_school
        return ret_val
    
    # Start and end dates
    if info["has_dates"]:
        try:
            start_date = datetime.datetime.strptime(info["start_date"], "%m/%d/%Y")
        except:
            print("WARNING: Participant {0:s} - Can not parse start date {1:s}".format(pid, info["start_date"]) )
            start_date = None

        try:
            end_date = datetime.datetime.strptime(info["end_date"], "%m/%d/%Y")
        except:
            print("WARNING: Participant {0:s} - Can not parse end date {1:s}".format(pid, info["end_date"]))
            end_date = None

        if start_date is None or end_date is None:
            start_date = None
            end_date = None
        else:
            if (end_date - start_date).total_seconds() <= 0.:
                print("WARNING: Participant {0:s} - Invalid dates: {1:s}-{2:s}".format(
                    pid, start_date.strftime("%m/%d/%y"), end_date.strftime("%m/%d/%y")) )
                start_date = None
                end_date = None

            if start_date.year < years_of_collection[0] or start_date.year > years_of_collection[1]:
                print("WARNING: Participant {0:s} - Invalid dates: {1:s}-{2:s}".format(
                    pid, start_date.strftime("%m/%d/%y"), end_date.strftime("%m/%d/%y")) )
                start_date = None
                end_date = None

            if end_date.year < years_of_collection[0] or end_date.year > years_of_collection[1]:
                print("WARNING: Participant {0:s} - Invalid dates: {1:s}-{2:s}".format(
                    pid, start_date.strftime("%m/%d/%y"), end_date.strftime("%m/%d/%y")) )
                start_date = None
                end_date = None
        
    if info['has_ACC'] in ['0', 0]:
        acc = None
        print("SKIP: Participant {0:s} - no ACC data available".format(pid))
        ret_val['status'] = STATUS.noACCfile
        return ret_val
    else:
        acc = AccelerometerData.fromMatFile(info['ACC_filename'], pid)

    if start_date is None:
        assert end_date is None
        start_date = acc.startDate()
        end_date   = acc.endDate()

    acc.trim(start_date, end_date)

    if info['has_GPS'] in ['0', 0]:
        print("SKIP: Participant {0:s} - no GPS data available".format(pid))
        ret_val['status'] = STATUS.noACCfile
        return ret_val

    raw_gps = RawGPSData(info['GPS_filename'], pid, years_of_collection=years_of_collection )


    error = raw_gps.read_fromQTravel()
    if error == -1:
        print("SKIP: Participant {0:s} - Unrecognised GPS header".format(pid))
        ret_val['status'] = STATUS.GPS_incorrect_headers
        return ret_val
    elif error == -2:
        print("SKIP: Participant {0:s} - Corrupted/empty GPS".format(pid))
        ret_val['status'] = STATUS.GPS_empty
        return ret_val       
    
    status = raw_gps.trim(start_date, end_date)

    if status == -1:
        print("SKIP: Participant {0:s} - No fixes in window".format(pid))
        ret_val['status'] = STATUS.GPS_no_fixes
        return ret_val
    
    #try:
    success = raw_gps.sort_times()
    #except:
    #    print("SKIP: Participant {0:s} - Unknown exception".format(pid))
    #    ret_val['status'] = STATUS.unknown_GPS_sorting_error
    #    return ret_val

    if success == 0:
        print("SKIP: Participant {0:s} - GPS data not sorted".format(pid))
        ret_val['status'] = STATUS.GPSunsorted
        return ret_val
        
    #try:
    gps = raw_gps.getCleanData(parameters["invalid_fixes"], CommuteGPSData)
    #except Exception:
    #    print("SKIP: Participant {0:s} - Unknown cleaning exception".format(pid))
    #    ret_val['status'] = STATUS.unknown_GPS_cleaning_error
    #    return ret_val

    if gps.ntotal_fixes < 2:
        print("SKIP: Participant {0:s} - No fixes after cleaning".format(pid))
        ret_val['status'] = STATUS.GPS_no_fixes_after_cleaning
        return ret_val

    print('Date range: ', start_date.strftime('%Y-%m-%d'), " ", end_date.strftime('%Y-%m-%d') )
    
    days = np.unique([d.date() for d in gps.local_datetime])
    
    number_of_days = days.shape[0]
    # Return the day of the week as an integer, where Monday is 0 and Sunday is 6. 
    is_week_day    = np.array([d.weekday() < 5 for d in days])
    weekdays = days[is_week_day]
    number_of_weekdays = weekdays.shape[0]

    ret_val['days']     = number_of_days
    ret_val['weekdays'] = number_of_weekdays

    print("Found {0} days and {1} week-days".format(number_of_days, number_of_weekdays) )

    gps.mark_home(home)
    print('Percentage of fixes at home: ', gps.is_home.mean())
    gps.mark_dest(school)
    print('Percentage of fixes at school: ', gps.is_dest.mean())

    ret_val['fraction_fixes_home'] = gps.is_home.mean()
    ret_val['fraction_fixes_school'] = gps.is_dest.mean()

    estimated_number_of_trips = gps.process_tois(weekdays, tois)

    ret_val['estimated_h2s_trips'] = estimated_number_of_trips[0]
    ret_val['estimated_s2x_trips'] = estimated_number_of_trips[1]

    print('Estimated number of trips: h2s = {0}, s2x = {1}'.format(estimated_number_of_trips[0], estimated_number_of_trips[1]))

    gps.trip_detection(parameters["trip"])
    if info['everbike'] == 0:
        gps.classify_trip(parameters["speed_no_bike"])
    else:
        gps.classify_trip(parameters["speed_kid"])

    print('Percentage of fixes at home (after trapping): ', gps.is_home.mean())
    print('Percentage of fixes at destination (after trapping): ', gps.is_dest.mean())

    ret_val['fraction_fixes_home'] = gps.is_home.mean()
    ret_val['fraction_fixes_school'] = gps.is_dest.mean()



    GISlog_writer_commuter2(gps, outfiles.gis_log_fname(pid))

    if info['has_ACC'] in ['0', 0]:
        Triplog_writer_commuter(gps, outfiles.trip_log_fname(pid))
    else:
        TriplogAcc_writer_commuter(gps, acc, cut_points_intensity, outfiles.trip_log_fname(pid))

    summary_stats = commute_trip_stats(gps, acc, cut_points_intensity)
    summaryWriter.writerow(summary_stats)


    return ret_val 
    

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
    fname = 'STREETS_main.csv'
    base_dir = "/Users/uvilla/Library/CloudStorage/Box-Box/STREETS Device data/Raw Device Data for GPS-ACC matching/Time 1 - data for new code"
    school_fname = os.path.join(base_dir, 'STREETS_schools_ER.csv')

    cut_points_intensity = CutPoints.Evenson()

    outfiles = Outfiles()

    parameters = defaultParameters()

    weekdays = np.ones(7)
    weekdays[5:6] = 0
    h2s_start = datetime.time(hour=6, minute=30, second=0)
    h2s_end = datetime.time(hour=8, minute=30, second=0)
    h2s_toi  = TimeFrameWindow(h2s_start, h2s_end, weekdays)

    s2hx_start = datetime.time(hour=14, minute=30, second=0)
    s2hx_end = datetime.time(hour=18, minute=30, second=0)
    s2hx_toi = TimeFrameWindow(s2hx_start, s2hx_end, weekdays)

    at_home_start = datetime.time(hour=4, minute=30, second=0)
    at_home_end = h2s_start
    at_home_toi = TimeFrameWindow(at_home_start, at_home_end, weekdays)

    at_school_start = h2s_start
    at_school_end   = datetime.time(hour=10, minute=30, second=0)
    at_school_toi_am  =TimeFrameWindow(at_school_start, at_school_end, weekdays)

    at_school_start = datetime.time(hour=12, minute=30, second=0)
    at_school_end = s2hx_start
    at_school_toi_pm  =TimeFrameWindow(at_school_start, at_school_end, weekdays)

    tois = {"at_home_night": at_home_toi,
            "at_school_am": at_school_toi_am,
            "at_school_pm": at_school_toi_pm}

    schools = parse_areas_of_interest(school_fname, ['school_id','y_sch','x_sch','radius_m'])
 
    report_fid = open('report.csv', 'w', newline='')
    reportWriter = csv.DictWriter(report_fid, fieldnames=report_keys())
    reportWriter.writeheader()

    summary_fid = open('summary.csv', 'w', newline='')
    summaryWriter = csv.DictWriter(summary_fid, fieldnames=commute_trip_stats_headers(cut_points_intensity))
    summaryWriter.writeheader()

    with open(fname, newline='') as fid:
        reader = csv.DictReader(fid)
        counter = 0
        success = 0
        for r in reader:
            status = analyze_participant(r,  schools, tois, cut_points_intensity, parameters, outfiles, summaryWriter)
            reportWriter.writerow(status)
            report_fid.flush()
            counter=counter+1
            if status['status'] == 1:
                success = success + status['status']
            print("Participant: ", counter, " Success rate {0:0.2f}%".format(success/counter*100.), )



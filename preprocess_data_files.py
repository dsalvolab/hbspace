import csv
import os
import glob

# Purpose:
# Inputs: participant address files, accelerometry start/end date files, ever bike file, Acc and GPS folder
# Outputs: summary csv file with the following fields:
# participant ID, participant home coordinates, participant school ID, participant start date, participant end date, participant ever bikes, participant acc filename of present, participant gps filename if present

def map_extra_info(path_to_plist_extra, part_id):
    map_extra = {}
    with open(path_to_plist_extra, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:   
            map_extra[ row[part_id] ] = row

    return map_extra

def matchfile(pattern, files):
    match = []
    nmatches = 0
    for f in files:
        if pattern in f:
            match.append(f)
            nmatches += 1

    #Remove matches
    for m in match:
        files.remove(m)

    if nmatches > 1:
        cm = [m for m in match]
        match = []
        for m in cm:
            if '_r_' in m: #GPS
                match = []
                match.append(m)
                break
            elif '_rawgps_r' in m: #GPS
                match = []
                match.append(m)
                break
            elif '_r15sec' in m: #ACC
                match.append(m)
                break
            elif 'rawgps_csv_r' in m:
                match = []
                match.append(m)
                break
            elif 'rawgps_csv.' in m:
                print("Guessing", cm)
                match.append(m)
        assert len(match) > 0, "PID"+ pattern+ ": Lost all matches"+repr(cm)

    if len(match) == 0:
        return None
    elif len(match) == 1:
        return match[0]
    else:
        assert 0, "More than one match:" + repr(match)

def discovery(paths, output):
    gps_files = [f for f in glob.glob(paths["GPSfolder"]+'/*.csv') ]
    print('Found {0:d} gps files'.format(len(gps_files)))
    acc_files = [f for f in glob.glob(paths["ACCfolder"]+'/*.mat')]
    print('Found {0:d} acc files'.format(len(acc_files)))

    map_start_end_date = map_extra_info(paths["part_start_end_date"], 'participant_id')
    print("Participants with start_end_date:", len(map_start_end_date) )
    map_schoolID = map_extra_info(paths["part_school_id"], 'participant_id')
    print("Participants with school ID:", len(map_schoolID) )
    map_everbike = map_extra_info(paths["part_everbike"], 'participant_id')
    print("Participants with everbike:", len(map_everbike) )
    
    outfile = open(output, 'w', newline='')
    p_count = 0
    with open(paths["part_home_address"], newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = [fn for fn in reader.fieldnames]
        fieldnames.append("has_dates")
        fieldnames.append("start_date")
        fieldnames.append("end_date")
        fieldnames.append("school_id")
        fieldnames.append("ever_bike")
        fieldnames.append("ever_walk")
        fieldnames.append("has_GPS")
        fieldnames.append("GPS_filename")
        fieldnames.append('has_ACC')
        fieldnames.append('ACC_filename')

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in reader:
            p_count = p_count+1
            pid = row['participant_id']
            outrow = {key: row[key] for key in row}

            if pid in map_start_end_date:
                pid_extra = map_start_end_date.pop(pid)
                outrow['has_dates'] = 1
                outrow['start_date'] = pid_extra['start_date']
                outrow['end_date'] = pid_extra['end_date']
            else:
                print('ERROR: Participant {0:s} does not have start/end date info'.format(pid))
                outrow['has_dates'] = 0
                outrow['start_date'] = ''
                outrow['end_date'] = ''


            if pid in map_schoolID:
                pid_extra = map_schoolID.pop(pid)
                outrow['school_id'] = pid_extra['school_tea_id']
            else:
                print('ERROR: Participant {0:s} does not have school_id info'.format(pid))
                outrow['school_id'] = ''

            if pid in map_everbike:
                pid_extra = map_everbike.pop(pid)
                if pid_extra['ever_bike'] in ["0", "1"]:
                    outrow['ever_bike'] = pid_extra['ever_bike']
                else:
                    outrow['ever_bike'] = ""
                if pid_extra['ever_walk'] in ["0", "1"]:
                    outrow['ever_walk'] = pid_extra['ever_walk']
                else:
                    outrow['ever_walk'] = ""
            else:
                print('WARNING: Participant {0:s} does not have everbike info'.format(pid))
                outrow['ever_bike'] = ''
                outrow['ever_walk'] = ''

            gps_file = matchfile("_"+pid, gps_files)
            acc_file = matchfile("_"+pid, acc_files)
            if gps_file is None:
                outrow['has_GPS'] = 0
                outrow['GPS_filename'] = ''
            else:
                outrow['has_GPS'] = 1
                outrow['GPS_filename'] = gps_file
            if acc_file is None:
                outrow['has_ACC'] = 0
                outrow['ACC_filename'] = ''
            else:
                outrow['has_ACC'] = 1
                outrow['ACC_filename'] = acc_file

            writer.writerow(outrow)
        
        print('Written {0:d} participants'.format(p_count))

        if (len(map_start_end_date)):
            print('\n Unmatched partid_school_id')
            for k in map_start_end_date:
                print(k, map_start_end_date[k])

        if( len(map_schoolID) ):
            print('\n Unmatched partid_school_id')
            for k in map_schoolID:
                print(k, map_schoolID[k])

        if( len(map_everbike) ):
            print('\n Unmatched partid_everbike')
            for k in map_everbike:
                print(k, map_everbike[k])

        if (len(gps_files)):
            print( gps_files)

        if (len(acc_files)):
            print( acc_files)

if __name__ == "__main__":
    base_dir = "/Users/uvilla/Library/CloudStorage/Box-Box/STREETS Device data/"
    ever_bike_walk_dir = os.path.join(base_dir, "Ever walk and bike")
    common_dir = os.path.join(base_dir,"Raw Device Data for GPS-ACC matching")
    raw_dev_date_dir = os.path.join(base_dir,"Raw Device Data for GPS-ACC matching/ACC & GPS data/Time 2")
    paths = {}
    paths["part_home_address"] = os.path.join(common_dir, 'STREETS_cohort_participant_addresses_FIXED_12-21-2023.csv')
    paths["part_start_end_date"] = os.path.join(raw_dev_date_dir, 'STREETS_t2_accelerometer_startend_8.12.24.csv')
    paths["part_school_id"] = os.path.join(common_dir, 'STREETSCohortPartici-BaselineChild_DATA_2023-07-20_1021_SCHOOLID.csv')
    paths["part_everbike"] = os.path.join(ever_bike_walk_dir,'walk_bike_t2.csv')
    paths["GPSfolder"] =  os.path.join(raw_dev_date_dir,'GPS_RAWCSV')
    paths["ACCfolder"] = os.path.join(raw_dev_date_dir,'ACC/MATLAB')
    output = 'STREETS_main_t2.csv'

    discovery(paths, output)


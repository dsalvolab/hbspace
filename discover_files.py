import csv
import os
import glob

def map_extra_info(path_to_plist_extra, part_id):
    map_extra = {}
    with open(path_to_plist_extra, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:   
            map_extra[ row[part_id] ] = row

    return map_extra

def mathfile(pid, files):
    match = None
    for f in files:
        if pid in f:
            match = f
            break

    return match

def discovery(path_to_plist, path_to_plist_extra, path_to_gps_files, path_to_acc_files, output):
    gps_files = [f for f in glob.glob(path_to_gps_files+'/*.csv') ]
    print('Found {0:d} gps files'.format(len(gps_files)))
    acc_files = [f for f in glob.glob(path_to_acc_files+'/*.mat')]
    print('Found {0:d} acc files'.format(len(acc_files)))

    map_extra = map_extra_info(path_to_plist_extra, 'part_id')
    
    outfile = open(output, 'w', newline='')
    p_count = 0
    with open(path_to_plist, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = [fn for fn in reader.fieldnames]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in reader:
            p_count = p_count+1
            pid = row['part_id']
            outrow = {key: row[key] for key in fieldnames[0:6]}
            if pid in map_extra:
                pid_extra = map_extra[pid]
                outrow['Everbike'] = pid_extra['everbike']
            else:
                print('WARNING: Participant {0:s} does not have extra info'.format(pid))
                outrow['Everbike'] = ''
            gps_file = mathfile(pid, gps_files)
            acc_file = mathfile(pid, acc_files)
            if gps_file is None:
                outrow['GPS_data_avail'] = 0
                outrow['GPS_filename'] = ''
            else:
                outrow['GPS_data_avail'] = 1
                outrow['GPS_filename'] = gps_file
            if acc_file is None:
                outrow['ACC_data_avail'] = 0
                outrow['ACC_filename'] = ''
            else:
                outrow['ACC_data_avail'] = 1
                outrow['ACC_filename'] = acc_file

            writer.writerow(outrow)
        
        print('Written {0:d} participants'.format(p_count))





if __name__ == "__main__":
    path_to_plist = '../STREETS_home_and_school_location.csv'
    path_to_plist_extra = '../STREETS_biking_binary.csv'
    path_to_gps_files = '../GPS Baseline CSV Raw Files'
    path_to_acc_files = '../MATLAB_ACCE/15sec'
    output = '../STREETS_main.csv'

    discovery(path_to_plist, path_to_plist_extra, path_to_gps_files, path_to_acc_files, output)


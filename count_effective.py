import csv
from driver_streets import STATUS

if __name__=='__main__':
    report_fid = open('report.csv', 'r', newline='')
    reportReader = csv.DictReader(report_fid)

    tot_count = 0
    possible_states = {
    1: "success",
    -1: "excluded_school",
    -2: "missing_school", 
    -3: "home_too_close_to_school",
    -4: "home_too_far_from_school",
    -100: "noGPS_or_ACCfile",
    -200: "noGPS_or_ACCfile",
    -201: "GPS_fixes_unsortable",
    -202: "GPS_no_fixes_in_weekdays",
    -203: "GPS_no_fixes_in_weekdays_after_cleaning",
    -204: "GPS_has_incorrect_headers",
    -205: "GPS_empty",
    -206: "unknown_GPS_sorting_error",
    -207: "unknown_GPS_cleaning_error"
    }

    count = {k: 0 for k in possible_states.keys() }
    count_tot = 0
    at_least_one_trip_h2s = 0
    at_least_one_trip_s2x = 0

    for row in reportReader:
        count_tot = count_tot+1
        count[int(row['status'])] = count[int(row['status'])]+1
        try:
            if int(row['estimated_h2s_trips']) >= 1:
                at_least_one_trip_h2s = at_least_one_trip_h2s+1
        except:
            pass
        try:
            if int(row['estimated_s2x_trips']) >= 1:
                at_least_one_trip_s2x = at_least_one_trip_s2x+1
        except:
            pass

    print("Total N: ", count_tot)
    print("Valid N: ", count[1])
    print("With at least one h2s trip N: ", at_least_one_trip_h2s)
    print("With at least one s2x trip N: ", at_least_one_trip_s2x)
    print("------------")
    print("Exclusion reasons")
    print("------------")
    for k in possible_states.keys():
        if k < 0:
            print( possible_states[k], ": ", count[k])
    





import csv
import os
import glob


def extract(input, output):    
    schools = {}
    school_count = 0
    row_count = 0
    fieldnames = ['school_id','x_sch','y_sch']

    with open(input, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row_count = row_count+1
            s_id = row['school_id']
            if s_id in schools:
                data = schools[s_id]
                for field in fieldnames:
                    if( data[field] != row[field] ):
                        print('WARNING: unmatched info for school id: {0:s}; row = {1:d}'.format(s_id, row_count))
            else:
                data = {k: val for (k, val) in row.items() if k in fieldnames}
                schools[s_id] = data
                school_count = school_count+1

        print('Found {0:d} schools'.format(school_count))

        with open(output, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for key, val in schools.items():
                writer.writerow(val)
        

if __name__ == "__main__":
    input = '../STREETS_main.csv'
    output = '../STREETS_schools.csv'

    extract(input, output)


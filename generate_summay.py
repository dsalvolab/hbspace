import csv
import numpy as np
from hbspace import TripDirection

def parse_input(fid):
    reader = csv.DictReader(fid)
    out = {}
    partid = []
    ndays = []
    date = []
    ever_bike = []
    ever_walk = []
    trip_direction = []
    traveled_distance = []
    trip_acc_LPA_min = [] 
    trip_acc_MVPA_min = []
    for row in reader:
        partid.append( row["partid"] )
        ndays.append(int(row["n_days"]))
        date.append(row["trip_start_date"])
        ever_bike.append(row["ever_bike"])
        ever_walk.append(row["ever_walk"])
        trip_direction.append(int(row["trip_direction"]))
        traveled_distance.append(float(row["trip_dist_traveled"]))
        trip_acc_LPA_min.append(float(row["trip_acc_LPA_min"]))
        trip_acc_MVPA_min.append(float(row["trip_acc_MPA_min"])+float(row["trip_acc_VPA_min"]))

    out = lambda: 0
    out.partid = np.array(partid)
    out.ndays  = np.array(ndays)
    out.date   = np.array(date) 
    out.ever_bike = np.array(ever_bike)
    out.ever_walk = np.array(ever_walk)
    out.trip_direction = np.array(trip_direction)
    out.traveled_distance = np.array(traveled_distance)
    out.trip_acc_LPA_min = np.array(trip_acc_LPA_min)
    out.trip_acc_MVPA_min = np.array(trip_acc_MVPA_min)

    return out

def write_summary(output_keys, input, fid):
    writer = csv.DictWriter(fid, fieldnames=output_keys)
    writer.writeheader()

    unique_partid = np.unique(input.partid)
    for i in range(unique_partid.shape[0]):
        partid = unique_partid[i]
        row = {}
        row['partid'] = partid
        indexes = input.partid == partid
        row['ndays'] = (input.ndays[indexes])[0]
        row["ever_bike"] =  (input.ever_bike[indexes])[0]
        row["ever_walk"] =  (input.ever_walk[indexes])[0]
        row["ndays_w_trip"] = np.unique(input.date[indexes]).shape[0]

        part_trip_direction = input.trip_direction[indexes]
        row["ndays_w_h2s_trip"] = np.sum(part_trip_direction==TripDirection.H2D)
        row["ndays_w_s2h_trip"] = np.sum(part_trip_direction==TripDirection.D2H)
        row["ndays_w_s2x_trip"] = np.sum(part_trip_direction==TripDirection.D2X)
        row["ndays_w_s2hx_trip"] = row["ndays_w_s2h_trip"] + row["ndays_w_s2x_trip"]

        part_traveled_distance = input.traveled_distance[indexes]
        part_trip_acc_LPA_min = input.trip_acc_LPA_min[indexes]
        part_trip_acc_MVPA_min = input.trip_acc_MVPA_min[indexes]

        row["avg_travelled_distance"] = np.mean(part_traveled_distance)
        row["ntrips_w_5MVPA"] = np.sum(part_trip_acc_MVPA_min >= 5)
        row["ntrips_w_10MVPA"] = np.sum(part_trip_acc_MVPA_min >= 10)
        row["avg_min_MVPA_trip"] = np.mean(part_trip_acc_MVPA_min)
        row["tot_min_MVPA_trip"] = np.sum(part_trip_acc_MVPA_min)
        row["avg_min_LPA_trip"] = np.mean(part_trip_acc_LPA_min)
        row["tot_min_LPA_trip"] = np.sum(part_trip_acc_LPA_min)


        if row["ndays_w_h2s_trip"] > 0:
            dir_indexes = part_trip_direction==TripDirection.H2D
            row["avg_travelled_distance_h2s"] = np.mean(part_traveled_distance[dir_indexes])
            row["ntrips_w_5MVPA_h2s"] = np.sum(part_trip_acc_MVPA_min[dir_indexes] >= 5)
            row["ntrips_w_10MVPA_h2s"] = np.sum(part_trip_acc_MVPA_min[dir_indexes] >= 10)
            row["avg_min_MVPA_trip_h2s"] = np.mean(part_trip_acc_MVPA_min[dir_indexes])
            row["tot_min_MVPA_trip_h2s"] = np.sum(part_trip_acc_MVPA_min[dir_indexes])
            row["avg_min_LPA_trip_h2s"] = np.mean(part_trip_acc_LPA_min[dir_indexes])
            row["tot_min_LPA_trip_h2s"] = np.sum(part_trip_acc_LPA_min[dir_indexes])
        else:
            row["avg_travelled_distance_h2s"] = ""
            row["ntrips_w_5MVPA_h2s"] = ""
            row["ntrips_w_10MVPA_h2s"] = ""
            row["avg_min_MVPA_trip_h2s"] = ""
            row["tot_min_MVPA_trip_h2s"] = ""
            row["avg_min_LPA_trip_h2s"] = ""
            row["tot_min_LPA_trip_h2s"] = ""

        if row["ndays_w_s2h_trip"] > 0:
            dir_indexes = part_trip_direction==TripDirection.D2H
            row["avg_travelled_distance_s2h"] = np.mean(part_traveled_distance[dir_indexes])
            row["ntrips_w_5MVPA_s2h"] = np.sum(part_trip_acc_MVPA_min[dir_indexes] >= 5)
            row["ntrips_w_10MVPA_s2h"] = np.sum(part_trip_acc_MVPA_min[dir_indexes] >= 10)
            row["avg_min_MVPA_trip_s2h"] = np.mean(part_trip_acc_MVPA_min[dir_indexes])
            row["tot_min_MVPA_trip_s2h"] = np.sum(part_trip_acc_MVPA_min[dir_indexes])
            row["avg_min_LPA_trip_s2h"] = np.mean(part_trip_acc_LPA_min[dir_indexes])
            row["tot_min_LPA_trip_s2h"] = np.sum(part_trip_acc_LPA_min[dir_indexes])
        else:
            row["avg_travelled_distance_s2h"] = ""
            row["ntrips_w_5MVPA_s2h"] = ""
            row["ntrips_w_10MVPA_s2h"] = ""
            row["avg_min_MVPA_trip_s2h"] = ""
            row["tot_min_MVPA_trip_s2h"] = ""
            row["avg_min_LPA_trip_s2h"] = ""
            row["tot_min_LPA_trip_s2h"] = ""

        if row["ndays_w_s2x_trip"] > 0:
            dir_indexes = part_trip_direction==TripDirection.D2X
            row["avg_travelled_distance_s2x"] = np.mean(part_traveled_distance[dir_indexes])
            row["ntrips_w_5MVPA_s2x"] = np.sum(part_trip_acc_MVPA_min[dir_indexes] >= 5)
            row["ntrips_w_10MVPA_s2x"] = np.sum(part_trip_acc_MVPA_min[dir_indexes] >= 10)
            row["avg_min_MVPA_trip_s2x"] = np.mean(part_trip_acc_MVPA_min[dir_indexes])
            row["tot_min_MVPA_trip_s2x"] = np.sum(part_trip_acc_MVPA_min[dir_indexes])
            row["avg_min_LPA_trip_s2x"] = np.mean(part_trip_acc_LPA_min[dir_indexes])
            row["tot_min_LPA_trip_s2x"] = np.sum(part_trip_acc_LPA_min[dir_indexes])
        else:
            row["avg_travelled_distance_s2x"] = ""
            row["ntrips_w_5MVPA_s2x"] = ""
            row["ntrips_w_10MVPA_s2x"] = ""
            row["avg_min_MVPA_trip_s2x"] = ""
            row["tot_min_MVPA_trip_s2x"] = ""
            row["avg_min_LPA_trip_s2x"] = ""
            row["tot_min_LPA_trip_s2x"] = ""

        writer.writerow(row)




if __name__ == "__main__":
    input_fname = "Time2/trips.csv"
    output_fname = "Time2/summary_trips.csv"

    output_keys = [
        "partid",
        "ndays",
        "ever_bike",
        "ever_walk",
        "ndays_w_trip",
        "ndays_w_h2s_trip",
        "ndays_w_s2x_trip",
        "ndays_w_s2h_trip",
        "ndays_w_s2hx_trip",
        "avg_travelled_distance",
        "avg_travelled_distance_h2s",
        "avg_travelled_distance_s2h",
        "avg_travelled_distance_s2x",
        "ntrips_w_5MVPA",
        "ntrips_w_5MVPA_h2s",
        "ntrips_w_5MVPA_s2h",
        "ntrips_w_5MVPA_s2x",
        "ntrips_w_10MVPA",
        "ntrips_w_10MVPA_h2s",
        "ntrips_w_10MVPA_s2h",
        "ntrips_w_10MVPA_s2x",
        "avg_min_MVPA_trip",
        "avg_min_MVPA_trip_h2s",
        "avg_min_MVPA_trip_s2h",
        "avg_min_MVPA_trip_s2x",
        "avg_min_LPA_trip",
        "avg_min_LPA_trip_h2s",
        "avg_min_LPA_trip_s2h",
        "avg_min_LPA_trip_s2x",
        "tot_min_MVPA_trip",
        "tot_min_MVPA_trip_h2s",
        "tot_min_MVPA_trip_s2h",
        "tot_min_MVPA_trip_s2x",
        "tot_min_LPA_trip",
        "tot_min_LPA_trip_h2s",
        "tot_min_LPA_trip_s2h",
        "tot_min_LPA_trip_s2x"
    ]

    with open(input_fname) as fid:
        input = parse_input(fid)

    with open(output_fname, "w", newline="") as fid:
        write_summary(output_keys, input, fid)
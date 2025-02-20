import click
import pandas as pd
import numpy as np
from typing import List
from itertools import islice
from tqdm import tqdm

from location import LocationPoint

def calculate_accuracy_from_z(z_score:float)->int:
    if abs(z_score) <= 0.5:
        return 80 + (0.5 - abs(z_score))*38
    elif abs(z_score) <= 1:
        return 50 + (1 - abs(z_score))*30
    elif abs(z_score) <= 2:
        return 30 + (2 - abs(z_score))*10
    else:
        return 0

def calculate_mean_std_and_z_scores(input_list:List[LocationPoint]) -> List[LocationPoint]:

    all_zeros = all([item.location == (0,0) for item in input_list])

    if not all_zeros:
        lat_list = []
        lon_list = []
        for item in input_list:
            if item.location != (0,0):
                lat_list.append(item.location[0])
                lon_list.append(item.location[1])

        # remove outliers
        q1_lat = np.percentile(lat_list, 15)
        q3_lat = np.percentile(lat_list, 85)
        q1_lon = np.percentile(lon_list, 15)
        q3_lon = np.percentile(lon_list, 85)

        clean_lat_list = [item for item in lat_list if item >= q1_lat and item <= q3_lat]
        clean_lon_list = [item for item in lon_list if item >= q1_lon and item <= q3_lon]

        lat_avg = np.average(clean_lat_list)
        lon_avg = np.average(clean_lon_list)

        std_lat = np.std(clean_lat_list)
        std_lon = np.std(clean_lon_list)

        total_std = np.sqrt(np.sum(np.power([std_lat,std_lon],2)))

    for item in input_list:
        if item.location == (0,0):
            item.z_dist = -10
            item.tower_jump = "y"
            item.accuracy = 99
        else:
            item.z_dist = (
                np.linalg.norm(np.subtract(list(item.location), [lat_avg, lon_avg])) / total_std if total_std > 0 else 0
            )
            item.tower_jump = "y" if abs(item.z_dist) > 1 else "n"
            item.accuracy = calculate_accuracy_from_z(item.z_dist) if item.tower_jump == "n" else (100 - calculate_accuracy_from_z(item.z_dist))
        item.cluster_avg = (lat_avg,lon_avg) if not all_zeros else None
    return input_list

@click.command()
@click.argument('input_path')
@click.option('-q', '--quantile', default=0.8)
@click.option('-o', '--output_path', default="output.csv")
def process_file(input_path:str, quantile:float, output_path:str):
    """
    Generates an output with the same number of rows as the input file,
    ordered by the input file page and id columns.
    input_path: path to a csv file.
    """
    df = pd.DataFrame()
    with open(input_path, "r") as f:
        print("Opening file...")
        df = pd.read_csv(input_path)
        print("Done.")

    df["Datetime"] = pd.to_datetime(df["Local Date & Time"], format="%m/%d/%y %H:%M")  # convert to python datetime
    df = df.sort_values(by=["Datetime"])
    cleansed_df = df[df["Datetime"].notnull()]  # remove lines without datetime

    # calculates the diff in time between current row and next
    df["DatetimeDelta"] =  cleansed_df["Datetime"] - cleansed_df["Datetime"].shift(1)
    df["DatetimeDelta"] = df["DatetimeDelta"].fillna(0)

    # convert delta to minutes
    df["DatetimeDeltaMinutes"] = df["DatetimeDelta"].apply(lambda x: (x.total_seconds())/60 if x else 0)

    # find how many minutes the specified quantile to group into clusters
    quantile_limit = df["DatetimeDeltaMinutes"].quantile(quantile)
    print(f"Quantile value: {quantile_limit}")
    total_records = len(df.index)
    print(f"Number of input rows: {total_records}")
    point_dict_list = []
    current_cluster = [LocationPoint.from_row(df.iloc[0])]

    for _, row in tqdm(islice(df.iterrows(), 1, total_records), desc="Total Rows:", total=(total_records - 1)):
        if row["DatetimeDeltaMinutes"] < quantile_limit:
            current_cluster.append(LocationPoint.from_row(row))
        else:  # when cluster ends, calculate values for existing cluster and empties list
            point_list = calculate_mean_std_and_z_scores(current_cluster)
            point_dict_list += [item.to_dict() for item in point_list]
            current_cluster = [LocationPoint.from_row(row)]

    result_df = pd.DataFrame(point_dict_list)
    print(f"Total output: {len(result_df.index)}")
    result_df = result_df.sort_values(
        by=["page", "item"], ascending=[True, True]
    )  # reorders output to the same as input
    result_df.to_csv(output_path)


if __name__ == "__main__":
    process_file()

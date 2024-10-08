from typing import Tuple, Any, List
import pandas as pd
import os
from tqdm import tqdm
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from src.helper import *
from pathlib import Path

######################DATASET INFO#########################################
# sampling rate: 7s
# length: 2 years
# unit: watts
# households: 255
# some households are submetered
# Location: United Kingdom
# Source: https://www.nature.com/articles/s41597-021-00921-y


def read_and_preprocess_df(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=["timestamp", "value"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    # set timestamp as index
    df = df.set_index("timestamp")
    df.sort_index(inplace=True)
    # resample to 7s and forward fill up to 35s
    df = df.resample("7s").ffill(limit=7).dropna()

    # check for duplicates
    df = df[~df.index.duplicated(keep="first")]

    return df


# get house name and appliance name from file name
def parse_name(file_name: str) -> Tuple[str, str]:
    file_name = file_name.split("_")
    house_name = file_name[0].replace("home", "IDEAL_")
    appliance_name = file_name[3]
    if appliance_name == "electric-mains":
        appliance_name = "aggregate"

    if appliance_name == "electric-appliance":
        appliance_name = file_name[4].split(".")[0]
    return house_name, appliance_name


# process a single house
def process_house(house: Any, file_list: List[str], data_path: Path) -> Tuple[Any, dict]:
    house_data = {}
    for file in file_list:
        _, label, df = process_file(file, data_path)
        house_data[label] = df
    return house, house_data


# process a single file for a house
def process_file(file: str, data_path: Path) -> Tuple[str, str, pd.DataFrame]:
    house, label = parse_name(file)
    return house, label, read_and_preprocess_df(data_path / "data_merged/" / file)


def unpack_and_process(p: tuple) -> Tuple[str, str, pd.DataFrame]:
    return process_house(*p)


def parse_IDEAL(data_path: str, save_path: str) -> None:
    data_path: Path = Path(data_path).resolve()
    assert data_path.exists(), f"Path '{data_path}' does not exist!"
    data_dict = {}
    files_grouped_by_home = defaultdict(list)
    # get files for electricity consumption
    files = [file for file in os.listdir(data_path / "data_merged/") if ("electric-appliance" in file or "electric-mains" in file) and "home223" not in file]
    # group files by house
    for file in files:
        house, _ = parse_name(file)
        files_grouped_by_home[house].append(file)

    total_houses = len(files_grouped_by_home)

    print("Processing houses...")
    cpu_count = int(os.cpu_count() // 8)
    if os.cpu_count() < 16:
        cpu_count = os.cpu_count() // 2

    # no need for more than 32 processes for this dataset
    if cpu_count > 32:
        cpu_count = 32
    

    # process the houses in parallel
    with ProcessPoolExecutor(max_workers=cpu_count) as executor, tqdm(total=total_houses, desc="Processing houses", unit="house") as t:
        args = ((house, files_grouped_by_home[house], data_path) for house in files_grouped_by_home)

        for house_name, house_data in executor.map(unpack_and_process, args):
            data_dict[house_name] = house_data
            t.update(1)

    # save the data to a dictonary
    save_to_pickle(data_dict, save_path)

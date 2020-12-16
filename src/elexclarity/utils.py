import os
import json


def get_json_from_file(file_path):
    # Does the file exist?
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The specified file path {file_path} does not exist")

    with open(file_path) as f:
        data = json.load(f)
    return data


def get_fips_mapping(state_postal):
    file_path = f"src/elexclarity/data/fips-mappings/{state_postal.lower()}.json"
    return get_json_from_file(file_path)[state_postal]


def fips_mapping_exists(state_postal):
    file_path = f"src/elexclarity/data/fips-mappings/{state_postal.lower()}.json"
    if not os.path.isfile(file_path):
        return False
    return True

import os
import json
from dateutil import parser, tz


def get_json_from_file(file_path):
    """
    Parse JSON from file.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The specified file path {file_path} does not exist")

    with open(file_path) as f:
        data = json.load(f)
    return data


def get_list(item):
    """
    Return instance as a list.
    """
    return item if isinstance(item, list) else [item]


def format_timestamp(input_timestamp):
    # convert the timestamp and make sure we're in EST
    est = tz.gettz("America/New_York")
    timestamp = parser.parse(input_timestamp, tzinfos={"EST": est}).astimezone(est)
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

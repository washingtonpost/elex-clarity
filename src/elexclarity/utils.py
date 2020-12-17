import os
import json


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

from collections import defaultdict
import xmltodict
from elexclarity.utils import get_json_from_file
from slugify import slugify

from elexclarity.formatters import ClarityXMLConverter
from elexclarity.race_name_maps import RACE_NAME_MAPS


def convert(data, statepostal=None, level=None, outputType="results", style="default", resultsBy=None, countyMapping={}, **kwargs):
    """
    The entry point for formatting Clarity results data.
    """
    # TODO: Data formatting/conversion logic for settings and summary

    if outputType == "summary" or outputType == "settings":
        # Returns raw data for now
        return data

    if type(data) == list:
        data = [xmltodict.parse(i, attr_prefix="")["ElectionResult"] for i in data]
    else:
        data = [xmltodict.parse(data, attr_prefix="")["ElectionResult"]]

    if level == "precinct" or level == "county":
        county_lookup = countyMapping if countyMapping else None
        converter = ClarityXMLConverter(
            county_lookup=county_lookup,
            race_name_lookup=RACE_NAME_MAPS.get(statepostal, {})
        )
        results = [converter.transform_result_object(i, level=level) for i in data]

        if len(results) > 1:
            return results

        return results[0]

    raise Exception(f"The {level} Clarity formatter is not implemented yet")

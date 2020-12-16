from collections import defaultdict

import xmltodict
from elexclarity.utils import get_json_from_file, get_fips_mapping, fips_mapping_exists
from slugify import slugify

from elexclarity.formatters import ClarityXMLConverter


def convert(data, statepostal=None, level=None, outputType="results", style="default", resultsBy=None, countymapping=None, **kwargs):
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
        # If specific county mapping is provided
        if countymapping:
            fips_mapping = countymapping[statepostal]
            county_fips_lookup = {v["name"]: k for k, v in fips_mapping.items()}
        # Else if fips mapping static data is available
        elif fips_mapping_exists(statepostal):
            fips_mapping = get_fips_mapping(statepostal)
            county_fips_lookup = {v["name"]: k for k, v in fips_mapping.items()}
        # Else slugify county name as backup
        else:
            county_fips_lookup = None

        converter = ClarityXMLConverter(county_lookup=county_fips_lookup)
        results = [converter.transform_result_object(i, level=level) for i in data]

        if len(results) > 1:
            return results

        return results[0]

    raise Exception(f"The {level} Clarity formatter is not implemented yet")

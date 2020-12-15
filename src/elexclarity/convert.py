from collections import defaultdict

import xmltodict
from elexstatic import STATE_COUNTIES
from slugify import slugify

from elexclarity.formatters import ClarityXMLPrecinctConverter


def convert(data, statepostal=None, level=None, outputType="results", style="default", resultsBy=None, **kwargs):
    """
    The entry point for formatting Clarity results data.
    """
    if type(data) == list:
        data = [xmltodict.parse(i, attr_prefix="")["ElectionResult"] for i in data]
    else:
        data = [xmltodict.parse(data, attr_prefix="")["ElectionResult"]]

    if level == "precinct":
        county_fips_lookup = {v["name"]: k for k, v in STATE_COUNTIES[statepostal].items()}
        converter = ClarityXMLPrecinctConverter(county_lookup=county_fips_lookup)
        results = [converter.transform_result_object(i) for i in data]

        if len(results) > 1:
            return results

        return results[0]

    raise Exception(f"The {level} Clarity formatter is not implemented yet")

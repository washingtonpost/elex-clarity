from collections import defaultdict

import xmltodict
from elexstatic import STATE_COUNTIES

from elexclarity.formatters.results import ClarityXMLConverter
from elexclarity.formatters.settings import ClaritySettingsConverter


def convert(data, statepostal=None, level=None, outputType="results", style="default", **kwargs):
    """
    The entry point for formatting Clarity results data.
    """
    if style == "raw" or outputType == "summary":
        return data

    if outputType == "settings":
        return ClaritySettingsConverter().convert(data, level=level, statepostal=statepostal, **kwargs)

    elif outputType == "results":
        if isinstance(data, list):
            data = [xmltodict.parse(i, attr_prefix="")["ElectionResult"] for i in data]
        else:
            data = [xmltodict.parse(data, attr_prefix="")["ElectionResult"]]

        if level == "precinct" or level == "county":
            county_fips_lookup = {v["name"]: k for k, v in STATE_COUNTIES[statepostal].items()}
            converter = ClarityXMLConverter(county_lookup=county_fips_lookup)
            results = [converter.convert(i, level=level) for i in data]

            if len(results) > 1:
                return results

            return results[0]

    raise Exception(f"The {level} Clarity formatter is not implemented yet")

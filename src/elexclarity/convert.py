from elexclarity.formatters.results import ClarityXMLConverter
from elexclarity.formatters.settings import ClaritySettingsConverter


def convert(data, statepostal=None, level=None, outputType="results", style="default", countyMapping={}, **kwargs):
    """
    The entry point for formatting Clarity results data.
    """
    if style == "raw" or outputType == "summary":
        return data

    if outputType == "settings":
        return ClaritySettingsConverter().convert(data, level=level, statepostal=statepostal, **kwargs)

    if outputType == "results":
        county_lookup = countyMapping if countyMapping else None
        converter = ClarityXMLConverter(county_lookup=county_lookup)
        return [converter.convert(i, level=level) for i in data]

    raise Exception(f"The {level} Clarity formatter is not implemented yet")

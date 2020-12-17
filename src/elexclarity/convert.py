import xmltodict
from elexclarity.formatters.results import ClarityDetailXMLConverter
from elexclarity.formatters.settings import ClaritySettingsConverter


def convert(data, statepostal=None, level=None, outputType="results", style="default", countyMapping=None, **kwargs):
    """
    The entry point for formatting Clarity results data.
    """
    if style == "raw" or outputType == "summary":
        return data

    if outputType == "settings":
        return ClaritySettingsConverter(county_lookup=countyMapping).convert(
            data,
            level=level,
            statepostal=statepostal,
            **kwargs
        )

    if outputType == "results":
        converter = ClarityDetailXMLConverter(county_lookup=countyMapping)
        results = {}
        for sub_result in data:
            results.update(converter.convert(xmltodict.parse(sub_result, attr_prefix="")["ElectionResult"], level=level))
        return results

    raise Exception(f"The {level} Clarity formatter is not implemented yet")

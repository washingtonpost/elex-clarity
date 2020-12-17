import xmltodict
from elexclarity.formatters.results import ClarityXMLConverter
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
        data = [xmltodict.parse(data, attr_prefix="")["ElectionResult"]]
        converter = ClarityXMLConverter(county_lookup=countyMapping)
        results = [converter.convert(i, level=level) for i in data]
        if len(results) > 1:
            return results
        return results[0]

    raise Exception(f"The {level} Clarity formatter is not implemented yet")

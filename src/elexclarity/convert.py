from elexclarity.formatters.results import ClarityDetailXMLConverter
from elexclarity.formatters.settings import ClaritySettingsConverter


def convert(data, statepostal, level=None, outputType="results", style="default", countyMapping=None, **kwargs):
    """
    The entry point for formatting Clarity results data.
    """
    if style == "raw" or outputType == "summary":
        return data

    if outputType == "settings":
        return ClaritySettingsConverter(statepostal, county_lookup=countyMapping).convert(
            data,
            level=level,
            **kwargs
        )

    if outputType == "results":
        converter = ClarityDetailXMLConverter(
            statepostal,
            county_lookup=countyMapping
        )
        results = {}
        for sub_result in data:
            results.update(converter.convert(sub_result, level=level, **kwargs))
        return results

    raise Exception(f"The {level} Clarity formatter is not implemented yet")

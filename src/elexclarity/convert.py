from elexclarity.formatters.results import ClarityDetailXMLConverter
from elexclarity.formatters.settings import ClaritySettingsConverter


def convert(data, statepostal, outputType="results", style="default", countyMapping=None, **kwargs):
    """
    The entry point for formatting Clarity results data.
    """

    if kwargs.get("officeID") and type(kwargs.get("officeID")) == str:
        kwargs["officeID"] = kwargs["officeID"].split(",")

    if style == "raw" or outputType == "summary":
        return data

    if outputType == "settings":
        return ClaritySettingsConverter(statepostal, county_lookup=countyMapping).convert(
            data,
            **kwargs
        )

    if outputType == "results":
        converter = ClarityDetailXMLConverter(
            statepostal,
            county_lookup=countyMapping
        )

        if type(data) == list:
            results = {}
            for sub_result in data:
                results.update(converter.convert(sub_result, **kwargs))
            return results
        else:
            return converter.convert(data, **kwargs)

    raise Exception(f"The {outputType} Clarity formatter is not implemented yet")

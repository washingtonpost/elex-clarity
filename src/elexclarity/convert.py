from elexclarity.formatters.results import ClarityDetailXMLConverter
from elexclarity.formatters.settings import ClaritySettingsConverter


def convert(
    data,
    statepostal,
    outputType="results",
    style="default",
    countyMapping=None,
    candidateMapping=None,
    officeID=None,
    voteCompletionMode=None,
    precinctsReportingPct={},
    **kwargs
):
    """
    The entry point for formatting Clarity results data.
    """

    office_id = officeID
    vote_completion_mode = voteCompletionMode
    precincts_reporting_pct_override = precinctsReportingPct

    if office_id and isinstance(office_id, str):
        office_id = office_id.split(",")

    if style == "raw" or outputType == "summary":
        return data

    if outputType == "settings":
        return ClaritySettingsConverter(statepostal, county_lookup=countyMapping, candidate_lookup=candidateMapping).convert(
            data,
            office_id=office_id,
            **kwargs
        )

    if outputType == "results":
        converter = ClarityDetailXMLConverter(
            statepostal,
            county_lookup=countyMapping,
            candidate_lookup=candidateMapping
        )

        if isinstance(data, list):
            results = {}
            for sub_result in data:
                results.update(converter.convert(
                    sub_result,
                    vote_completion_mode=vote_completion_mode,
                    precincts_reporting_pct_override=precincts_reporting_pct_override,
                    office_id=office_id,
                    **kwargs
                ))
            return results
        else:
            return converter.convert(
                data,
                vote_completion_mode=vote_completion_mode,
                precincts_reporting_pct_override=precincts_reporting_pct_override,
                office_id=office_id,
                omit_locality_from_race_id=kwargs.get(
                    "omit_locality_from_race_id", True
                ),
                **kwargs
            )

    raise Exception(f"The {outputType} Clarity formatter is not implemented yet")

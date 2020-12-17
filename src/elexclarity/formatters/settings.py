from elexclarity.utils import format_timestamp


class ClaritySettingsConverter:
    """
    A class to convert Clarity JSON settings.
    """

    def __init__(self, statepostal=None, county_lookup=None, **kwargs):
        self.state_postal = statepostal
        self.county_lookup = county_lookup

    def convert(self, data, level="county", **kwargs):
        if level == "county":
            raw_counties = data.get("settings", {}).get("electiondetails", {}).get("participatingcounties")
            counties = {}
            for raw_county in raw_counties:
                name, clarity_id, version, raw_last_updated = raw_county.split("|")[0:4]
                county_id = name
                last_updated = format_timestamp(raw_last_updated)
                if self.county_lookup:
                    county_id = self.county_lookup[name]
                counties[county_id] = {
                    "id": county_id,
                    "version": version,
                    "lastUpdated": last_updated,
                    "clarityId": clarity_id
                }
            return counties
        raise Exception(f"The {level} Clarity settings formatter is not implemented yet")

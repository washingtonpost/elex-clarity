from collections import namedtuple

CountyIdentifier = namedtuple('CountyIdentifier', ['id', 'name', 'version', 'last_updated'])

class ClaritySettingsConverter:
    """
    A class to convert Clarity JSON settings.
    """

    def __init__(self, county_lookup=None, **kwargs):
        self.county_lookup = county_lookup

    def convert(self, data, **kwargs):
        raw_counties = data.get("settings", {}).get("electiondetails", {}).get("participatingcounties")
        counties = []
        for raw_county in raw_counties:
            name, _id, version, last_updated = raw_county.split("|")[0:4]
            counties.append(CountyIdentifier(_id, name, version, last_updated))
        return counties

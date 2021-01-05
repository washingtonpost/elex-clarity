from elexclarity.formatters.base import ClarityConverter


class ClaritySettingsConverter(ClarityConverter):
    """
    A class to convert Clarity JSON settings.
    """

    def convert(self, data, level="county", office_id=(), **kwargs):
        if level == "county":
            raw_counties = data.get("settings", {}).get("electiondetails", {}).get("participatingcounties")
            raw_date = data.get("settings", {}).get("electiondetails", {}).get("electiondate")
            raw_type = data.get("settings", {}).get("electiondetails", {}).get("internalname")

            election_date = self.format_date(raw_date)
            race_id_settings_mapping = {}
            for raw_county in raw_counties:
                name, clarity_id, version, raw_last_updated = raw_county.split("|")[0:4]
                last_updated = self.format_last_updated(raw_last_updated)
                for office in office_id:
                    race_id = "_".join([
                        election_date,
                        self.state_postal,
                        self.get_race_type(raw_type),
                        office,
                        self.get_county_id(name)
                    ])
                    race_id_settings_mapping[race_id] = {
                        "id": race_id,
                        "name": name,
                        "version": version,
                        "lastUpdated": last_updated,
                        "clarityId": clarity_id
                    }
            return race_id_settings_mapping
        raise Exception(f"The {level} Clarity settings formatter is not implemented yet")

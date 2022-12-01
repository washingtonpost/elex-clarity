import re
from slugify import slugify
from dateutil import parser, tz

from elexclarity.formatters.const import (
    STATE_OFFICE_ID_MAPS,
    STATE_RACE_TYPE_MAPS,
    STATE_VOTE_TYPE_MAPS,
)

US_TIMEZONES = {
    "PST": tz.gettz("US/Pacific"),
    "PDT": tz.gettz("US/Pacific"),
    "MST": tz.gettz("US/Mountain"),
    "MDT": tz.gettz("US/Mountain"),
    "CST": tz.gettz("US/Central"),
    "CDT": tz.gettz("US/Central"),
    "EST": tz.gettz("US/Eastern"),
    "EDT": tz.gettz("US/Eastern"),
}

class ClarityConverter(object):
    def __init__(self, statepostal, county_lookup=None, candidate_lookup=None, **kwargs):
        self.state_postal = statepostal
        self.county_lookup = county_lookup
        self.candidate_lookup = candidate_lookup

    def get_race_type(self, election_name, *, contest={}):
        contest_name = contest.get('text', '')
        lookup = STATE_RACE_TYPE_MAPS.get(self.state_postal, {})
        if contest_name in lookup:
            return lookup[contest_name]
        for key, value in lookup.items():
            if key in election_name or key in contest_name:
                return value
        if "General" or "Runoff" in election_name:
            return "G"
        raise Exception(f"Unknown election type: {election_name}")

    def get_race_office(self, contest_name):
        office_id_maps = STATE_OFFICE_ID_MAPS[self.state_postal]

        contest_slug = slugify(contest_name, separator="_", replacements=[['.','']])

        office_id = contest_slug

        for name, id in office_id_maps.items():
            slug = slugify(name, separator="_", replacements=[['.','']])
            if slug in contest_slug:
                office_id = id
                break # stop at first match

        if office_id == "H" and "district" in contest_slug:
            district_match = re.search(r"district_([0-9]+)", contest_slug)
            if district_match:
                office_id += f"_{int(district_match.group(1))}"

        return office_id

    def get_choice_id(self, name, party=None, race_id=None):
        if party and party == "REP":
            party = "GOP"
        if party and party == "NP":
            party = None
        choice_id = "_".join(filter(None, [race_id, party, slugify(name, separator="_")]))
        if self.candidate_lookup:
            choice_id = self.candidate_lookup.get(choice_id, choice_id)
        return choice_id

    def get_precinct_id(self, name, county_id=None):
        return "_".join(filter(None,[county_id, slugify(name, separator='-')]))

    def get_vote_type_id(self, name):
        id = slugify(name, separator='-').replace("-votes", "")
        id = STATE_VOTE_TYPE_MAPS.get(self.state_postal,{}).get(id, id)
        return id

    def get_county_id(self, name):
        """
        Returns special mapping, fips code, or slugified county name
        based on specified county mapping.
        """
        slug = slugify(name, separator="_")
        if not self.county_lookup:  # No mapping provided
            return slug
        return self.county_lookup.get(
            name, self.county_lookup.get(name.replace("_", " "), slug)
        )

    @classmethod
    def get_timestamp(cls, input_timestamp):
        # convert the timestamp
        return parser.parse(input_timestamp, tzinfos=US_TIMEZONES).astimezone(tz.gettz("UTC"))

    @classmethod
    def format_last_updated(cls, input_timestamp):
        return cls.get_timestamp(input_timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")

    @classmethod
    def format_date(cls, input_timestamp):
        return cls.get_timestamp(input_timestamp).strftime("%Y-%m-%d")

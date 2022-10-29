from slugify import slugify
from dateutil import parser, tz

from elexclarity.formatters.const import STATE_OFFICE_ID_MAPS, STATE_RACE_TYPE_MAPS


class ClarityConverter(object):
    def __init__(self, statepostal, county_lookup=None, **kwargs):
        self.state_postal = statepostal
        self.county_lookup = county_lookup

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

        for name, id in office_id_maps.items():
            slug = slugify(name, separator="_", replacements=[['.','']])
            if slug in contest_slug:
                return id

        return contest_slug

    @classmethod
    def get_choice_id(cls, name):
        return slugify(name, separator="_")

    def get_precinct_id(self, name, county_id=None):
        return "_".join(filter(None,[county_id, slugify(name, separator='-')]))

    def get_county_id(self, name):
        """
        Returns special mapping, fips code, or slugified county name
        based on specified county mapping.
        """
        slug = slugify(name, separator="_")
        if not self.county_lookup:  # No mapping provided
            return slug
        return self.county_lookup[name]

    @classmethod
    def get_timestamp(cls, input_timestamp):
        # convert the timestamp and make sure we're in EST
        est = tz.gettz("America/New_York")
        return parser.parse(input_timestamp, tzinfos={"EST": est}).astimezone(tz.gettz("UTC"))

    @classmethod
    def format_last_updated(cls, input_timestamp):
        return cls.get_timestamp(input_timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")

    @classmethod
    def format_date(cls, input_timestamp):
        return cls.get_timestamp(input_timestamp).strftime("%Y-%m-%d")

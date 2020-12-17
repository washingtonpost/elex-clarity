from collections import defaultdict
from slugify import slugify
import xmltodict

from elexclarity.formatters.const import STATE_OFFICE_ID_MAPS
from elexclarity.utils import get_list, format_timestamp


class ClarityDetailXMLConverter:
    """
    A class to convert Clarity XML into our expected data format.
    """

    def __init__(self, statepostal, county_lookup=None, **kwargs):
        self.state_postal = statepostal
        self.county_lookup = county_lookup

    def get_race_type(self, election_name):
        if "General" in election_name:
            return "G"
        raise Exception("Unknown election type")

    def get_race_office(self, contest_name):
        return STATE_OFFICE_ID_MAPS[self.state_postal].get(contest_name, slugify(contest_name, separator="_"))

    def get_county_id(self, name):
        """
        Returns special mapping, fips code, or slugified county name
        based on specified county mapping.
        """
        if self.county_lookup is None:  # No mapping provided
            return slugify(name, separator="_")
        return self.county_lookup.get(name)

    def get_subunit_id(self, subunit_name, fips=None):
        """
        Create an ID for a precinct or county.
        Fips codes are present when level == precinct.
        """
        # Subunit is a county
        if fips is None:
            return self.get_county_id(subunit_name)
        # Subunit is a precinct
        precinct_name = slugify(subunit_name, separator="_")
        return f"{fips}_{precinct_name}"

    def get_subunit_totals_from_choice(self, choice, level):
        """
        Takes a Clarity `Choice` object and aggregates all the different
        kinds of votes into one total per subunit.
        """
        name = choice.get("text")
        key = choice.get("key")
        slug = slugify(name, separator="_")

        subunit_objs = defaultdict(lambda: 0)

        for i in get_list(choice["VoteType"]):
            subunit_level = level.capitalize()
            subunits = i[subunit_level]
            for subunit in get_list(subunits):
                subunit_objs[subunit["name"]] += int(subunit["votes"])

        return {
            "key": key,
            "name": name,
            "id": slug,
            "subunits": subunit_objs,
        }

    def aggregate_subunits_from_choices(self, choices, level, fips):
        """
        Takes a list of `Choice` objects from Clarity and aggregates/transforms
        them into a the format our data importer expects.
        """
        processed_choices = [self.get_subunit_totals_from_choice(i, level) for i in filter(lambda choice: choice.get("text"), choices)]

        # Get a flat, unique, list of our subunit names
        subunits = [i["subunits"].keys() for i in processed_choices]
        if level == "county":
            processed_subunits = []
            for county in list(subunits[0]):
                processed_subunits.append(self.get_subunit_id(county))
        elif level == "precinct":
            processed_subunits = set([self.get_subunit_id(precinct, fips) for subunit in subunits for precinct in subunit])

        agg = {i: {
            "id": i,
            "counts": defaultdict(lambda: 0)
        } for i in processed_subunits}

        for choice in processed_choices:
            candidate = choice["id"]
            for subunit_name, vote_count in choice["subunits"].items():
                if level == 'precinct':
                    key = self.get_subunit_id(subunit_name, fips)
                else:
                    key = self.get_subunit_id(subunit_name)
                agg[key]["counts"][candidate] += vote_count

        return agg

    def get_total_votes_from_choices(self, choices):
        """
        Aggregates the total votes for a candidate from the
        Clarity `Choice` object.
        """
        agg = {}

        for choice in choices:
            name = choice.get("text")
            slug = slugify(name, separator="_")
            agg[slug] = int(choice["totalVotes"])

        return agg

    def transform_contest(self, contest, election_date, election_type, timestamp=None, fips=None, level=None, **kwargs):
        """
        Transforms a Clarity `Contest` object into our expected format.
        """
        # Available fields vary in Clarity data
        precincts_reporting_pct = contest.get("precinctsReportingPercent")
        if precincts_reporting_pct:
            precincts_reporting_pct = float(precincts_reporting_pct)
        else:
            precincts_reported = int(contest.get("precinctsReported"))
            precincts_reporting = int(contest.get("precinctsReporting"))
            precincts_reporting_pct = (precincts_reported/precincts_reporting)*100

        choices = get_list(contest["Choice"])
        contest_name = contest["text"]
        race_id = "_".join([
            election_date,
            self.state_postal,
            election_type,
            self.get_race_office(contest_name)
        ])

        result = {
            "id": race_id,
            "source": "clarity",
            "precinctsReportingPct": precincts_reporting_pct,
            "subunits": self.aggregate_subunits_from_choices(choices, level, fips),
            "counts": self.get_total_votes_from_choices(choices)
        }
        if timestamp:
            result["lastUpdated"] = timestamp
        return result


    def convert(self, data, **kwargs):
        """
        Transforms a Clarity `ElectionResult` object into our expected format.
        """
        result = {}
        dictified_data = xmltodict.parse(data, attr_prefix="").get("ElectionResult", {})
        county = dictified_data["Region"]
        if self.county_lookup:
            fips = self.county_lookup.get(county)
        else:
            fips = slugify(county, separator="_")
        election_date = format_timestamp(dictified_data["ElectionDate"]).split("T")[0]
        election_type = self.get_race_type(dictified_data["ElectionName"])
        timestamp = format_timestamp(dictified_data["Timestamp"])

        for contest in get_list(dictified_data.get("Contest")):
            race_result = self.transform_contest(contest, election_date, election_type, timestamp=timestamp, fips=fips, **kwargs)
            result[race_result["id"]] = race_result
        return result

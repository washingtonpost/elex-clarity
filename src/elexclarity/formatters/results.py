from collections import defaultdict
from slugify import slugify

from elexclarity.utils import get_list, format_timestamp


class ClarityDetailXMLConverter:
    """
    A class to convert Clarity XML into our expected data format.
    """

    def __init__(self, county_lookup=None, **kwargs):
        self.county_lookup = county_lookup

    def get_race_id(self, name):
        return slugify(name)

    def get_county_id(self, name):
        """
        Returns special mapping, fips code, or slugified county name
        based on specified county mapping.
        """
        if self.county_lookup is None:  # No mapping provided
            return slugify(name)
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
        precinct_name = slugify(subunit_name)
        return f"{fips}_{precinct_name}"

    def get_subunit_totals_from_choice(self, choice, level):
        """
        Takes a Clarity `Choice` object and aggregates all the different
        kinds of votes into one total per subunit.
        """
        name = choice.get("text")
        key = choice.get("key")
        slug = slugify(name)

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
            slug = slugify(name)
            agg[slug] = int(choice["totalVotes"])

        return agg

    def transform_contest(self, contest, level, fips, timestamp):
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

        return {
            "id": self.get_race_id(contest["text"]),
            "source": "clarity",
            "lastUpdated": timestamp,
            "precinctsReportingPct": precincts_reporting_pct,
            "subunits": self.aggregate_subunits_from_choices(choices, level, fips),
            "counts": self.get_total_votes_from_choices(choices)
        }

    def convert(self, result, level):
        """
        Transforms a Clarity `Result` object into our expected format.
        """
        fips = None

        # Need to pass down county fips if level = precinct
        if level == 'precinct':
            county = result["Region"]
            if self.county_lookup:
                fips = self.county_lookup.get(county)
            else:
                fips = slugify(county)

        contests = [self.transform_contest(i, level, fips, format_timestamp(result["Timestamp"])) for i in get_list(result["Contest"])]
        return {i["id"]: i for i in contests}

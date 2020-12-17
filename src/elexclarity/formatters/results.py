<<<<<<< HEAD:src/elexclarity/formatters/results.py
=======
from collections import defaultdict
import xmltodict
>>>>>>> fips-lookups:src/elexclarity/formatters.py
from slugify import slugify
from dateutil import parser, tz
from collections import defaultdict

from elexclarity.utils import get_list


class ClarityXMLConverter:
    """
    A class to convert Clarity XML into our expected data format.
    """

    def __init__(self, county_lookup=None, **kwargs):
        self.county_lookup = county_lookup

    def get_id_for_choice(self, name):
        """
        Create an ID from the clarity key and candidate name.
        """
        return slugify(name)

    def get_county_mapping(self, name):
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
        name = slugify(subunit_name)
        # Subunit is a county
        if fips is None:
            return self.get_county_mapping(subunit_name)
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
        slug = self.get_id_for_choice(name)

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
        processed_choices = [self.get_subunit_totals_from_choice(i, level) for i in choices]

        # Get a flat, unique, list of our subunit names
        subunits = [i["subunits"].keys() for i in processed_choices]
        if level == "county":
            processed_subunits = []
            for county in list(subunits[0]):
                processed_subunits.append(self.get_subunit_id(county))
        elif level == "precinct":
            processed_subunits = set([self.get_subunit_id(i, fips) for l in subunits for i in l])

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
            slug = self.get_id_for_choice(name)
            agg[slug] = int(choice["totalVotes"])

        return agg

    def transform_contest(self, contest, level, fips, timestamp):
        """
        Transforms a Clarity `Contest` object into our expected format.
        """
        # Available fields vary in Clarity data
        if "precinctsReportingPercent" in contest:
            precincts_reporting_pct = float(contest.get("precinctsReportingPercent"))
        else:
            precincts_reported = int(contest.get("precinctsReported"))
            precincts_reporting = int(contest.get("precinctsReporting"))
            precincts_reporting_pct = (precincts_reported/precincts_reporting)*100

<<<<<<< HEAD:src/elexclarity/formatters/results.py
        # some light validation on the choices to make sure we get a list
        choices = contest["Choice"]
        if not isinstance(choices, list):
            choices = [choices]
=======
        choices = get_list(contest["Choice"])
>>>>>>> fips-lookups:src/elexclarity/formatters.py

        return {
            "source": "clarity",
            "lastUpdated": timestamp,
            "name": contest.get("text"),
            "precinctsReportingPct": precincts_reporting_pct,
            "subunits": self.aggregate_subunits_from_choices(choices, level, fips=fips),
            "counts": self.get_total_votes_from_choices(choices)
        }

    def convert(self, result, level):
        """
        Transforms a Clarity `Result` object into our expected format.
        """
        fips = None

        # convert the timestamp and make sure we're in EST
        est = tz.gettz("America/New_York")
        timestamp = parser.parse(result["Timestamp"], tzinfos={"EST": est}).astimezone(est)
        timestamp = timestamp.strftime("%Y-%m-%dT%H:%H:%SZ")

        # Need to pass down county fips if level = precinct
        if level == 'precinct':
            county = result["Region"]
<<<<<<< HEAD:src/elexclarity/formatters/results.py
            fips = self.county_lookup.get(county)

        # Multiple contests
        if not isinstance(result["Contest"], list):
            contests = [self.transform_contest(i, level, fips=fips, timestamp=timestamp) for i in result["Contest"]]
        else:
            contest_obj = [result["Contest"]]
            contests = [self.transform_contest(i, level, fips=fips, timestamp=timestamp) for i in contest_obj]
=======
            if self.county_lookup:
                fips = self.county_lookup.get(county)
            else:
                fips = slugify(county)
>>>>>>> fips-lookups:src/elexclarity/formatters.py

        contests = [self.transform_contest(i, level, fips=fips) for i in get_list(result["Contest"])]
        return {i["name"]: i for i in contests}

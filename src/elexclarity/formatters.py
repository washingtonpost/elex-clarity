from slugify import slugify
from dateutil import parser, tz
from collections import defaultdict


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

    def get_subunit_id(self, subunit_name, fips=None):
        """
        Create an ID for a precinct or county.
        Fips codes are present when level == precinct.
        """
        name = slugify(subunit_name)
        if fips is None:
            fips = self.county_lookup.get(subunit_name)
        return f"{fips}_{name}"

    def get_subunit_totals_from_choice(self, choice, level):
        """
        Takes a Clarity `Choice` object and aggregates all the different
        kinds of votes into one total per subunit.
        """
        name = choice.get("text")
        key = choice.get("key")
        slug = self.get_id_for_choice(name)

        subunit_objs = defaultdict(lambda: 0)

        for i in choice["VoteType"]:
            # more validation, for one precinct races
            subunit_level = level.capitalize()
            subunits = i[subunit_level]
            if type(subunits) != list:
                subunits = [subunits]
            for subunit in subunits:
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
                fips = self.county_lookup.get(county)
                processed_subunits.append(self.get_subunit_id(county))
        elif level == "precinct":
            processed_subunits = set([self.get_subunit_id(i, fips) for l in subunits for i in l])

        # Get a list of our candidates
        candidates = [i['id'] for i in processed_choices]

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
            key = choice.get("key")
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

        # some light validation on the choices to make sure we get a list
        choices = contest["Choice"]
        if type(choices) != list:
            choices = [choices]

        return {
            "source": "clarity",
            "timestamp": timestamp,
            "name": contest.get("text"),
            "precinctsReportingPct": precincts_reporting_pct,
            "subunits": self.aggregate_subunits_from_choices(choices, level, fips=fips),
            "counts": self.get_total_votes_from_choices(choices)
        }

    def transform_result_object(self, result, level):
        """
        Transforms a Clarity `Result` object into our expected format.
        """
        fips = None
        tzinfos = {"EST": tz.gettz("America/New_York")}
        timestamp = str(parser.parse(result["Timestamp"], tzinfos=tzinfos))

        # Need to pass down county fips if level = precinct
        if level == 'precinct':
            county = result["Region"]
            fips = self.county_lookup.get(county)

        # Multiple contests
        if type(result["Contest"]) == list:
            contests = [self.transform_contest(i, level, fips=fips, timestamp=timestamp) for i in result["Contest"]]
        else:
            contest_obj = [result["Contest"]]
            contests = [self.transform_contest(i, level, fips=fips, timestamp=timestamp) for i in contest_obj]

        return {i["name"]: i for i in contests}

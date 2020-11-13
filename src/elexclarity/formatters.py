from collections import defaultdict

import xmltodict
from slugify import slugify


class ClarityXMLPrecinctConverter:
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

    def get_id_for_precinct(self, fips, name):
        """
        Create an ID from the clarity key and candidate name. Unclear
        if these precinct names are unique across counties (assume
        they are not), so prepent the county fips.
        """
        name = slugify(name)
        return f"{fips}_{name}"

    def get_subunit_totals_from_choice(self, choice):
        """
        Takes a Clarity `Choice` object and aggregates all the different
        kinds of votes into one total per subunit.
        """
        name = choice.get("text")
        key = choice.get("key")
        slug = self.get_id_for_choice(name)

        subunits = defaultdict(lambda: 0)

        for i in choice["VoteType"]:
            # more validation, for one precinct races
            precincts = i["Precinct"]
            if type(precincts) != list:
                precincts = [precincts]

            for subunit in precincts:
                subunits[subunit["name"]] += int(subunit["votes"])

        return {
            "key": key,
            "name": name,
            "id": slug,
            "subunits": subunits,
        }

    def aggregate_subunits_from_choices(self, choices, fips):
        """
        Takes a list of `Choice` objects from Clarity and aggregates/transforms
        them into a the format our data importer expects.
        """
        processed_choices = [self.get_subunit_totals_from_choice(i) for i in choices]

        # Get a flat, unique, list of our subunit names
        subunits = [i["subunits"].keys() for i in processed_choices]
        subunits = set([self.get_id_for_precinct(fips, i) for l in subunits for i in l])

        # Get a list of our candidates
        candidates = [i['id'] for i in processed_choices]

        agg = {i: {
            "id": i,
            "counts": defaultdict(lambda: 0)
        } for i in subunits}

        for choice in processed_choices:
            candidate = choice["id"]
            for subunit_name, vote_count in choice["subunits"].items():
                key = self.get_id_for_precinct(fips, subunit_name)
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

    def transform_contest(self, contest, fips=""):
        """
        Transforms a Clarity `Contest` object into our expected format.
        """
        precincts_reported = int(contest.get("precinctsReported"))
        precincts_reporting = int(contest.get("precinctsReporting"))

        # some light validation on the choices to make sure we get a list
        choices = contest["Choice"]
        if type(choices) != list:
            choices = [choices]

        return {
            "source": "clarity",
            "name": contest.get("text"),
            "precinctsReportingPct": (precincts_reported/precincts_reporting)*100,
            "subunits": self.aggregate_subunits_from_choices(choices, fips=fips),
            "counts": self.get_total_votes_from_choices(choices)
        }

    def transform_result_object(self, result):
        """
        Transforms a Clarity `Result` object into our expected format.
        """
        county = result["Region"]
        fips = self.county_lookup.get(county)
        contests = [self.transform_contest(i, fips=fips) for i in result["Contest"]]
        return {i["name"]: i for i in contests}

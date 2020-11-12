import xmltodict
from slugify import slugify
from collections import defaultdict
from elexstatic import STATE_COUNTIES


class ClarityXMLConverter:
    """
    A class to convert Clarity XML into our expected data format.
    """
    def get_id_for_choice(self, key, name):
        """
        Create an ID from the clarity key and candidate name.
        """
        name = slugify(name)
        return f"{key}_{name}"

    def get_id_for_precinct(self, fips, name):
        """
        Create an ID from the clarity key and candidate name.
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
        slug = self.get_id_for_choice(key, name)
        
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
        agg = {}
        
        for choice in choices:
            name = choice.get("text")
            key = choice.get("key")
            slug = self.get_id_for_choice(key, name)
            agg[slug] = int(choice["totalVotes"])
        
        return agg

    def transform_contest(self, contest, fips=""):
        precincts_reported = int(contest.get("precinctsReported"))
        precincts_reporting = int(contest.get("precinctsReporting"))
        
        # some light validation on the choices to make sure we get a list
        choices = contest["Choice"]
        if type(choices) != list:
            choices = [choices]        
        
        return {
            "source": "clarity",
            "name": contest.get("text"),
            "precinctsReportingPct": precincts_reported/precincts_reporting,
            "subunits": self.aggregate_subunits_from_choices(choices, fips=fips),
            "counts": self.get_total_votes_from_choices(choices)
        }

    def transform_result_object(self, result):
        county = result["Region"]
        fips = self.county_lookup.get(county)
        contests = [self.transform_contest(i, fips=fips) for i in result["Contest"]]
        return {i["name"]: i for i in contests}

    def convert(self, data, statepostal="", outputType="results", style="default", resultsBy=None, **kwargs):
        """
        The entry point for formatting Clarity results data.
        """
        self.county_lookup = {v["name"]: k for k, v in STATE_COUNTIES[statepostal].items()}

        if type(data) == list:
            data = [xmltodict.parse(i, attr_prefix="")["ElectionResult"] for i in data]
        else:
            data = [xmltodict.parse(data, attr_prefix="")["ElectionResult"]]

        if style == "raw":
            return data
        
        results = [self.transform_result_object(i) for i in data]

        if len(results) > 1:
            return results
        
        return results[0]

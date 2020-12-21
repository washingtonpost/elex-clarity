from collections import defaultdict
from slugify import slugify
import xmltodict

from elexclarity.formatters.base import ClarityConverter
from elexclarity.utils import get_list


class ClarityDetailXMLConverter(ClarityConverter):
    """
    A class to convert Clarity XML into our expected data format.
    """

    def aggregate_choice_vote_types(self, choice, level):
        """
        Takes a Clarity `Choice` object and aggregates all the different
        kinds of votes into one total per subunit.

        For example, a precinct level file will have an entry like this:

        ```
        <Choice key="1" text="Donald J. Trump (I) (Rep)" party="NP" totalVotes="4018">
            <VoteType name="Election Day Votes" votes="431">
                <Precinct name="Douglas" votes="431" />
            </VoteType>
            <VoteType name="Advanced Voting Votes" votes="3099">
                <Precinct name="Douglas" votes="3099" />
            </VoteType>
            <VoteType name="Absentee by Mail Votes" votes="487">
                <Precinct name="Douglas" votes="487" />
            </VoteType>
            <VoteType name="Provisional Votes" votes="1">
                <Precinct name="Douglas" votes="1" />
            </VoteType>
        </Choice>
        ```

        And a county level file will have an entry like this:

        ```
        <Choice key="2" text="Joseph R. Biden (Dem)" party="NP" totalVotes="2474507">
            <VoteType name="Election Day Votes" votes="367205">
                <County name="Appling" votes="334" />
                <County name="Atkinson" votes="250" />
                <County name="Bacon" votes="140" />
                <County name="Baker" votes="149" />
                <County name="Baldwin" votes="1527" />
                <County name="Banks" votes="150" />
                <County name="Barrow" votes="1717" />
                <County name="Bartow" votes="2175" />
                <County name="Ben Hill" votes="336" />
                ...
            </VoteType>
            ...
        </Choice>
        ```

        So we have to convert our level into the XML tag name and then aggregate
        the vote types accordingly.
        """
        subunits = defaultdict(lambda: 0)
        clarity_level = level.capitalize()

        for vote_type in get_list(choice.get("VoteType", [])):
            vote_type_subunits = vote_type.get(clarity_level, [])
            for vote_type_subunit in get_list(vote_type_subunits):
                if level == "precinct":
                    subunit_id = self.get_precinct_id(vote_type_subunit["name"])
                else:
                    subunit_id = self.get_county_id(vote_type_subunit["name"])

                subunits[subunit_id] += int(vote_type_subunit["votes"])

        return subunits

    def format_subunits(self, choices, level):
        """
        Takes a list of `Choice` objects from Clarity and aggregates/transforms
        them into a the format our data importer expects.
        """
        subunit_results = {}
        for choice in filter(lambda choice: choice.get("text"), choices):
            choice_votes_by_subunit = self.aggregate_choice_vote_types(choice, level)
            for subunit_id, subunit_choice_votes in choice_votes_by_subunit.items():
                subunit_results.setdefault(subunit_id, {"id": subunit_id, "counts": defaultdict(lambda: 0)})
                choice_id = self.get_choice_id(choice.get("text"))
                subunit_results[subunit_id]["counts"][choice_id] += subunit_choice_votes

        return subunit_results

    def format_top_level_counts(self, choices):
        """
        Aggregates the total votes for a candidate from the
        Clarity `Choice` objects.
        """
        counts = {}

        for choice in choices:
            choice_id = self.get_choice_id(choice.get("text"))
            counts[choice_id] = int(choice["totalVotes"])

        return counts

    def format_race(self, contest, election_date, election_type, timestamp=None, level=None, county_id=None, **kwargs):
        """
        Transforms a Clarity `Contest` object into our expected race result format.
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
        office = self.get_race_office(contest_name)
        id_parts = [
            election_date,
            self.state_postal,
            election_type,
            office
        ]
        if level == "precinct":
            id_parts.append(county_id)
        race_id = "_".join(id_parts)

        result = {
            "id": race_id,
            "source": "clarity",
            "precinctsReportingPct": precincts_reporting_pct,
            "counts": self.format_top_level_counts(choices),
            "office": office
        }
        if timestamp:
            result["lastUpdated"] = timestamp
        if level in ["precinct", "county"]:
            result["subunits"] = self.format_subunits(choices, level)

        return result

    def convert(self, data, level="precinct", **kwargs):
        """
        Transforms a Clarity `ElectionResult` object into our expected format.
        """
        result = {}
        dictified_data = xmltodict.parse(data, attr_prefix="").get("ElectionResult", {})
        if level == "precinct":
            region = dictified_data["Region"]
            county_id = self.get_county_id(region)
        else:
            county_id = None
        election_date = self.format_date(dictified_data["ElectionDate"])
        election_type = self.get_race_type(dictified_data["ElectionName"])
        timestamp = self.format_last_updated(dictified_data["Timestamp"])


        officeID = kwargs.get("officeID", ())

        for contest in get_list(dictified_data.get("Contest")):
            race_result = self.format_race(
                contest,
                election_date,
                election_type,
                level=level,
                county_id=county_id,
                timestamp=timestamp,
                **kwargs
            )

            office = race_result.get('office')
            if not officeID or office in officeID:
                result[race_result["id"]] = race_result

        return result

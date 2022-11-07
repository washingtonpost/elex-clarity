from collections import defaultdict
import xmltodict

from elexclarity.formatters.base import ClarityConverter
from elexclarity.utils import get_list


class ClarityDetailXMLConverter(ClarityConverter):
    """
    A class to convert Clarity XML into our expected data format.
    """
    NUM_VOTE_TYPES = 4

    def aggregate_choice_vote_types(self, choice, level, *, county_id=None):
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
                    subunit_id = self.get_precinct_id(vote_type_subunit["name"], county_id=county_id)
                else:
                    subunit_id = self.get_county_id(vote_type_subunit["name"])

                subunits[subunit_id] += int(vote_type_subunit["votes"])

        return subunits

    def get_vote_totals_by_vote_types(self, choices, level, *, county_id=None):
        """
        Creates a mapping from subunit IDs to the total number of votes in
        for that vote type across all choices.
        """
        subunit_vote_types = {}
        clarity_level = level.capitalize()

        for choice in choices:
            for vote_type in get_list(choice.get("VoteType", [])):
                vote_type_subunits = vote_type.get(clarity_level, [])
                for vote_type_subunit in get_list(vote_type_subunits):
                    subunit_id = self.get_precinct_id(vote_type_subunit["name"], county_id=county_id)
                    subunit_vote_types.setdefault(subunit_id, defaultdict(lambda: 0))
                    subunit_vote_types[subunit_id][vote_type["name"]] += int(vote_type_subunit["votes"])

        return subunit_vote_types

    def _get_valid_contest_choices(self, contest):
        return list(filter(lambda choice: choice.get("text"), get_list(contest["Choice"])))

    def format_subunits(self, choices, level, subunit_fully_reporting_statuses=None, *, county_id=None):
        """
        Takes a list of `Choice` objects from Clarity and aggregates/transforms
        them into a the format our data importer expects.
        """
        subunit_results = {}

        for choice in choices:
            choice_votes_by_subunit = self.aggregate_choice_vote_types(choice, level, county_id=county_id)
            for subunit_id, subunit_choice_votes in choice_votes_by_subunit.items():
                subunit_results.setdefault(subunit_id, {"id": subunit_id, "counts": defaultdict(lambda: 0)})
                choice_id = self.get_choice_id(choice.get("text"))
                subunit_results[subunit_id]["counts"][choice_id] += subunit_choice_votes

        if subunit_fully_reporting_statuses:
            for subunit_id, subunit_result in subunit_results.items():
                is_subunit_fully_reporting = subunit_fully_reporting_statuses.get(subunit_id, False)
                subunit_result["precinctsReportingPct"] = 100 if is_subunit_fully_reporting else 0
                if is_subunit_fully_reporting:
                    subunit_result["expectedVotes"] = sum(subunit_results[subunit_id]["counts"].values())
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

    def _get_precinct_fully_reporting_statuses_via_percent_reporting(self, election, county_id=None):
        """
        Constructs a mapping from precinct IDs to boolean flags representing
        whether or not the given precinct is fully reporting. This method does so by looking
        at the VoterTurnout from the ElectionResults tag in the precinct details xml
        and checking if ``percentReporting`` is 4. This means (we think) that all 4 vote
        types (early/absentee/day of in person/provisional) have been reported for the
        given precinct.
        """
        subunit_fully_reporting_statuses = {}
        precincts = get_list(election["VoterTurnout"]["Precincts"]["Precinct"])
        for precinct in precincts:
            subunit_id = self.get_precinct_id(precinct["name"], county_id=county_id)
            is_precinct_fully_reporting = (precinct.get("percentReporting") == str(self.NUM_VOTE_TYPES))
            subunit_fully_reporting_statuses[subunit_id] = is_precinct_fully_reporting

        return subunit_fully_reporting_statuses

    def _get_precinct_fully_reporting_statuses_via_vote_types(self, contest, *, county_id=None):
        """
        Constructs a mapping from precinct IDs to boolean flags representing
        whether or not the given precinct is fully reporting. This method does so by looking
        at the various vote types for each precinct and checking that some votes are
        in for each of those types (except provisional votes).
        """
        choices = self._get_valid_contest_choices(contest)
        subunit_fully_reporting_statuses = {}

        vote_types_by_subunit = self.get_vote_totals_by_vote_types(choices, "precinct", county_id=county_id)
        for subunit_id, vote_type_totals in vote_types_by_subunit.items():
            is_precinct_fully_reporting = True
            for vote_type, vote_total in vote_type_totals.items():
                if vote_total == 0 and vote_type not in ["Provisional Votes"]:
                    is_precinct_fully_reporting = False

            subunit_fully_reporting_statuses[subunit_id] = is_precinct_fully_reporting
        return subunit_fully_reporting_statuses

    def format_race(
        self,
        contest,
        election_date,
        election_type,
        timestamp=None,
        level=None,
        county_id=None,
        subunit_fully_reporting_statuses=None,
        vote_completion_mode=None,
        **kwargs
    ):
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
        if level == "precinct" and not kwargs.get("omit_locality_from_race_id"):
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
            choices = self._get_valid_contest_choices(contest)
            # if we're using vote completion mode "voteTypes", we look at the number of votes
            # for each vote type for each contest so we have to construct the reporting
            # statuses mapping here
            if subunit_fully_reporting_statuses is None and level == "precinct" and vote_completion_mode == "voteTypes":
                subunit_fully_reporting_statuses = self._get_precinct_fully_reporting_statuses_via_vote_types(contest, county_id=county_id)
            result["subunits"] = self.format_subunits(choices, level, subunit_fully_reporting_statuses, county_id=county_id)

        return result

    def convert(self, data, level="precinct", vote_completion_mode="percentReporting", office_id=None, **kwargs):
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
        timestamp = self.format_last_updated(dictified_data["Timestamp"])

        if level == "precinct" and vote_completion_mode == "percentReporting":
            # the default method of determining vote completion is to use the VoterTurnout
            # fields at the ElectionResult level in the precinct detail XML files
            subunit_fully_reporting_statuses = self._get_precinct_fully_reporting_statuses_via_percent_reporting(dictified_data, county_id=county_id)
        else:
            subunit_fully_reporting_statuses = None

        for contest in get_list(dictified_data.get("Contest")):
            election_type = self.get_race_type(dictified_data["ElectionName"], contest=contest)
            race_result = self.format_race(
                contest,
                election_date,
                election_type,
                level=level,
                county_id=county_id,
                timestamp=timestamp,
                vote_completion_mode=vote_completion_mode,
                subunit_fully_reporting_statuses=subunit_fully_reporting_statuses,
                **kwargs
            )

            race_office = race_result.get('office')
            if not office_id or race_office[0] in office_id:
                result[race_result["id"]] = race_result

        return result

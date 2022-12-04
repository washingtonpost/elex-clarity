from elexclarity.formatters.results import ClarityDetailXMLConverter
from elexclarity.formatters.base import ClarityConverter


def test_georgia_precinct_formatting_basic(atkinson_precincts, ga_county_mapping_fips):
    results = ClarityDetailXMLConverter("GA", county_lookup=ga_county_mapping_fips).convert(
        atkinson_precincts,
        level="precinct"
    )

    assert len(results) == 25
    assert results["2020-11-03_GA_G_P_13003"]["precinctsReportingPct"] == 100
    assert results["2020-11-03_GA_G_P_13003"]["lastUpdated"] == "2020-11-06T18:05:50Z"
    assert len(results["2020-11-03_GA_G_P_13003"]["subunits"]) == 4

    # Top level counts for this county
    counts = results["2020-11-03_GA_G_P_13003"]["counts"]
    assert counts["2020-11-03_GA_G_P_13003_donald_j_trump_i_rep"] == 2300
    assert counts["2020-11-03_GA_G_P_13003_joseph_r_biden_dem"] == 825
    assert counts["2020-11-03_GA_G_P_13003_jo_jorgensen_lib"] == 30

    # Pearson City precinct
    pearson = results["2020-11-03_GA_G_P_13003"]["subunits"]["13003_pearson-city"]
    assert pearson["precinctsReportingPct"] == 100
    assert pearson["expectedVotes"] == 564
    assert pearson["counts"]["2020-11-03_GA_G_P_13003_donald_j_trump_i_rep"] == 229
    assert pearson["counts"]["2020-11-03_GA_G_P_13003_joseph_r_biden_dem"] == 329
    assert pearson["counts"]["2020-11-03_GA_G_P_13003_jo_jorgensen_lib"] == 6

    # Willacoochee precinct
    willacoochee = results["2020-11-03_GA_G_P_13003"]["subunits"]["13003_willacoochee"]
    assert willacoochee["precinctsReportingPct"] == 100
    assert willacoochee["expectedVotes"] == 522
    assert willacoochee["counts"]["2020-11-03_GA_G_P_13003_donald_j_trump_i_rep"] == 342
    assert willacoochee["counts"]["2020-11-03_GA_G_P_13003_joseph_r_biden_dem"] == 174
    assert willacoochee["counts"]["2020-11-03_GA_G_P_13003_jo_jorgensen_lib"] == 6

def test_formatting_date_override(atkinson_precincts, ga_county_mapping_fips):
    results = ClarityDetailXMLConverter("GA", county_lookup=ga_county_mapping_fips).convert(
        atkinson_precincts,
        level="precinct",
        date="2022-12-06"
    )

    assert "2022-12-06_GA_G_P_13003" in results

def test_georgia_precinct_formatting_vote_types_completion_mode(atkinson_precincts, ga_county_mapping_fips):
    results = ClarityDetailXMLConverter("GA", county_lookup=ga_county_mapping_fips).convert(
        atkinson_precincts,
        level="precinct",
        office_id="P",
        vote_completion_mode="voteTypes"
    )

    # Pearson City precinct
    pearson = results["2020-11-03_GA_G_P_13003"]["subunits"]["13003_pearson-city"]
    assert pearson["precinctsReportingPct"] == 100
    assert pearson["expectedVotes"] == 564

    # Willacoochee precinct
    willacoochee = results["2020-11-03_GA_G_P_13003"]["subunits"]["13003_willacoochee"]
    assert willacoochee["precinctsReportingPct"] == 0
    assert willacoochee.get("expectedVotes") is None


def test_georgia_precinct_formatting_race_name_mapping(gwinnett_precincts, ga_county_mapping_fips):
    '''
    Gwinnett has some special contest names so this test makes sure that those get mapped
    to the right office IDs
    '''
    results = ClarityDetailXMLConverter("GA", county_lookup=ga_county_mapping_fips).convert(
        gwinnett_precincts,
        level="precinct"
    )

    # President
    assert "2020-11-03_GA_G_P_13135" in results
    # Loeffler
    assert "2020-11-03_GA_G_S2_13135" in results
    # Perdue
    assert "2020-11-03_GA_G_S_13135" in results


def test_georgia_state_formatting_basic(ga_counties, ga_county_mapping_fips):
    results = ClarityDetailXMLConverter("GA", county_lookup=ga_county_mapping_fips).convert(
        ga_counties,
        level="state"
    )

    assert len(results) == 2
    assert "2020-11-03_GA_G_P" in results
    assert "2020-11-03_GA_G_state_senate_district_1" in results
    assert not results["2020-11-03_GA_G_P"].get("subunits")
    assert results["2020-11-03_GA_G_P"]["precinctsReportingPct"] == 100
    assert results["2020-11-03_GA_G_P"]["lastUpdated"] == "2020-11-20T20:37:06Z"
    counts = results["2020-11-03_GA_G_P"]["counts"]
    assert counts["2020-11-03_GA_G_P_donald_j_trump_i_rep"] == 2461837
    assert counts["2020-11-03_GA_G_P_joseph_r_biden_dem"] == 2474507
    assert counts["2020-11-03_GA_G_P_jo_jorgensen_lib"] == 62138


def test_georgia_county_formatting_basic(ga_counties, ga_county_mapping_fips):
    results = ClarityDetailXMLConverter("GA", county_lookup=ga_county_mapping_fips).convert(
        ga_counties,
        level="county"
    )

    assert len(results["2020-11-03_GA_G_P"]["subunits"]) == 159
    # County-level counts
    wilcox_county = results["2020-11-03_GA_G_P"]["subunits"]["13315"]
    assert wilcox_county["id"] == "13315"
    assert wilcox_county["counts"]["2020-11-03_GA_G_P_donald_j_trump_i_rep"] == 2403
    assert wilcox_county["counts"]["2020-11-03_GA_G_P_joseph_r_biden_dem"] == 862
    assert wilcox_county["counts"]["2020-11-03_GA_G_P_jo_jorgensen_lib"] == 16


def test_georgia_county_formatting_alternate_county_mapping(ga_counties, ga_county_mapping_alternate):
    results = ClarityDetailXMLConverter("GA", county_lookup=ga_county_mapping_alternate).convert(
        ga_counties,
        level="county"
    )

    assert len(results) == 2
    catoosa_county = results["2020-11-03_GA_G_P"]["subunits"]["22"]
    assert catoosa_county["id"] == "22"
    assert len(catoosa_county["counts"].keys()) == 3
    assert catoosa_county["counts"]["2020-11-03_GA_G_P_donald_j_trump_i_rep"] == 25167
    assert catoosa_county["counts"]["2020-11-03_GA_G_P_joseph_r_biden_dem"] == 6932
    assert catoosa_county["counts"]["2020-11-03_GA_G_P_jo_jorgensen_lib"] == 494


def test_county_formatting_no_county_mapping(wv_counties):
    results = ClarityDetailXMLConverter("WV").convert(wv_counties, level="county")

    assert len(results) == 2
    marshall_county = results["2020-11-03_WV_G_P"]["subunits"]["marshall"]
    print(marshall_county)
    assert marshall_county["id"] == "marshall"
    assert len(marshall_county["counts"].keys()) == 4
    assert marshall_county["counts"]["2020-11-03_WV_G_P_GOP_donald_j_trump"] == 10435
    assert marshall_county["counts"]["2020-11-03_WV_G_P_DEM_joseph_r_biden"] == 3455
    assert marshall_county["counts"]["2020-11-03_WV_G_P_LBN_jo_jorgensen"] == 143
    assert marshall_county["counts"]["2020-11-03_WV_G_P_MTN_howie_hawkins"] == 47

def test_georgia_get_race_office():
    converter = ClarityConverter(statepostal="GA")

    assert converter.get_race_office("U.S. House Representative") == "H"
    assert converter.get_race_office("U.S. House Representative District 01") == "H_1"
    assert converter.get_race_office("U.S. House Representative District 10") == "H_10"
    assert converter.get_race_office("US Senate") == "S"
    assert converter.get_race_office("United States Senator") == "S"
    assert converter.get_race_office("U.S. Senate Loeffler Special") == "S2"
    assert converter.get_race_office("US President and Vice President") == "P"

from elexclarity.formatters.results import ClarityDetailXMLConverter


def test_georgia_precinct_formatting_basic(atkinson_precincts, ga_county_mapping_fips):
    results = ClarityDetailXMLConverter("GA", county_lookup=ga_county_mapping_fips).convert(atkinson_precincts, level="precinct")

    assert len(results) == 25
    assert results["2020-11-03_GA_G_P"]["precinctsReportingPct"] == 100
    assert results["2020-11-03_GA_G_P"]["lastUpdated"] == "2020-11-06T13:05:50Z"

    # Top level counts for this county
    counts = results["2020-11-03_GA_G_P"]["counts"]
    assert counts["donald_j_trump_i_rep"] == 2300
    assert counts["joseph_r_biden_dem"] == 825
    assert counts["jo_jorgensen_lib"] == 30

    # Subunit
    assert len(results["2020-11-03_GA_G_P"]["subunits"]) == 4
    pearson = results["2020-11-03_GA_G_P"]["subunits"]["13003_pearson_city"]
    assert pearson["counts"]["donald_j_trump_i_rep"] == 229
    assert pearson["counts"]["joseph_r_biden_dem"] == 329
    assert pearson["counts"]["jo_jorgensen_lib"] == 6


def test_georgia_precinct_formatting_race_name_mapping(gwinnett_precincts):
    results = ClarityDetailXMLConverter("GA").convert(gwinnett_precincts, level="precinct")

    # President
    assert "2020-11-03_GA_G_P" in results
    # Loeffler
    assert "2020-11-03_GA_G_S2" in results
    # Perdue
    assert "2020-11-03_GA_G_S" in results


def test_georgia_county_formatting_basic(ga_counties, ga_county_mapping_fips):
    results = ClarityDetailXMLConverter("GA", county_lookup=ga_county_mapping_fips).convert(ga_counties, level="county")

    assert len(results) == 2
    assert "2020-11-03_GA_G_P" in results
    assert "2020-11-03_GA_G_state_senate_district_1" in results
    assert results["2020-11-03_GA_G_P"]["precinctsReportingPct"] == 100
    assert results["2020-11-03_GA_G_P"]["lastUpdated"] == "2020-11-20T15:37:06Z"

    # County-level counts
    wilcox_county = results["2020-11-03_GA_G_P"]["subunits"]["13315"]
    assert wilcox_county["id"] == "13315"
    assert wilcox_county["counts"]["donald_j_trump_i_rep"] == 2403
    assert wilcox_county["counts"]["joseph_r_biden_dem"] == 862
    assert wilcox_county["counts"]["jo_jorgensen_lib"] == 16

    # Top level counts for this state
    counts = results["2020-11-03_GA_G_P"]["counts"]
    assert counts["donald_j_trump_i_rep"] == 2461837
    assert counts["joseph_r_biden_dem"] == 2474507
    assert counts["jo_jorgensen_lib"] == 62138


def test_georgia_county_formatting_alternate_county_mapping(ga_counties, ga_county_mapping_alternate):
    results = ClarityDetailXMLConverter("GA", county_lookup=ga_county_mapping_alternate).convert(ga_counties, level="county")

    assert len(results) == 2
    catoosa_county = results["2020-11-03_GA_G_P"]["subunits"]["22"]
    assert catoosa_county["id"] == "22"
    assert len(catoosa_county["counts"].keys()) == 3
    assert catoosa_county["counts"]["donald_j_trump_i_rep"] == 25167
    assert catoosa_county["counts"]["joseph_r_biden_dem"] == 6932
    assert catoosa_county["counts"]["jo_jorgensen_lib"] == 494


def test_county_formatting_no_county_mapping(wv_counties):
    results = ClarityDetailXMLConverter("WV").convert(wv_counties, level="county")

    assert len(results) == 2
    marshall_county = results["2020-11-03_WV_G_P"]["subunits"]["marshall"]
    assert marshall_county["id"] == "marshall"
    assert len(marshall_county["counts"].keys()) == 4
    assert marshall_county["counts"]["donald_j_trump"] == 10435
    assert marshall_county["counts"]["joseph_r_biden"] == 3455
    assert marshall_county["counts"]["jo_jorgensen"] == 143
    assert marshall_county["counts"]["howie_hawkins"] == 47

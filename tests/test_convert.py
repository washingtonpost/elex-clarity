from elexclarity.convert import convert


def test_precinct_level_results_raw(bacon_precincts):
    results = convert([bacon_precincts], statepostal="GA", level="precinct", style="raw")
    assert isinstance(results, list)


def test_county_settings(bacon_precincts):
    results = convert([bacon_precincts], statepostal="GA", level="precinct", style="raw")
    assert isinstance(results, list)


def test_precinct_level_results(bacon_precincts, ga_county_mapping_fips):
    results = convert([bacon_precincts], statepostal="GA", level="precinct", countyMapping=ga_county_mapping_fips)

    assert len(results) == 20
    assert "2020-11-03_GA_G_P_13005" in results


def test_county_level_results(ga_counties, ga_county_mapping_fips):
    results = convert([ga_counties], statepostal="GA", level="county", countyMapping=ga_county_mapping_fips)

    assert len(results) == 2
    assert "2020-11-03_GA_G_P" in results

def test_single_result_object(ga_counties, ga_county_mapping_fips):
    results = convert(ga_counties, statepostal="GA", level="county", countyMapping=ga_county_mapping_fips)

    assert len(results) == 2
    assert "2020-11-03_GA_G_P" in results

def test_filter_officeid(ga_counties, ga_county_mapping_fips):
    results = convert(ga_counties, statepostal="GA", level="county", countyMapping=ga_county_mapping_fips, officeID="P")

    assert len(results) == 1
    assert "2020-11-03_GA_G_P" in results
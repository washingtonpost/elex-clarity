import os
import pytest
from elexclarity.convert import convert
from elexclarity.utils import get_json_from_file, get_fips_mapping

_TEST_FOLDER = os.path.dirname(__file__)
FIXTURE_DIR = os.path.join(_TEST_FOLDER, 'fixtures')


@pytest.fixture
def atkinson_precincts(get_fixture):
    path = os.path.join(FIXTURE_DIR, "atkinson_precincts_11-3.xml")
    with open(path) as f:
        fixture = f.read()
    return fixture


@pytest.fixture
def bacon_precincts(get_fixture):
    path = os.path.join(FIXTURE_DIR, "bacon_precincts_11-3.xml")
    with open(path) as f:
        fixture = f.read()
    return fixture


@pytest.fixture
def fulton_precincts(get_fixture):
    path = os.path.join(FIXTURE_DIR, "fulton_precincts_11-3.xml")
    with open(path) as f:
        fixture = f.read()
    return fixture


@pytest.fixture
def atkinson_presidential_contest(get_fixture):
    path = os.path.join(FIXTURE_DIR, "atkinson_precincts_2020-11-03_GA_G_P.xml")
    with open(path) as f:
        fixture = f.read()
    return fixture


@pytest.fixture
def georgia_counties(get_fixture):
    path = os.path.join(FIXTURE_DIR, "2020-11-03_GA.xml")
    with open(path) as f:
        fixture = f.read()
    return fixture


@pytest.fixture
def alternate_ga_county_mapping(get_fixture):
    path = os.path.join(FIXTURE_DIR, "alternate_GA_county_mapping.json")
    return get_json_from_file(path)


@pytest.fixture
def wv_counties(get_fixture):
    path = os.path.join(FIXTURE_DIR, "2020-11-03_WV_G.xml")
    with open(path) as f:
        fixture = f.read()
    return fixture


def test_format_atkinson_precincts(atkinson_precincts):
    results = convert(atkinson_precincts, statepostal="GA", level="precinct")

    assert len(results.keys()) == 25
    assert "President of the United States" in results.keys()
    assert results["President of the United States"]["precinctsReportingPct"] == 100

    # Top level counts for this county
    counts = results["President of the United States"]["counts"]
    assert counts["donald-j-trump-i-rep"] == 2300
    assert counts["joseph-r-biden-dem"] == 825
    assert counts["jo-jorgensen-lib"] == 30

    # Subunit
    assert len(results["President of the United States"]["subunits"].keys()) == 4

    print(results["President of the United States"]["subunits"])

    pearson = results["President of the United States"]["subunits"]["13003_pearson-city"]
    assert pearson["counts"]["donald-j-trump-i-rep"] == 229
    assert pearson["counts"]["joseph-r-biden-dem"] == 329
    assert pearson["counts"]["jo-jorgensen-lib"] == 6


def test_format_bacon_precincts(bacon_precincts):
    results = convert(bacon_precincts, statepostal="GA", level="precinct")

    assert len(results.keys()) == 20
    assert "President of the United States" in results.keys()
    assert results["President of the United States"]["precinctsReportingPct"] == 100

    # Top level counts for this county
    counts = results["President of the United States"]["counts"]
    assert counts["donald-j-trump-i-rep"] == 4018
    assert counts["joseph-r-biden-dem"] == 625
    assert counts["jo-jorgensen-lib"] == 25

    # Subunit
    assert len(results["President of the United States"]["subunits"].keys()) == 1

    print(results["President of the United States"]["subunits"])
    douglas = results["President of the United States"]["subunits"]["13005_douglas"]

    assert douglas["counts"]["donald-j-trump-i-rep"] == 4018
    assert douglas["counts"]["joseph-r-biden-dem"] == 625
    assert douglas["counts"]["jo-jorgensen-lib"] == 25


def test_format_fulton_precincts(fulton_precincts):
    results = convert(fulton_precincts, statepostal="GA", level="precinct")

    assert len(results.keys()) == 60
    assert "President of the United States" in results.keys()
    assert results["President of the United States"]["precinctsReportingPct"] == 100

    # Top level counts for this county
    counts = results["President of the United States"]["counts"]
    assert counts["donald-j-trump-i-rep"] == 137200
    assert counts["joseph-r-biden-dem"] == 381057
    assert counts["jo-jorgensen-lib"] == 6275

    # Subunit
    assert len(results["President of the United States"]["subunits"].keys()) == 384

    precinct = results["President of the United States"]["subunits"]["13121_ss22"]
    assert precinct["counts"]["donald-j-trump-i-rep"] == 691
    assert precinct["counts"]["joseph-r-biden-dem"] == 1082
    assert precinct["counts"]["jo-jorgensen-lib"] == 19


def test_format_single_contest(atkinson_presidential_contest):
    results = convert(atkinson_presidential_contest, statepostal="GA", level="precinct")

    assert len(results.keys()) == 1
    assert "President of the United States" in results.keys()
    assert results["President of the United States"]["precinctsReportingPct"] == 100

    # Top level counts for this county
    counts = results["President of the United States"]["counts"]
    assert counts["donald-j-trump-i-rep"] == 2300
    assert counts["joseph-r-biden-dem"] == 825
    assert counts["jo-jorgensen-lib"] == 30


def test_format_georgia_counties(georgia_counties):
    results = convert(georgia_counties, statepostal="GA", level="county")

    assert len(results.keys()) == 2
    assert "President of the United States" in results.keys()
    assert "State Senate District 1" in results.keys()
    assert results["President of the United States"]["precinctsReportingPct"] == 100

    # County-level counts
    wilcox_county = results["President of the United States"]["subunits"]["13315"]
    assert wilcox_county["id"] == "13315"
    assert wilcox_county["counts"]["donald-j-trump-i-rep"] == 2403
    assert wilcox_county["counts"]["joseph-r-biden-dem"] == 862
    assert wilcox_county["counts"]["jo-jorgensen-lib"] == 16

    # Top level counts for this state
    counts = results["President of the United States"]["counts"]
    assert counts["donald-j-trump-i-rep"] == 2461837
    assert counts["joseph-r-biden-dem"] == 2474507
    assert counts["jo-jorgensen-lib"] == 62138


def test_alternate_county_mapping(georgia_counties, alternate_ga_county_mapping):
    results = convert(georgia_counties, statepostal="GA", level="county", countymapping=alternate_ga_county_mapping)

    assert len(results.keys()) == 2
    catoosa_county = results["President of the United States"]["subunits"]["22"]
    assert catoosa_county["id"] == "22"
    assert len(catoosa_county["counts"].keys()) == 3
    assert catoosa_county["counts"]["donald-j-trump-i-rep"] == 25167
    assert catoosa_county["counts"]["joseph-r-biden-dem"] == 6932
    assert catoosa_county["counts"]["jo-jorgensen-lib"] == 494


def test_no_county_mapping(wv_counties):
    results = convert(wv_counties, statepostal="WV", level="county")

    assert len(results.keys()) == 2
    marshall_county = results["PRESIDENT"]["subunits"]["marshall"]
    assert marshall_county["id"] == "marshall"
    assert len(marshall_county["counts"].keys()) == 4
    assert marshall_county["counts"]["donald-j-trump"] == 10435
    assert marshall_county["counts"]["joseph-r-biden"] == 3455
    assert marshall_county["counts"]["jo-jorgensen"] == 143
    assert marshall_county["counts"]["howie-hawkins"] == 47

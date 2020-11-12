import os
import pytest
from elexclarity.convert import convert

_TEST_FOLDER = os.path.dirname(__file__)
FIXTURE_DIR = os.path.join(_TEST_FOLDER, 'fixtures')

@pytest.fixture
def atkinson_precincts(get_fixture):
    return get_fixture("atkinson_precincts_11-3.xml")

def test_format_atkinson_preconcts(atkinson_precincts):
    results = convert(atkinson_precincts)
    # print(results)
    # assert results["2019-11-05_VA_G_Y_23"]["precinctsReportingPct"] == 100
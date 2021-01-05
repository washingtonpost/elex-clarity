import os
import json
import sys
import logging
import pytest
import requests
from betamax import Betamax
from betamax_serializers import pretty_json

from elexclarity.client import ElectionsClient


_TEST_FOLDER = os.path.dirname(__file__)
FIXTURE_DIR = os.path.join(_TEST_FOLDER, 'fixtures')


@pytest.fixture(autouse=True, scope='session')
def setup_logging():
    LOG = logging.getLogger('elexclarity')
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s %(name)s %(message)s'))
    LOG.addHandler(handler)


@pytest.fixture(scope='session')
def get_fixture():
    def _get_fixture(filename, load=False):
        fileobj = open(os.path.join(FIXTURE_DIR, filename))
        if load:
            return json.load(fileobj)
        return fileobj.read()
    return _get_fixture


@pytest.fixture(autouse=True, scope='session')
def _setup_betamax():
    Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
    config = Betamax.configure()
    config.cassette_library_dir = FIXTURE_DIR
    config.default_cassette_options['record_mode'] = 'once'
    config.default_cassette_options['match_requests_on'] = ['path', 'host']
    config.default_cassette_options['serialize_with'] = 'prettyjson'


@pytest.fixture(scope='session')
def requests_session():
    return requests.Session()


@pytest.fixture(scope='session')
def api_client(requests_session):
    return ElectionsClient('https://results.enr.clarityelections.com/', session=requests_session)


@pytest.fixture(scope='session')
def recorder(requests_session):
    return Betamax(requests_session)


@pytest.fixture(scope='session')
def ga_2020_summary(recorder, api_client):
    with recorder.use_cassette('results/GA_2020_summary'):
        return api_client.get_summary(105369, 'GA')


@pytest.fixture
def bacon_precincts(get_fixture):
    return get_fixture("results/ga_bacon_precincts_11-3.xml")


@pytest.fixture
def atkinson_precincts(get_fixture):
    return get_fixture("results/ga_atkinson_precincts_11-3.xml")


@pytest.fixture
def gwinnett_precincts(get_fixture):
    return get_fixture("results/ga_gwinnett_precincts_11-3.xml")


@pytest.fixture
def ga_counties(get_fixture):
    return get_fixture("results/ga_counties_11-3.xml")


@pytest.fixture
def wv_counties(get_fixture):
    return get_fixture("results/wv_counties_11-3.xml")


@pytest.fixture
def ga_county_mapping_fips(get_fixture):
    return get_fixture("mappings/GA_county_fips.json", load=True)


@pytest.fixture
def ga_county_mapping_alternate(get_fixture):
    return get_fixture("mappings/GA_county_alternate.json", load=True)


@pytest.fixture
def ga_county_settings(get_fixture):
    return get_fixture("settings/GA_2020.json", load=True)

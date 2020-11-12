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
    def _get_fixture(filename, load=True):
        fileobj = open(os.path.join(FIXTURE_DIR, filename))
        if load:
            return json.load(fileobj)
        return fileobj
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
def ga_2020_summary(recorder, ap_client):
    with recorder.use_cassette('ga_2020_summary'):
        return ap_client.get_summary(105369, 'GA')

import pytest


def test_get_summary_basic(recorder, api_client):
    with recorder.use_cassette('ga_2020_summary'):
        assert len(api_client.get_summary(105369, 'GA')) == 298

def test_get_summary_basic(recorder, api_client):
    with recorder.use_cassette('results/GA_2020_summary'):
        assert len(api_client.get_summary(105369, 'GA')) == 298


def test_get_settings_basic(recorder, api_client):
    with recorder.use_cassette('settings/GA_2020'):
        assert len(api_client.get_settings(105369, 'GA')) == 19

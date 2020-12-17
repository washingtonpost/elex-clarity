from elexclarity.formatters.settings import ClaritySettingsConverter


def test_format_county_settings(recorder, api_client):
    with recorder.use_cassette('settings/GA_2020'):
        settings = api_client.get_settings(105369, 'GA')

        result = ClaritySettingsConverter().convert(settings, level="county")
        assert len(result) == 159
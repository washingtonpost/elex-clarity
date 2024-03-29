from elexclarity.formatters.settings import ClaritySettingsConverter


def test_format_county_settings(recorder, api_client, ga_county_mapping_fips):
    with recorder.use_cassette('settings/GA_2020'):
        settings = api_client.get_settings(105369, 'GA', None)
        result = ClaritySettingsConverter('GA', county_lookup=ga_county_mapping_fips).convert(settings, office_id=("S"), level="county")
        assert len(result) == 159
        assert result["2020-11-03_GA_G_S_13001"] == {
            'clarityId': '105371',
            'name': 'Appling',
            'id': '2020-11-03_GA_G_S_13001',
            'lastUpdated': '2020-11-16T20:48:35Z',
            'version': '271560'
        }
        assert result["2020-11-03_GA_G_S_13277"] == {
            'clarityId': '105507',
            'name': 'Tift',
            'id': '2020-11-03_GA_G_S_13277',
            'lastUpdated': '2020-11-06T22:50:20Z',
            'version': '270028'
        }

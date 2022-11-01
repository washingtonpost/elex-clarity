from elexclarity.formatters.base import ClarityConverter

def test_get_county_id():
    converter = ClarityConverter("AR", county_lookup={"Hot Spring": "1234"})

    assert converter.get_county_id("Hot Spring") == "1234"
    assert converter.get_county_id("Hot_Spring") == "1234"
    assert converter.get_county_id("Not a County") == "not_a_county"

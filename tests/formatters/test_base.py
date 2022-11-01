from elexclarity.formatters.base import ClarityConverter


def test_arkansas_get_county_id():
    converter = ClarityConverter("AR", county_lookup={"Hot Spring": "1234"})

    assert converter.get_county_id("Hot Spring") == "1234"
    assert converter.get_county_id("Hot_Spring") == "1234"
    assert converter.get_county_id("Not a County") == "not_a_county"


def test_georgia_get_county_id():
    converter = ClarityConverter(
        "GA", county_lookup={"Ben Hill": "1234", "Jeff Davis": "3456"}
    )

    assert converter.get_county_id("Ben_Hill") == "1234"
    assert converter.get_county_id("Jeff_Davis") == "3456"

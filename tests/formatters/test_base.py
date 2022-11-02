from elexclarity.formatters.base import ClarityConverter
from datetime import datetime
from dateutil import tz


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


def test_get_timestamp():
    converter = ClarityConverter("IA")

    assert converter.get_timestamp("10/17/2022 2:21:22 PM CDT") == datetime(2022, 10, 17, 19, 21, 22, tzinfo=tz.gettz("UTC"))

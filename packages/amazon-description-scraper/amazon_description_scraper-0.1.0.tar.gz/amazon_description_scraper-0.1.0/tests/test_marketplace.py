from amzsc.utils import get_zone


def test_get_zone() -> None:
    """Test the get_zone function."""
    zone = get_zone("US")
    assert zone == "com", "Expected zone for US marketplace is 'com'"

    zone = get_zone("USA")
    assert zone == "com", "Expected zone for USA marketplace is 'com'"

    zone = get_zone("UK")
    assert zone == "co.uk", "Expected zone for UK marketplace is 'co.uk'"

    zone = get_zone("GB")
    assert zone == "co.uk", "Expected zone for UK marketplace is 'co.uk'"

    zone = get_zone("DE")
    assert zone == "de", "Expected zone for DE marketplace is 'de'"

    zone = get_zone("INVALID")
    assert zone == "de", "Expected zone for invalid marketplace is 'de'"

    zone = get_zone()
    assert zone == "de", "Expected default zone is 'de'"

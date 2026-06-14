from app.core.countries import parse_location


def test_parses_city_and_country_code():
    assert parse_location("Warszawa, PL") == ("Warszawa", "pl", "Poland")


def test_parses_country_full_name():
    assert parse_location("Warsaw, Poland") == ("Warsaw", "pl", "Poland")


def test_city_only_has_no_country():
    assert parse_location("Warszawa") == ("Warszawa", None, None)


def test_unknown_tail_is_not_treated_as_country():
    # A region that isn't a known country stays part of the input, no country resolved.
    assert parse_location("Warszawa, Mazowieckie") == ("Warszawa", None, None)


def test_empty_or_none():
    assert parse_location("") == ("", None, None)
    assert parse_location(None) == ("", None, None)


def test_case_and_whitespace_insensitive():
    assert parse_location("  warsaw ,  poland ") == ("warsaw", "pl", "Poland")

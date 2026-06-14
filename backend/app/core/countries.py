"""Lightweight location parsing shared by the job sources and the search filter.

Job boards label location inconsistently — Jooble returns coarse country names
("Poland"), Apify/Indeed returns cities ("Warszawa") and needs an ISO country code to
pick the right domain (pl.indeed.com). We let users type a single "City, Country" string
(e.g. "Warszawa, PL") and split it into the city, an ISO-3166 alpha-2 code, and the
English country name so each consumer can use whichever form it needs."""

# Small, extensible set — covers the markets in scope; extend as needed.
COUNTRY_NAMES: dict[str, str] = {
    "pl": "Poland",
    "us": "United States",
    "gb": "United Kingdom",
    "uk": "United Kingdom",
    "de": "Germany",
    "fr": "France",
    "es": "Spain",
    "it": "Italy",
    "nl": "Netherlands",
    "ie": "Ireland",
    "ua": "Ukraine",
    "ca": "Canada",
    "cz": "Czechia",
}

_NAME_TO_CODE: dict[str, str] = {name.lower(): code for code, name in COUNTRY_NAMES.items()}


def parse_location(text: str | None) -> tuple[str, str | None, str | None]:
    """Split "City, Country" into (city, country_code, country_name).

    The country is taken from the last comma-separated token only when it is a recognised
    ISO code or country name; otherwise it's left as part of the input and no country is
    resolved (so "Warszawa, Mazowieckie" yields city "Warszawa", no country). Returns
    ("", None, None) for empty/None input.
    """
    parts = [p.strip() for p in (text or "").split(",") if p.strip()]
    if not parts:
        return ("", None, None)
    city = parts[0]
    if len(parts) > 1:
        tail = parts[-1].lower()
        if tail in COUNTRY_NAMES:
            return (city, tail, COUNTRY_NAMES[tail])
        if tail in _NAME_TO_CODE:
            code = _NAME_TO_CODE[tail]
            return (city, code, COUNTRY_NAMES[code])
    return (city, None, None)

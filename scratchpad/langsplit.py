"""Group census rows by the working language of the meeting.

ENGLISH = a society in an anglophone country, or an international / Europe-wide
body (those publish and present in English by default). OTHER = a national society
elsewhere, whose programme and abstract book are in its own language — which is
exactly the population the mandatory local-language sweep exists for.

A missing country is OTHER: never silently promote a row into the English set on
absent evidence.
"""
import re

ANGLOPHONE = re.compile(
    r"^\s*(US|USA|U\.S\.|UK|U\.K\.|United States|United Kingdom|Canada|Australia|"
    r"Ireland|New Zealand|India|Singapore|South Africa)\b",
    re.I,
)
#: bodies with no single national language
MULTINATIONAL = re.compile(r"^\s*(international|europe|european|global|worldwide|pan[- ])", re.I)
#: a country string that merely mentions the US/UK alongside others
MENTIONS_ANGLO = re.compile(r"\b(US|USA|UK)\b", re.I)

ENGLISH = "ENGLISH"
OTHER = "OTHER"


def group(country):
    c = (country or "").strip()
    if not c:
        return OTHER
    if ANGLOPHONE.match(c) or MULTINATIONAL.match(c) or MENTIONS_ANGLO.search(c):
        return ENGLISH
    return OTHER


def partition(rows, country):
    """Split rows into the two groups, preserving order within each."""
    out = {ENGLISH: [], OTHER: []}
    for r in rows:
        out[group(country(r))].append(r)
    return out

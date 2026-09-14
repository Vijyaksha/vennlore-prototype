"""Tests for langsplit — grouping census rows into English-language and other.

The split is by the working language of the meeting, inferred from the society's
country. Anglophone countries and international/Europe-wide bodies run in English;
national societies elsewhere run in their own language (which is why the mandatory
local-language sweep exists).
"""
import langsplit


def test_anglophone_countries_are_english():
    for c in ("US", "USA", "UK", "Canada", "Australia", "Ireland",
              "New Zealand", "India", "Singapore", "South Africa"):
        assert langsplit.group(c) == "ENGLISH", c


def test_international_and_europe_wide_bodies_are_english():
    for c in ("international", "International", "Europe", "europe/international",
              "global", "international (rotating Europe/US/Asia)"):
        assert langsplit.group(c) == "ENGLISH", c


def test_a_country_that_merely_mentions_us_is_still_english():
    assert langsplit.group("US/international") == "ENGLISH"
    assert langsplit.group("US (Hawaii)") == "ENGLISH"


def test_non_anglophone_national_societies_are_other():
    for c in ("China", "Russia", "Japan", "Spain", "Italy", "Germany",
              "Brazil", "South Korea", "Iran", "Portugal"):
        assert langsplit.group(c) == "OTHER", c


def test_a_missing_country_is_other_so_it_is_never_silently_promoted():
    assert langsplit.group(None) == "OTHER"
    assert langsplit.group("") == "OTHER"


def test_partition_puts_every_english_row_before_every_other_row():
    rows = [(1, "China"), (2, "US"), (3, "Japan"), (4, "UK")]

    out = langsplit.partition(rows, country=lambda r: r[1])

    assert [r[0] for r in out["ENGLISH"]] == [2, 4]
    assert [r[0] for r in out["OTHER"]] == [1, 3]


def test_partition_loses_no_rows():
    rows = [(i, c) for i, c in enumerate(["US", "China", "UK", "Iran", "Europe"])]

    out = langsplit.partition(rows, country=lambda r: r[1])

    assert len(out["ENGLISH"]) + len(out["OTHER"]) == len(rows)


def test_partition_preserves_the_original_order_within_each_group():
    rows = [(1, "China"), (2, "US"), (3, "Russia"), (4, "Canada"), (5, "Japan")]

    out = langsplit.partition(rows, country=lambda r: r[1])

    assert [r[0] for r in out["ENGLISH"]] == [2, 4]
    assert [r[0] for r in out["OTHER"]] == [1, 3, 5]

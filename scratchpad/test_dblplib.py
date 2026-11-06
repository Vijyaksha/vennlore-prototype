"""Tests for dblplib — turning DBLP SPARQL results and Crossref facets into census rows.

The unit is accepted contributed papers (Rupert, 2026-09-12); workshop volumes are separate.
"""
import dblplib


# --- main-track vs workshop split -------------------------------------------

def test_workshop_volumes_are_separated_from_the_main_track():
    vols = [
        dict(stream="conf/cvpr", year=2024, vtitle="IEEE/CVF Conference on Computer Vision and Pattern Recognition, CVPR 2024, Seattle", n=2715),
        dict(stream="conf/cvpr", year=2024, vtitle="IEEE/CVF Conference on Computer Vision and Pattern Recognition, CVPR 2024 - Workshops, Seattle", n=803),
    ]
    split = dblplib.main_track_split(vols)
    assert split[("conf/cvpr", 2024)] == {"main": 2715, "workshop": 803}


def test_companion_adjunct_tutorial_and_demo_volumes_count_as_workshop():
    vols = [dict(stream="conf/www", year=2025, vtitle="Companion Proceedings of the ACM Web Conference 2025", n=877),
            dict(stream="conf/www", year=2025, vtitle="Proceedings of the ACM on Web Conference 2025", n=1000),
            dict(stream="conf/chi", year=2025, vtitle="Extended Abstracts of the CHI Conference 2025", n=50)]
    split = dblplib.main_track_split(vols)
    assert split[("conf/www", 2025)] == {"main": 1000, "workshop": 877}
    assert split[("conf/chi", 2025)]["workshop"] == 50


# --- which year to write, and the cadence -----------------------------------

def test_latest_year_prefers_2025_when_it_has_a_main_track_count():
    split = {("conf/x", 2024): {"main": 900, "workshop": 0}, ("conf/x", 2025): {"main": 950, "workshop": 10}}
    assert dblplib.latest_year("conf/x", split) == 2025


def test_latest_year_falls_back_to_2024_for_a_biennial_that_did_not_meet_in_2025():
    split = {("conf/eccv", 2024): {"main": 2300, "workshop": 500}}
    assert dblplib.latest_year("conf/eccv", split) == 2024


def test_cadence_is_the_share_of_recent_years_with_records():
    yearly = {("conf/eccv", y): 1 for y in (2018, 2020, 2022, 2024)}
    assert dblplib.cadence("conf/eccv", yearly, years=range(2018, 2026)) == 0.5
    yearly2 = {("conf/annual", y): 1 for y in range(2018, 2026)}
    assert dblplib.cadence("conf/annual", yearly2, years=range(2018, 2026)) == 1


# --- de-duplication against what the workbook already holds -----------------

def test_existing_rows_are_matched_by_acronym_or_normalised_name():
    existing = [dict(sheet="Census - Physical Sciences", conference="IEEE NSS/MIC/RTSD (Nuclear Science Symposium + Medical Imaging Conference)"),
                dict(sheet="Census - Life Sciences", conference="ISMB Conference"),
                dict(sheet="Census - Physical Sciences", conference="CLEO (co-sponsored with APS-DLS and IEEE Photonics)")]
    hit = dblplib.find_existing("IEEE Nuclear Science Symposium and Medical Imaging Conference (NSS/MIC)", existing)
    assert hit and hit["sheet"] == "Census - Physical Sciences"
    assert dblplib.find_existing("Intelligent Systems for Molecular Biology (ISMB)", existing)["sheet"] == "Census - Life Sciences"
    assert dblplib.find_existing("Conference on Neural Information Processing Systems (NeurIPS)", existing) is None


def test_the_same_stream_listed_under_two_titles_is_one_row():
    meta = [dict(stream="conf/hci", title="HCI International Conference (HCII)"),
            dict(stream="conf/hci", title="International Conference on Human-Computer Interaction (HCI International)")]
    assert len(dblplib.one_row_per_stream(meta)) == 1


# --- Crossref container titles -> conference series -------------------------

def test_crossref_titles_collapse_to_a_series_key_without_year_or_ordinal():
    a = dblplib.series_key("2024 IEEE International Conference on Robotics and Automation (ICRA)")
    b = dblplib.series_key("2025 IEEE International Conference on Robotics and Automation (ICRA)")
    assert a == b
    assert dblplib.series_key("Proceedings of the 32nd ACM International Conference on Multimedia") == \
           dblplib.series_key("Proceedings of the 33rd ACM International Conference on Multimedia")
    assert dblplib.series_key("ICASSP 2025 - 2025 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)") == \
           dblplib.series_key("ICASSP 2024 - 2024 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)")


def test_publisher_series_that_are_not_a_conference_are_skipped():
    assert dblplib.is_not_a_conference("AIP Conference Proceedings")
    assert dblplib.is_not_a_conference("SAE Technical Paper Series")
    assert dblplib.is_not_a_conference("IOP Conference Series Earth and Environmental Science")
    assert dblplib.is_not_a_conference("Journal of Physics: Conference Series")
    assert not dblplib.is_not_a_conference("2025 IEEE International Symposium on Circuits and Systems (ISCAS)")


# --- the census row --------------------------------------------------------

def test_a_row_carries_the_figure_year_source_rung_and_tier():
    row = dblplib.census_row(stream="conf/nips", title="Conference on Neural Information Processing Systems (NeurIPS)",
                             year=2025, main=5824, workshop=0, events_per_yr=1, crossref=5823)
    assert row["abstracts_numeric"] == 5824 and row["year"] == 2025
    assert row["source_url"] == "https://dblp.org/streams/conf/nips"
    assert row["rung"] == 4 and row["tier"] == "VERIFIED" and row["events_per_yr"] == 1
    assert "5,823" in row["method"] and "workshop" in row["method"].lower()


def test_tier_follows_the_bar_on_the_main_track_count():
    assert dblplib.tier_for(1500) == "VERIFIED"
    assert dblplib.tier_for(1499) == "BORDERLINE"
    assert dblplib.tier_for(800) == "BORDERLINE"
    assert dblplib.tier_for(799) == "OUT"


# --- de-duplication defects found in the first dry run -------------------------

def test_generic_organisation_acronyms_never_match_rows():
    existing = [dict(sheet="Census - Physical Sciences", conference="CLEO (co-sponsored with APS-DLS and IEEE Photonics)")]
    assert dblplib.find_existing("IEEE International Conference on Robotics and Automation (ICRA)", existing) is None
    assert dblplib.find_existing("ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD)", existing) is None
    assert dblplib.find_existing("IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)", existing) is None


def test_an_acronym_collision_between_different_meetings_is_not_a_match():
    existing = [dict(sheet="Census - Medicine & Health", conference="ICML (lymphoma, Lugano)"),
                dict(sheet="Census - Chemistry", conference="CAC - Chemometrics in Analytical Chemistry")]
    assert dblplib.find_existing("International Conference on Machine Learning (ICML)", existing) is None
    assert dblplib.find_existing("China Automation Congress (CAC)", existing) is None


def test_a_crossref_only_row_cites_the_facet_query_and_carries_the_bar():
    row = dblplib.crossref_row(title="2025 44th Chinese Control Conference (CCC)", year=2025, n=1556, events_per_yr=1)
    assert row["abstracts_numeric"] == 1556 and row["tier"] == "VERIFIED" and row["rung"] == 4
    assert "api.crossref.org" in row["source_url"] and "proceedings-article" in row["source_url"]
    assert "Chinese Control Conference" in row["conference"] and "2025" not in row["conference"].split("(")[0].strip()[:4]


def test_a_collision_with_a_single_distinguishing_word_is_still_a_collision():
    existing = [dict(sheet="Census - Chemistry", conference="ICC — International Congress on Catalysis")]
    assert dblplib.find_existing("IEEE International Conference on Communications (ICC)", existing) is None

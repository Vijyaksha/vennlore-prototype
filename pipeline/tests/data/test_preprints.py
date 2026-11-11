"""Preprints from arXiv, bioRxiv and medRxiv become contract Talk rows, so every
engine can recommend papers next to programme talks. Fixtures only, no network."""
import json

from gps_core.contracts import validate
from gps_data.preprints import ID_BASE, ID_SPAN, dedupe, paper_url, parse_arxiv, parse_rxiv, preprint_id
from gps_data.talk import to_row

ARXIV = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2511.01234v2</id>
    <published>2025-11-03T17:59:59Z</published>
    <title>Graph   neural networks for
      exciton transport</title>
    <summary>  We learn exciton hopping
      rates with message passing.  </summary>
    <arxiv:primary_category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.LG"/><category term="cond-mat.mtrl-sci"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2511.05555v1</id>
    <published>2025-11-04T10:00:00Z</published>
    <title>Photocurrent spectroscopy of perovskites</title>
    <summary>Transient photocurrent reveals trap states.</summary>
    <arxiv:primary_category term="cond-mat.mtrl-sci" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>"""

RXIV = json.dumps({
    "messages": [{"status": "ok", "cursor": 0, "count": 2, "total": 2}],
    "collection": [
        {"doi": "10.1101/2025.10.30.685000", "title": "Optogenetic photocurrents in neurons",
         "authors": "Doe, J.; Roe, R.", "date": "2025-11-01", "version": "2",
         "category": "neuroscience", "abstract": "We record light-gated currents.",
         "server": "bioRxiv"},
        {"doi": "10.1101/2025.10.29.25339000", "title": "Wearable sensors for sepsis",
         "authors": "Lee, K.", "date": "2025-10-30", "version": "1",
         "category": "infectious diseases", "abstract": "A cohort study.",
         "server": "medRxiv"},
    ]})


def test_arxiv_entries_become_contract_valid_talks():
    talks = parse_arxiv(ARXIV)
    assert [t.external_id for t in talks] == ["arXiv:2511.01234", "arXiv:2511.05555"]
    t = talks[0]
    assert t.title == "Graph neural networks for exciton transport"
    assert t.abstract == "We learn exciton hopping rates with message passing."
    assert t.type == "preprint:arxiv" and t.topics == ("Machine Learning", "Materials Science")
    assert t.publication_reference == "arXiv 2025-11-03"
    assert t.start is None and t.presenter_ids == ()
    for talk in talks:
        validate("talk", to_row(talk))


def test_rxiv_items_become_contract_valid_talks():
    bio, med = parse_rxiv(RXIV)
    assert bio.external_id == "doi:10.1101/2025.10.30.685000" and bio.type == "preprint:biorxiv"
    assert med.type == "preprint:medrxiv" and med.topics == ("infectious diseases",)
    assert bio.publication_reference == "bioRxiv 2025-11-01"
    for talk in (bio, med):
        validate("talk", to_row(talk))


def test_units_mark_non_physics_papers_as_another_domain():
    """The programme is a physics meeting: a physics arXiv paper has unknown
    division (never 'cross-domain' on its own), anything else has its own unit."""
    gnn, perov = parse_arxiv(ARXIV)
    bio, med = parse_rxiv(RXIV)
    assert gnn.units == ("arXiv:cs.LG",)
    assert perov.units == ()
    assert bio.units == ("bioRxiv:neuroscience",) and med.units == ("medRxiv:infectious diseases",)


def test_ids_are_stable_and_clear_of_programme_ids():
    a = preprint_id("arXiv:2511.01234")
    assert a == preprint_id("arXiv:2511.01234") != preprint_id("arXiv:2511.05555")
    assert ID_BASE <= a < ID_BASE + ID_SPAN
    assert ID_BASE + ID_SPAN <= 2_147_483_647   # Postgres integer column


def test_dedupe_keeps_one_row_per_paper():
    talks = parse_arxiv(ARXIV) + parse_arxiv(ARXIV) + parse_rxiv(RXIV)
    assert len(dedupe(talks)) == 4


def test_paper_url():
    assert paper_url("arXiv:2511.01234") == "https://arxiv.org/abs/2511.01234"
    assert paper_url("doi:10.1101/2025.10.30.685000") == "https://doi.org/10.1101/2025.10.30.685000"
    assert paper_url("SMT26-0000010") is None and paper_url(None) is None


def test_arxiv_categories_get_readable_topic_names():
    gnn, perov = parse_arxiv(ARXIV)
    assert gnn.topics == ("Machine Learning", "Materials Science")
    assert perov.topics == ("Materials Science",)
    assert gnn.units == ("arXiv:cs.LG",)      # units keep the code: they are identifiers

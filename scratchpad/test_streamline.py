"""Tests for streamline: the slim wave-brief generator (post-pilot waves only)."""
import streamline


def brief():
    return streamline.build_wave_brief(
        field='Social Sciences',
        field_notes='docs/business/field-notes/social-sciences.md',
        queue='scratchpad/soc/wave2/queue_2.json',
        results='scratchpad/soc/wave2/results_2.json',
        status='scratchpad/soc/wave2/STATUS_2.json',
        n_rows=30,
        extra_traps='- Acronym collisions: ASA is sociology here.',
    )


def test_digest_carries_every_binding_rule():
    d = streamline.BINDING_DIGEST
    for phrase in (
        'exact-page clickable URL',
        'search snippet',
        'Invited speakers are NOT counted',
        'stated total NEVER beats a countable artefact',
        'Cap: 3 web searches per conference',
        'NEVER evidence a meeting is small',
        'NEEDS_RUNG_5',
        'NOT COUNTED',
        'credit the rung that PRODUCED',
        'rewritten in full after every single row',
        'authoritative',  # methodology remains the authority, consult on anything unusual
    ):
        assert phrase in d, phrase


def test_brief_wires_paths_and_field_notes():
    b = brief()
    assert 'scratchpad/soc/wave2/queue_2.json' in b
    assert 'scratchpad/soc/wave2/results_2.json' in b
    assert 'scratchpad/soc/wave2/STATUS_2.json' in b
    assert 'docs/business/field-notes/social-sciences.md' in b
    assert 'Social Sciences' in b
    assert '30 rows' in b
    assert 'ASA is sociology here' in b


def test_brief_is_slim_but_complete():
    b = brief()
    # slim: no full-methodology read order, no analogue-field notes
    assert 'IN FULL' not in b
    assert 'chemistry.md' not in b and 'engineering.md' not in b and 'life-sciences.md' not in b
    # complete: digest embedded, output contract, crawl budget, blind run
    assert streamline.BINDING_DIGEST in b
    assert 'verdict (VERIFIED|BORDERLINE|OUT|UNRESOLVED|NEEDS_RUNG_5)' in b
    assert 'NEEDS_BULK_COUNT' in b
    assert 'BLIND RUN' in b


def test_crawl_budget_rule_defers_not_drops():
    # the crawl rule must checkpoint a reproducible counting plan, never a guess
    assert 'exact counting plan' in streamline.CRAWL_RULE
    assert '40' in streamline.CRAWL_RULE
    assert 'NEEDS_BULK_COUNT' in streamline.CRAWL_RULE

"""Tests for wavelib.plan — turn researcher records into workbook writes, rung-9 calls and moves."""
import wavelib

TAG = '[eng wave 1, 2026-09-14]'


def rec(**kw):
    base = dict(row=70, conference='Conf', outcome='COUNTED', abstracts_numeric=2400, abstracts='2,400 papers',
                year=2024, rung=4, source_url='https://x/y', spot_checks=[], searches_used=1, events_per_yr=1,
                cadence_evidence='annual per site', attendance_numeric=None, attendance_year=None,
                attendance_basis=None, attendance_rung=None, attendance_source_url=None, alt_figures=[],
                character='CONTRIBUTED', character_evidence='open call', programme_type='CONTRIBUTED',
                programme_evidence='', direct_abstracts=None, ratio=None, ratio_rationale=None,
                duplicate_of=None, method='counted volumes', verdict='VERIFIED', confidence='exact')
    base.update(kw)
    return base


def test_counted_verified_row_becomes_a_figure_write_and_no_move():
    out = wavelib.plan([rec()], tag=TAG)
    assert out['problems'] == [] and out['moves'] == [] and out['calls'] == []
    w = out['wb_recs'][0]
    assert (w['row'], w['expected_name'], w['abstracts'], w['year'], w['rung'], w['tier']) == (70, 'Conf', '2,400 papers', 2024, 4, 'VERIFIED')
    assert w['events_per_yr'] == 1 and TAG in w['method'] and 'VERDICT VERIFIED' in w['method']


def test_counted_out_row_moves_to_deleted_with_the_evidence():
    out = wavelib.plan([rec(abstracts_numeric=500, abstracts='500 papers', verdict='OUT')], tag=TAG)
    assert out['wb_recs'][0]['tier'] == 'OUT'
    assert out['moves'] == [dict(row=70, expected_name='Conf', why=f'OUT on positive evidence: 500 papers — see Method {TAG}')]


def test_unresolved_and_needs_rung5_stay_borderline_with_no_figure():
    recs = [rec(row=70, outcome='UNKNOWN', abstracts_numeric=None, abstracts=None, rung=None, source_url=None, verdict='UNRESOLVED'),
            rec(row=71, conference='B', outcome='NEEDS_RUNG_5', abstracts_numeric=None, abstracts=None, rung=None, source_url=None, verdict='NEEDS_RUNG_5')]
    out = wavelib.plan(recs, tag=TAG)
    assert [w['tier'] for w in out['wb_recs']] == ['BORDERLINE', 'BORDERLINE']
    assert all(w['abstracts'] is None for w in out['wb_recs']) and out['moves'] == []


def test_rung9_row_is_resolved_by_attlib_and_below_bar_moves():
    r9 = rec(outcome='INFERRED', abstracts_numeric=None, abstracts=None, rung=9, source_url=None,
             attendance_numeric=1000, attendance_year=2024, attendance_basis='DELEGATES', attendance_rung='A2',
             attendance_source_url='https://x/att', ratio=0.3, ratio_rationale='mostly practitioners, small poster hall',
             verdict='BORDERLINE')
    out = wavelib.plan([r9], tag=TAG)
    assert out['problems'] == []
    call = out['calls'][0]
    assert call['implied'] == 300 and call['decision'] == 'BELOW BAR' and call['bar'] == 900
    assert out['wb_recs'][0]['tier'] == 'OUT' and out['moves'][0]['row'] == 70


def test_rung9_row_near_the_bar_is_included_as_borderline():
    r9 = rec(outcome='INFERRED', abstracts_numeric=None, abstracts=None, rung=9, source_url=None,
             attendance_numeric=2000, attendance_basis='DELEGATES', attendance_rung='A2',
             attendance_source_url='https://x/att', ratio=0.45, ratio_rationale='society meeting where most attendees present',
             verdict='BORDERLINE')
    out = wavelib.plan([r9], tag=TAG)
    assert out['calls'][0]['decision'] == 'INCLUDE' and out['wb_recs'][0]['tier'] == 'BORDERLINE' and out['moves'] == []


def test_problems_are_reported_for_missing_source_events_and_bad_ratio():
    recs = [rec(row=70, source_url=None),
            rec(row=71, conference='B', events_per_yr=None),
            rec(row=72, conference='C', outcome='INFERRED', abstracts_numeric=None, abstracts=None, rung=9, source_url=None,
                attendance_numeric=1000, attendance_rung='A2', attendance_source_url='https://x', ratio=0.3, ratio_rationale='', verdict='BORDERLINE')]
    out = wavelib.plan(recs, tag=TAG)
    assert [p[0] for p in out['problems']] == [70, 71, 72]


def test_orchestrator_rung5_count_overrides_the_researcher_and_dupes_move_with_reason():
    r5 = {70: dict(abstracts_numeric=1700, abstracts='1,700 papers', year=2025, rung=5, source_url='https://x/r5',
                   confidence='exact', orchestrator_note='counted in Playwright', tier='VERIFIED')}
    recs = [rec(outcome='NEEDS_RUNG_5', abstracts_numeric=None, abstracts=None, rung=None, source_url=None, verdict='NEEDS_RUNG_5'),
            rec(row=71, conference='B')]
    out = wavelib.plan(recs, tag=TAG, r5=r5, dupes={71: 'DUPLICATE of row X'})
    a, b = out['wb_recs']
    assert (a['abstracts'], a['tier'], a['rung']) == ('1,700 papers', 'VERIFIED', 5) and 'counted in Playwright' in a['method']
    assert out['moves'] == [dict(row=71, expected_name='B', why='DUPLICATE of row X')]


def test_rung9_row_with_a_stated_figure_needs_no_ratio_and_resolves_on_the_figure():
    r9 = rec(outcome='INFERRED', abstracts_numeric=None, abstracts='~425+ REPORTED BY SOURCE, NOT COUNTED', rung=8,
             source_url='https://x/report', attendance_numeric=20000, attendance_rung='A3', attendance_source_url='https://x/att',
             direct_abstracts=425, ratio=None, ratio_rationale=None, verdict='OUT')
    out = wavelib.plan([r9], tag=TAG)
    assert out['problems'] == []
    assert out['calls'][0]['decision'] == 'BELOW BAR' and out['calls'][0]['figure'] == 425
    assert out['wb_recs'][0]['tier'] == 'OUT' and out['moves'][0]['row'] == 70

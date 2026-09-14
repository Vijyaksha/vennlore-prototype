"""Failing-first tests for the attendance writeback."""
import re
import openpyxl, pytest, attlib

@pytest.fixture
def sheet(tmp_path):
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'Census - Medicine & Health'
    hdr = ['Field','Umbrella','Society','Country','Conference','Events/yr','Abstracts','Abstr. yr',
           'Abstracts source','Attendance','Attendance source','Venue','Agent verdict','Tier',
           'Include','SOM','US','Rev','Notes','Method','Phase-2 priority']
    for i,h in enumerate(hdr,1): ws.cell(4,i).value = h
    ws.cell(5,5).value='ASH Annual Meeting'; ws.cell(5,7).value='7,964 abstracts'; ws.cell(5,14).value='VERIFIED'
    ws.cell(6,5).value='EuroPCR';            ws.cell(6,7).value='743 abstracts';   ws.cell(6,14).value='BORDERLINE'
    ws.cell(7,5).value='Some Congress';      ws.cell(7,7).value='UNKNOWN';         ws.cell(7,14).value='BORDERLINE'
    p = tmp_path/'wb.xlsx'; wb.save(p); return str(p)

def _rec(**kw):
    base = dict(row=5, conference='ASH Annual Meeting', attendance='30,000 attendees',
                attendance_numeric=30000, attendance_year='2024', attendance_basis='TOTAL_ONSITE',
                attendance_rung='A2', attendance_rung_name='post-meeting report',
                attendance_source_url='https://ash.org/report', attendance_method='Opened the report.',
                alt_figures=[], character='CONTRIBUTED', character_evidence='https://ash.org/call',
                confidence='HIGH', searches_used=2)
    base.update(kw); return base

def test_adds_the_four_new_columns(sheet):
    attlib.apply([_rec()], path=sheet)
    ws = openpyxl.load_workbook(sheet)['Census - Medicine & Health']
    assert [ws.cell(4,c).value for c in range(22,26)] == [
        'Attendance basis','Attendance rung + how','Programme character',"Rupert's call"]

def test_writes_number_and_source_and_basis(sheet):
    attlib.apply([_rec()], path=sheet)
    ws = openpyxl.load_workbook(sheet)['Census - Medicine & Health']
    assert ws.cell(5,10).value == '30,000 attendees (2024)'
    assert ws.cell(5,11).value == 'https://ash.org/report'
    assert ws.cell(5,22).value == 'TOTAL_ONSITE'
    assert 'RUNG A2 PRODUCED THIS FIGURE' in ws.cell(5,23).value
    assert ws.cell(5,24).value == 'CONTRIBUTED'

def test_null_result_says_no_rung_yielded_and_does_not_invent_a_number(sheet):
    attlib.apply([_rec(attendance_numeric=None, attendance=None, attendance_rung=None,
                       attendance_source_url=None, attendance_method='A1-A4 all failed.')], path=sheet)
    ws = openpyxl.load_workbook(sheet)['Census - Medicine & Health']
    assert ws.cell(5,10).value == 'UNKNOWN'
    assert 'NO RUNG YIELDED' in ws.cell(5,23).value
    assert 'A2' not in ws.cell(5,23).value          # must not credit a rung that produced nothing

def test_disagreement_is_recorded_not_averaged(sheet):
    r = _rec(alt_figures=[{'value':15000,'year':'2024','basis':'UNSPECIFIED','rung':'A1','url':'https://x/pro'}])
    attlib.apply([r], path=sheet)
    ws = openpyxl.load_workbook(sheet)['Census - Medicine & Health']
    assert ws.cell(5,10).value.startswith('30,000')   # headline stays the accountable rung
    m = ws.cell(5,23).value
    assert 'DISAGREEMENT' in m and '15,000' in m and 'https://x/pro' in m

def test_never_touches_tier_or_abstracts(sheet):
    attlib.apply([_rec(row=7, conference='Some Congress')], path=sheet)
    ws = openpyxl.load_workbook(sheet)['Census - Medicine & Health']
    assert ws.cell(7,14).value == 'BORDERLINE' and ws.cell(7,7).value == 'UNKNOWN'

def test_remap_reanchors_by_conference_name(sheet):
    # agent recorded row 5 but the sheet has it at 6 -> must follow the name, not the number
    recs = [_rec(row=99, conference='EuroPCR')]
    out = attlib.remap(recs, path=sheet)
    assert out[0]['row'] == 6

def test_remap_drops_records_whose_conference_is_absent(sheet):
    out = attlib.remap([_rec(row=5, conference='Nonexistent Meeting')], path=sheet)
    assert out == []


def test_character_only_write_does_not_touch_attendance(sheet):
    ws0 = openpyxl.load_workbook(sheet)['Census - Medicine & Health']
    attlib.apply_character([{'row':5,'conference':'ASH Annual Meeting','character':'CONTRIBUTED',
                             'character_evidence':'7,964 counted abstracts'}], path=sheet)
    ws = openpyxl.load_workbook(sheet)['Census - Medicine & Health']
    assert ws.cell(5,24).value == 'CONTRIBUTED'
    assert ws.cell(5,10).value is None          # attendance untouched
    assert ws.cell(5,14).value == 'VERIFIED'    # tier untouched
    assert 'counted abstracts' in ws.cell(5,23).value

def test_counted_abstracts_imply_contributed(sheet):
    out = attlib.character_from_abstracts(path=sheet)
    byrow = {r['row']: r for r in out}
    assert byrow[5]['character'] == 'CONTRIBUTED'   # 7,964 abstracts
    assert byrow[6]['character'] == 'CONTRIBUTED'   # 743 abstracts
    assert 7 not in byrow                            # UNKNOWN abstracts -> needs research


# ---- abstracts : attendance conversion (Rupert's rule, 2026-09-12) -------------------

def test_parse_attendance_reads_the_headline_number():
    assert attlib.parse_attendance('20,522 participants from 131 countries') == 20522
    assert attlib.parse_attendance('~38,000') == 38000
    assert attlib.parse_attendance('More than 7,000 (2024)') == 7000
    assert attlib.parse_attendance('2190 in-person + 137 remote') == 2190

def test_parse_attendance_refuses_non_figures():
    assert attlib.parse_attendance('UNKNOWN') is None
    assert attlib.parse_attendance(None) is None
    assert attlib.parse_attendance('') is None

def test_parse_attendance_ignores_a_bare_year():
    # a year is not an attendance figure
    assert attlib.parse_attendance('(2024)') is None
    assert attlib.parse_attendance('record attendance in 2025') is None

def test_ratio_rows_pairs_counted_abstracts_with_attendance(sheet):
    ws = openpyxl.load_workbook(sheet)
    s = ws['Census - Medicine & Health']
    s.cell(5,10).value = '30,000 attendees'     # ASH: 7,964 abstracts
    s.cell(6,10).value = '12,177'               # EuroPCR: 743 abstracts
    s.cell(7,10).value = '5,000'                # abstracts UNKNOWN -> not a calibration row
    ws.save(sheet)
    out = {r['conference']: r for r in attlib.ratio_rows(path=sheet)}
    assert set(out) == {'ASH Annual Meeting', 'EuroPCR'}
    assert out['ASH Annual Meeting']['abstracts'] == 7964
    assert out['ASH Annual Meeting']['attendance'] == 30000
    assert round(out['EuroPCR']['ratio'], 4) == round(743/12177, 4)

def test_implied_abstracts_applies_a_ratio_without_inventing_precision():
    # 2,500 attendees at a 0.5 ratio -> ~1,250 implied abstracts
    assert attlib.implied_abstracts(2500, 0.5) == 1250
    assert attlib.implied_abstracts(None, 0.5) is None


# ---- the inclusion log (no new switches, no new files) -------------------------------

def _call(**kw):
    base = dict(row=6, conference='EuroPCR', decision='INCLUDE',
                attendance=12177, attendance_year='2025', attendance_basis='TOTAL_ONSITE',
                attendance_rung='A2', attendance_source_url='https://europcr.com/report',
                programme_type='majority-teaching', programme_evidence='live-case course',
                ratio=0.10, implied=1218, direct_abstracts=None, bar=1000)
    base.update(kw); return base

def test_log_append_keeps_the_existing_method_text(sheet):
    ws = openpyxl.load_workbook(sheet); ws['Census - Medicine & Health'].cell(6,20).value = 'RUNG 6 reached, no figure.'
    ws.save(sheet)
    attlib.log_inclusion([_call()], path=sheet)
    ws = openpyxl.load_workbook(sheet)['Census - Medicine & Health']
    t = ws.cell(6,20).value
    assert t.startswith('RUNG 6 reached, no figure.')      # prior method text survives
    assert 'RUNG 9' in t

def test_log_records_ratio_basis_bar_and_that_abstracts_were_not_counted(sheet):
    attlib.log_inclusion([_call()], path=sheet)
    t = openpyxl.load_workbook(sheet)['Census - Medicine & Health'].cell(6,20).value
    assert 'majority-teaching' in t and '10% of attendance' in t
    assert '1,000' in t                                     # Rupert's bar
    assert '12,177' in t and 'A2' in t                      # the attendance evidence and its rung
    assert 'NOT a counted abstract figure' in t

def test_log_writes_rupert_call_as_text_and_touches_no_switch(sheet):
    attlib.log_inclusion([_call()], path=sheet)
    ws = openpyxl.load_workbook(sheet)['Census - Medicine & Health']
    assert ws.cell(6,25).value.startswith('INCLUDE')
    assert ws.cell(6,15).value is None                      # Include (1/0) switch untouched
    assert ws.cell(6,14).value == 'BORDERLINE'              # Tier untouched
    assert ws.cell(6,7).value == '743 abstracts'            # abstracts untouched

def test_log_prefers_a_direct_abstract_figure_over_the_ratio(sheet):
    attlib.log_inclusion([_call(direct_abstracts=1900, programme_type='majority-abstract')], path=sheet)
    t = openpyxl.load_workbook(sheet)['Census - Medicine & Health'].cell(6,20).value
    assert '1,900' in t
    assert 'reported for this meeting' in t

def test_log_is_stamped_with_the_call_date_not_the_research_date(sheet):
    attlib.log_inclusion([_call()], path=sheet)
    ws = openpyxl.load_workbook(sheet)['Census - Medicine & Health']
    assert attlib.CALL_DATE in ws.cell(6,20).value and attlib.CALL_DATE in ws.cell(6,25).value
    assert attlib.CALL_DATE != attlib.TODAY          # the attendance pass ran on a different day

def test_inferred_abstracts_are_written_to_the_abstracts_column_clearly_labelled(sheet):
    # row 7 has no counted figure, so rung 9 may write there
    attlib.write_inferred_abstracts([_call(row=7, conference='Some Congress',
                                           implied=1218, direct_abstracts=None)], path=sheet)
    a = openpyxl.load_workbook(sheet)['Census - Medicine & Health'].cell(7,7).value
    assert a.startswith('~1,218 INFERRED FROM ATTENDANCE')
    assert 'NOT COUNTED' in a
    assert 'PRIOR: UNKNOWN' in a           # the prior cell text is preserved, not erased

def test_a_sub_one_percent_ratio_is_not_printed_as_zero(sheet):
    """0.5% must not render as '0% of attendance' — that reads as 'no abstracts at all'."""
    attlib.write_inferred_abstracts([_call(row=7, conference='Some Congress', ratio=0.005,
                                           attendance=7000, implied=35, direct_abstracts=None)], path=sheet)
    a = openpyxl.load_workbook(sheet)['Census - Medicine & Health'].cell(7,7).value
    assert '0.5% of attendance' in a and '0% of attendance' not in a

def test_relabelling_a_row_does_not_nest_the_old_label(sheet):
    """Rewriting a row after a re-audit must replace the old rung-9 label, not bury it in PRIOR."""
    c = _call(row=7, conference='Some Congress', ratio=0.02, attendance=7000, implied=140,
              direct_abstracts=None)
    attlib.write_inferred_abstracts([c], path=sheet)
    attlib.write_inferred_abstracts([dict(c, ratio=0.005, implied=35)], path=sheet)
    a = openpyxl.load_workbook(sheet)['Census - Medicine & Health'].cell(7,7).value
    assert a.upper().count('NOT COUNTED') == 1
    assert '~35' in a and '~140' not in a
    assert 'PRIOR: UNKNOWN' in a          # the ORIGINAL prior text is what survives
    # and a THIRD pass must still leave exactly one label, not peel one layer of many
    attlib.write_inferred_abstracts([dict(c, ratio=0.01, implied=70)], path=sheet)
    a = openpyxl.load_workbook(sheet)['Census - Medicine & Health'].cell(7,7).value
    assert a.upper().count('NOT COUNTED') == 1 and '~70' in a and 'PRIOR: UNKNOWN' in a

def test_a_reported_figure_is_labelled_reported_not_inferred(sheet):
    attlib.write_inferred_abstracts([_call(row=7, conference='Some Congress',
                                           direct_abstracts=1900)], path=sheet)
    a = openpyxl.load_workbook(sheet)['Census - Medicine & Health'].cell(7,7).value
    assert a.startswith('~1,900 REPORTED BY SOURCE, NOT COUNTED')

def test_an_inferred_figure_never_overwrites_a_real_counted_figure(sheet):
    # row 5 (ASH) carries a counted 7,964 — rung 9 must not touch it
    attlib.write_inferred_abstracts([_call(row=5, conference='ASH Annual Meeting')], path=sheet)
    assert openpyxl.load_workbook(sheet)['Census - Medicine & Health'].cell(5,7).value == '7,964 abstracts'

def test_inferred_figures_are_excluded_from_the_calibration(sheet):
    """Otherwise the ratio feeds on its own output and becomes self-fulfilling."""
    ws = openpyxl.load_workbook(sheet); s = ws['Census - Medicine & Health']
    s.cell(7,10).value = '12,177'
    ws.save(sheet)
    attlib.write_inferred_abstracts([_call(row=7, conference='Some Congress', implied=1218)], path=sheet)
    assert attlib._counted(openpyxl.load_workbook(sheet)['Census - Medicine & Health'].cell(7,7).value) is None
    assert [r['conference'] for r in attlib.ratio_rows(path=sheet)] == []

def test_a_ratio_must_be_judged_per_conference_with_a_reason():
    ok = attlib.check_ratio({'ratio': 0.35, 'ratio_rationale': 'poster-dominated programme; '
                             'comparable oncology congresses in this census run 0.21-0.27'})
    assert ok == []

def test_a_ratio_without_a_stated_reason_is_rejected():
    problems = attlib.check_ratio({'ratio': 0.35, 'ratio_rationale': ''})
    assert any('rationale' in p for p in problems)

def test_an_implausible_ratio_is_rejected():
    assert any('range' in p for p in attlib.check_ratio({'ratio': 4.0, 'ratio_rationale': 'x'*40}))
    assert any('range' in p for p in attlib.check_ratio({'ratio': 0.001, 'ratio_rationale': 'x'*40}))

def test_a_missing_ratio_is_rejected():
    assert any('no ratio' in p for p in attlib.check_ratio({'ratio': None, 'ratio_rationale': 'x'*40}))

def test_the_written_label_shows_the_judged_ratio_as_a_percentage(sheet):
    attlib.write_inferred_abstracts([_call(row=7, conference='Some Congress', ratio=0.35,
                                           implied=4262, direct_abstracts=None)], path=sheet)
    a = openpyxl.load_workbook(sheet)['Census - Medicine & Health'].cell(7,7).value
    assert '35% of attendance' in a
    assert 'judged for this conference' in a

def test_the_log_carries_the_reason_for_the_ratio(sheet):
    attlib.log_inclusion([_call(row=7, conference='Some Congress', ratio=0.35, implied=4262,
                                direct_abstracts=None,
                                ratio_rationale='poster-dominated; comparable congresses run 0.21-0.27')],
                         path=sheet)
    t = openpyxl.load_workbook(sheet)['Census - Medicine & Health'].cell(7,20).value
    assert 'poster-dominated' in t and '35%' in t

# ---- resolving borderline rows (Rupert's sensitivity rule, 2026-09-12) ----------------

def test_a_figure_within_100_of_the_bar_is_included():
    v = attlib.resolve_borderline({'implied': 920, 'ratio': 0.25, 'bar': 1000})
    assert v['decision'] == 'INCLUDE' and 'within 100' in v['why']

def test_a_figure_that_reaches_the_band_when_the_ratio_flexes_up_is_included():
    # 3,500 x 25% = 875; flexing the ratio +20% relative -> 30% -> 1,050, which clears 900
    v = attlib.resolve_borderline({'implied': 875, 'ratio': 0.25, 'attendance': 3500, 'bar': 1000})
    assert v['decision'] == 'INCLUDE'
    assert v['high'] == 1050 and v['low'] == 700

def test_a_figure_that_stays_short_even_when_flexed_is_excluded():
    # 2,331 x 30% = 699; +20% relative -> 36% -> 839, still under 900
    v = attlib.resolve_borderline({'implied': 699, 'ratio': 0.30, 'attendance': 2331, 'bar': 1000})
    assert v['decision'] == 'BELOW BAR' and v['high'] == 839

def test_the_flex_is_relative_so_a_tiny_ratio_is_not_blown_up():
    """A teaching meeting at 2% must not be rescued by adding percentage points to its ratio."""
    v = attlib.resolve_borderline({'implied': 600, 'ratio': 0.02, 'attendance': 30000, 'bar': 1000})
    assert v['decision'] == 'BELOW BAR'
    assert v['high'] == 720                      # 2.4%, not 7%

def test_a_reported_figure_is_not_flexed_by_a_ratio():
    """A number a source stated has no ratio behind it to vary."""
    v = attlib.resolve_borderline({'direct_abstracts': 800, 'ratio': 0.27, 'attendance': 3000, 'bar': 1000})
    assert v['decision'] == 'BELOW BAR'
    assert v['high'] == 800 and 'not flexed' in v['why']


# ---- the upgrade sweep: removed list -> approved list ---------------------------------

@pytest.fixture
def twosheets(tmp_path):
    """A census sheet with a totals block, and a deleted sheet, shaped like the real workbook."""
    wb = openpyxl.Workbook()
    c = wb.active; c.title = 'Census - Medicine & Health'
    d = wb.create_sheet('Deleted - Medicine & Health')
    for i, h in enumerate(['Field','Umbrella','Society','Country','Conference','Events/yr','Abstracts',
                           'Abstr. yr','Abstracts source','Attendance','Attendance source','Venue',
                           'Agent verdict','Tier','Include','SOM','US','Rev','Notes','Method'], 1):
        c.cell(4,i).value = h
    for i, h in enumerate(['Field','Umbrella','Society','Country','Conference','Events/yr','Abstracts',
                           'Abstr. yr','Abstracts source','Attendance','Attendance source','Venue',
                           'Agent verdict','Tier','Include','SOM','US','Rev','Notes','Deleted on',
                           'Why deleted','Method'], 1):
        d.cell(4,i).value = h
    c.cell(5,5).value='Kept Congress'; c.cell(5,6).value=1; c.cell(5,14).value='VERIFIED'; c.cell(5,17).value=1
    # totals block over rows 5..7, mirroring the real sheet's fixed ranges
    c.cell(9,5).value='VERIFIED events/yr';  c.cell(9,6).value='=SUMPRODUCT((N5:N7="VERIFIED")*(F5:F7))'
    c.cell(10,5).value='VER+BORD events/yr'; c.cell(10,6).value='=SUMPRODUCT(((N5:N7="VERIFIED")+(N5:N7="BORDERLINE"))*(F5:F7))'
    c.cell(11,5).value='count';              c.cell(11,6).value='=COUNTIF(N5:N7,"BORDERLINE")'
    d.cell(5,1).value='Medicine & health'; d.cell(5,5).value='Upgradeable Congress'; d.cell(5,6).value=1
    d.cell(5,7).value='UNKNOWN'; d.cell(5,14).value='OUT'; d.cell(5,17).value=1
    d.cell(5,20).value='2026-08-01'; d.cell(5,21).value='no abstract count found'
    d.cell(5,22).value='RUNG 6 reached, nothing published.'
    d.cell(6,5).value='Stays Deleted'; d.cell(6,14).value='OUT'
    p = tmp_path/'wb2.xlsx'; wb.save(p); return str(p)

def test_attendance_is_recorded_on_the_deleted_sheet_too(twosheets):
    """Rule 5: write the number even when the row stays deleted. The deleted sheet is a
    reversible parking place, so restoring a row must never mean re-running the research."""
    rec = {'conference': 'Upgradeable Congress', 'attendance': '19,084 attendees',
           'attendance_numeric': 19084, 'attendance_year': '2025', 'attendance_basis': 'TOTAL_ONSITE',
           'attendance_rung': 'A2', 'attendance_rung_name': 'post-show report',
           'attendance_source_url': 'https://x/postshow', 'attendance_method': 'Read the post-show PDF.',
           'alt_figures': [], 'character': 'CURATED', 'character_evidence': 'no call for abstracts',
           'confidence': 'HIGH', 'searches_used': 2}
    attlib.apply_deleted([rec], path=twosheets)
    d = openpyxl.load_workbook(twosheets)['Deleted - Medicine & Health']
    assert d.cell(5,10).value == '19,084 attendees (2025)'
    assert d.cell(5,11).value == 'https://x/postshow'
    m = d.cell(5,22).value
    assert 'RUNG A2 PRODUCED THIS FIGURE' in m
    assert 'RUNG 6 reached' in m              # the row's existing method text is kept
    assert d.cell(5,14).value == 'OUT'        # still deleted; rung 9 moved nothing

def _upg(**kw):
    base = dict(conference='Upgradeable Congress', attendance=6000, attendance_year='2025',
                attendance_basis='DELEGATES', attendance_rung='A2',
                attendance_source_url='https://x/report', ratio=0.30,
                ratio_rationale='poster-led congress; comparable counted rows run 25-37%',
                programme_type='majority-abstract', programme_evidence='open call is the spine of it',
                direct_abstracts=None, implied=1800, bar=1000, decision='UPGRADE')
    base.update(kw); return base

def test_upgrade_moves_the_row_onto_the_census_sheet(twosheets):
    attlib.upgrade_rows([_upg()], path=twosheets)
    wb = openpyxl.load_workbook(twosheets)
    c, d = wb['Census - Medicine & Health'], wb['Deleted - Medicine & Health']
    names = [c.cell(r,5).value for r in range(5,9)]
    assert 'Upgradeable Congress' in names
    assert 'Upgradeable Congress' not in [d.cell(r,5).value for r in range(5,d.max_row+1)]
    assert 'Stays Deleted' in [d.cell(r,5).value for r in range(5,d.max_row+1)]

def test_upgrade_keeps_the_row_inside_the_totals_ranges(twosheets):
    attlib.upgrade_rows([_upg()], path=twosheets)
    c = openpyxl.load_workbook(twosheets)['Census - Medicine & Health']
    formulas = [c.cell(r,6).value for r in range(5,15) if isinstance(c.cell(r,6).value, str)
                and str(c.cell(r,6).value).startswith('=')]
    row = next(r for r in range(5,9) if c.cell(r,5).value == 'Upgradeable Congress')
    for f in formulas:
        for end in re.findall(r'[A-Z]{1,2}5:[A-Z]{1,2}(\d+)', f):
            assert int(end) >= row, f'row {row} falls outside {f}'

def test_upgraded_row_is_borderline_never_verified(twosheets):
    attlib.upgrade_rows([_upg()], path=twosheets)
    c = openpyxl.load_workbook(twosheets)['Census - Medicine & Health']
    row = next(r for r in range(5,9) if c.cell(r,5).value == 'Upgradeable Congress')
    assert c.cell(row,14).value == 'BORDERLINE'      # never VERIFIED: nothing was counted

def test_upgrade_carries_the_history_and_the_reasoning(twosheets):
    attlib.upgrade_rows([_upg()], path=twosheets)
    c = openpyxl.load_workbook(twosheets)['Census - Medicine & Health']
    row = next(r for r in range(5,9) if c.cell(r,5).value == 'Upgradeable Congress')
    method = c.cell(row,20).value
    assert 'RUNG 6 reached' in method                       # prior method text survives the move
    assert 'no abstract count found' in method              # why it was deleted survives
    assert '2026-08-01' in method                           # when it was deleted survives
    assert 'UPGRADED FROM THE REMOVED LIST' in method
    assert 'poster-led congress' in method                  # the ratio reasoning
    assert attlib.NOT_COUNTED in c.cell(row,7).value        # labelled estimate in abstracts

def test_upgrade_refuses_a_row_under_the_bar(twosheets):
    done = attlib.upgrade_rows([_upg(implied=400)], path=twosheets)
    assert done == []
    d = openpyxl.load_workbook(twosheets)['Deleted - Medicine & Health']
    assert 'Upgradeable Congress' in [d.cell(r,5).value for r in range(5,d.max_row+1)]

def test_upgrade_refuses_a_row_whose_ratio_has_no_reasoning(twosheets):
    assert attlib.upgrade_rows([_upg(ratio_rationale='')], path=twosheets) == []

def test_log_can_record_a_borderline_row_without_including_it(sheet):
    attlib.log_inclusion([_call(decision='BORDERLINE')], path=sheet)
    ws = openpyxl.load_workbook(sheet)['Census - Medicine & Health']
    assert ws.cell(6,25).value.startswith('BORDERLINE')
    assert 'INCLUDE' not in ws.cell(6,25).value


# --- Rupert, 2026-09-12 (second change): the two tests use DIFFERENT thresholds ---
# Test 1 (within-100) passes at bar-100. Test 2 (ratio flex) must reach the bar itself.

def test_the_within_100_test_still_passes_at_one_hundred_below_the_bar():
    v = attlib.resolve_borderline({'implied': 820, 'ratio': 0.25, 'bar': 900})

    assert v['decision'] == 'INCLUDE'


def test_the_flex_test_must_reach_the_bar_itself_not_one_hundred_below_it():
    """12,000 attendees judged at 6% -> 720; flexed band tops out at 864, under 900."""
    v = attlib.resolve_borderline({'implied': 720, 'ratio': 0.06, 'attendance': 12000, 'bar': 900})

    assert v['high'] == 864
    assert v['decision'] == 'BELOW BAR'


def test_a_flexed_band_that_does_reach_the_bar_includes_the_row():
    """12,000 attendees judged at 7% -> 840; flexed band tops out at 1,008, over 900."""
    v = attlib.resolve_borderline({'implied': 840, 'ratio': 0.07, 'attendance': 12000, 'bar': 900})

    assert v['high'] == 1008
    assert v['decision'] == 'INCLUDE'


def test_the_default_bar_is_now_900():
    v = attlib.resolve_borderline({'implied': 810, 'ratio': 0.25})

    assert v['decision'] == 'INCLUDE'

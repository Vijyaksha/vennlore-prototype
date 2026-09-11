"""Failing-first tests for the attendance writeback."""
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

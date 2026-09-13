"""Failing-first tests for building a new field's census + deleted sheet pair."""
import openpyxl, pytest, chemlib


@pytest.fixture
def wb_path(tmp_path):
    """A workbook shaped like the real one: an existing field pair that must not be touched."""
    wb = openpyxl.Workbook()
    c = wb.active; c.title = 'Census - Medicine & Health'
    d = wb.create_sheet('Deleted - Medicine & Health')
    for i, h in enumerate(chemlib.CENSUS_COLS, 1): c.cell(4, i).value = h
    for i, h in enumerate(chemlib.DELETED_COLS, 1): d.cell(4, i).value = h
    c.cell(5, 5).value = 'ASH Annual Meeting'; c.cell(5, 14).value = 'VERIFIED'; c.cell(5, 6).value = 1
    p = tmp_path / 'wb.xlsx'; wb.save(p); return str(p)


NAMES = [
    {'conference': 'ACS Spring National Meeting', 'society': 'ACS', 'country_or_region': 'US',
     'subfield': 'general', 'frequency_note': 'twice yearly', 'source_url': 'https://acs.org'},
    {'conference': '全国电化学大会 (CCS National Electrochemistry Congress)', 'society': 'CCS',
     'country_or_region': 'China', 'subfield': 'electrochemistry', 'source_url': 'https://chemsoc.org.cn'},
    {'conference': 'Reunión GEE', 'society': 'RSEQ', 'country_or_region': 'Spain',
     'subfield': 'electrochemistry', 'implied': True, 'source_url': 'https://rseq.org/grupos'},
]
DUPES = [{'conference': 'SciX (FACSS)', 'counted_on': 'Census - Physical Sciences'}]


def test_creates_both_sheets_with_the_same_columns_as_the_existing_field(wb_path):
    chemlib.build_field(NAMES, [], 'Chemistry', path=wb_path)
    wb = openpyxl.load_workbook(wb_path)
    assert 'Census - Chemistry' in wb.sheetnames and 'Deleted - Chemistry' in wb.sheetnames
    c, d = wb['Census - Chemistry'], wb['Deleted - Chemistry']
    assert [c.cell(4, i).value for i in range(1, len(chemlib.CENSUS_COLS) + 1)] == chemlib.CENSUS_COLS
    assert [d.cell(4, i).value for i in range(1, len(chemlib.DELETED_COLS) + 1)] == chemlib.DELETED_COLS


def test_every_name_becomes_a_row_with_no_numbers_and_not_yet_censused(wb_path):
    chemlib.build_field(NAMES, [], 'Chemistry', path=wb_path)
    c = openpyxl.load_workbook(wb_path)['Census - Chemistry']
    names = [c.cell(r, 5).value for r in range(5, 5 + len(NAMES))]
    assert names == [n['conference'] for n in NAMES]
    for r in range(5, 5 + len(NAMES)):
        assert c.cell(r, 14).value == 'NOT YET CENSUSED'
        assert c.cell(r, 7).value is None      # abstracts empty
        assert c.cell(r, 10).value is None     # attendance empty


def test_totals_block_ranges_cover_every_data_row(wb_path):
    """Fixed ranges that stop short of the last row make rows count for nothing, silently."""
    import re
    chemlib.build_field(NAMES, [], 'Chemistry', path=wb_path)
    c = openpyxl.load_workbook(wb_path)['Census - Chemistry']
    last = 4 + len(NAMES)
    formulas = [c.cell(r, 6).value for r in range(last + 1, c.max_row + 1)
                if isinstance(c.cell(r, 6).value, str) and c.cell(r, 6).value.startswith('=')]
    assert formulas, 'no totals block was written'
    for f in formulas:
        for end in re.findall(r'[A-Z]{1,2}5:[A-Z]{1,2}(\d+)', f):
            assert int(end) >= last, f'range stops at {end}, before the last data row {last}: {f}'


def test_cross_field_duplicates_are_parked_on_the_deleted_sheet_with_a_reason(wb_path):
    """A meeting already counted in another field must not be counted again in this one."""
    chemlib.build_field(NAMES, DUPES, 'Chemistry', path=wb_path)
    wb = openpyxl.load_workbook(wb_path)
    c, d = wb['Census - Chemistry'], wb['Deleted - Chemistry']
    assert 'SciX (FACSS)' not in [c.cell(r, 5).value for r in range(5, c.max_row + 1)]
    row = next(r for r in range(5, d.max_row + 1) if d.cell(r, 5).value == 'SciX (FACSS)')
    assert 'Census - Physical Sciences' in d.cell(row, 21).value      # Why deleted
    assert 'double' in d.cell(row, 21).value.lower()


def test_implied_placeholders_are_flagged_so_phase_2_resolves_them(wb_path):
    chemlib.build_field(NAMES, [], 'Chemistry', path=wb_path)
    c = openpyxl.load_workbook(wb_path)['Census - Chemistry']
    row = next(r for r in range(5, c.max_row + 1) if c.cell(r, 5).value == 'Reunión GEE')
    assert 'IMPLIED' in str(c.cell(row, 19).value).upper()            # Notes
    other = next(r for r in range(5, c.max_row + 1) if c.cell(r, 5).value == 'ACS Spring National Meeting')
    assert 'IMPLIED' not in str(c.cell(other, 19).value or '').upper()


def test_the_existing_field_is_left_exactly_as_it_was(wb_path):
    before = openpyxl.load_workbook(wb_path)['Census - Medicine & Health']
    snapshot = [[before.cell(r, col).value for col in range(1, 26)] for r in range(1, 10)]
    chemlib.build_field(NAMES, DUPES, 'Chemistry', path=wb_path)
    after = openpyxl.load_workbook(wb_path)['Census - Medicine & Health']
    assert [[after.cell(r, col).value for col in range(1, 26)] for r in range(1, 10)] == snapshot


def test_building_twice_does_not_duplicate_rows(wb_path):
    chemlib.build_field(NAMES, [], 'Chemistry', path=wb_path)
    chemlib.build_field(NAMES, [], 'Chemistry', path=wb_path)
    c = openpyxl.load_workbook(wb_path)['Census - Chemistry']
    names = [c.cell(r, 5).value for r in range(5, c.max_row + 1) if c.cell(r, 14).value == 'NOT YET CENSUSED']
    assert len(names) == len(NAMES)

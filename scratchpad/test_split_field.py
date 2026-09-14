"""Tests for split_field.py — split one `Census/Deleted - <field>` pair into two by a row rule."""
import openpyxl
import chemlib
import split_field


def _wb(tmp_path):
    p = tmp_path / 'wb.xlsx'
    openpyxl.Workbook().save(p)
    names = [
        {'conference': 'NeurIPS', 'subfield': 'CS / AI', 'society': None, 'country_or_region': 'intl'},
        {'conference': 'ICASSP', 'subfield': 'engineering (IEEE society meeting)', 'society': None, 'country_or_region': 'intl'},
        {'conference': 'CogSci', 'subfield': 'CS / AI — BOUNDARY: cognitive science', 'society': None, 'country_or_region': 'intl'},
        {'conference': 'CCC', 'subfield': 'engineering — control (China)', 'society': None, 'country_or_region': 'CN'},
    ]
    dups = [{'conference': 'EMBC', 'counted_on': 'Census - Medicine & Health'}]
    chemlib.build_field(names, dups, 'CS & Engineering', path=p)
    wb = openpyxl.load_workbook(p)
    ws = wb['Census - CS & Engineering']
    ws['N5'].value, ws['F5'].value = 'VERIFIED', 1      # NeurIPS
    ws['N6'].value, ws['F6'].value = 'VERIFIED', 1      # ICASSP
    ws['N7'].value, ws['F7'].value = 'BORDERLINE', 1    # CogSci
    ws['N8'].value, ws['F8'].value = 'BORDERLINE', 1    # CCC
    wd = wb['Deleted - CS & Engineering']
    wd['B6'].value, wd['E6'].value, wd['N6'].value = 'CS / AI', 'WWW', 'OUT'
    wb.save(p)
    return p


def _is_cs(umbrella):
    return str(umbrella or '').startswith('CS')


def test_split_partitions_census_and_deleted_rows_and_removes_the_source_pair(tmp_path):
    p = _wb(tmp_path)
    out = split_field.split_field(p, 'CS & Engineering', _is_cs, 'CS & AI', 'Engineering')
    wb = openpyxl.load_workbook(p)
    assert 'Census - CS & Engineering' not in wb.sheetnames and 'Deleted - CS & Engineering' not in wb.sheetnames

    def rows(sn):
        return [(r[0], r[4]) for r in wb[sn].iter_rows(min_row=5, max_row=8, values_only=True) if r[4]]
    assert rows('Census - CS & AI') == [('CS & AI', 'NeurIPS'), ('CS & AI', 'CogSci')]
    assert rows('Census - Engineering') == [('Engineering', 'ICASSP'), ('Engineering', 'CCC')]
    assert rows('Deleted - CS & AI') == [('CS & AI', 'WWW')]
    assert rows('Deleted - Engineering') == [('Engineering', 'EMBC')]
    assert out == {'CS & AI': {'census': 2, 'deleted': 1}, 'Engineering': {'census': 2, 'deleted': 1}}


def test_split_keeps_rows_in_place_so_totals_formulas_still_cover_them(tmp_path):
    p = _wb(tmp_path)
    src = openpyxl.load_workbook(p)['Census - CS & Engineering']
    formulas = {c.coordinate: c.value for row in src.iter_rows() for c in row
                if isinstance(c.value, str) and c.value.startswith('=')}
    split_field.split_field(p, 'CS & Engineering', _is_cs, 'CS & AI', 'Engineering')
    wb = openpyxl.load_workbook(p)
    for sn in ('Census - CS & AI', 'Census - Engineering'):
        ws = wb[sn]
        assert {k: ws[k].value for k in formulas} == formulas          # same formulas, same cells
        assert ws['E5'].value in ('NeurIPS', None) and ws['E6'].value in ('ICASSP', None)   # rows not shifted
        assert ws['A1'].value.startswith(sn.split(' - ')[1])


def test_split_refuses_a_rule_that_sends_every_row_one_way(tmp_path):
    p = _wb(tmp_path)
    try:
        split_field.split_field(p, 'CS & Engineering', lambda u: True, 'CS & AI', 'Engineering')
    except ValueError as e:
        assert 'Engineering' in str(e)
    else:
        raise AssertionError('expected ValueError')
    assert 'Census - CS & Engineering' in openpyxl.load_workbook(p).sheetnames   # untouched

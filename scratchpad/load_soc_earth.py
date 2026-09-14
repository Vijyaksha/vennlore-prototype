"""One-shot load, 2026-09-14: build Social Sciences and Earth Sciences sheet pairs from the
phase-1 names, move APA/APS from Life Sciences to Social Sciences (Rupert's call), verify
totals independently from cells before and after. Glue over tested chemlib/fieldload."""
import json
import re

import openpyxl

import chemlib
import fieldload

WB = chemlib.WB
TODAY = '2026-09-14'
APA_ROW, APS_ROW = 91, 92  # Census - Life Sciences


def counted_totals(wb, sheet):
    """Recompute VERIFIED and VERIFIED+BORDERLINE events/yr straight from cells."""
    ws = wb[sheet]
    v = vb = 0.0
    for r in range(5, ws.max_row + 1):
        tier, ev = ws.cell(r, 14).value, ws.cell(r, 6).value
        try:
            ev = float(str(ev).replace(',', '')) if ev is not None else 0.0
        except ValueError:
            continue
        if tier == 'VERIFIED':
            v += ev
            vb += ev
        elif tier == 'BORDERLINE':
            vb += ev
    return round(v, 2), round(vb, 2)


def norm(name):
    s = re.sub(r'\([^)]*\)', ' ', str(name).lower())
    for w in ('annual', 'meeting', 'conference', 'congress', 'symposium', 'international', 'national', 'the'):
        s = re.sub(rf'\b{w}\b', ' ', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


wb = openpyxl.load_workbook(WB)
census_sheets = [s for s in wb.sheetnames if s.startswith('Census - ')]
before = {s: counted_totals(wb, s) for s in census_sheets}
print('BEFORE:', json.dumps(before, indent=1))

# existing names across every sheet, for the collision check
existing = {}
for s in wb.sheetnames:
    if s.startswith(('Census - ', 'Deleted - ')):
        ws = wb[s]
        for r in range(5, ws.max_row + 1):
            v = ws.cell(r, 5).value
            if v and not str(v).startswith(('VERIFIED', 'Conferences', 'Candidates', 'CENSUS')):
                existing.setdefault(norm(v), []).append(f'{s}!r{r}')

soc = json.load(open('soc/p1/names.json'))
earth = json.load(open('earth/p1/names.json'))
assert len(soc) == 200 and len(earth) == 127, (len(soc), len(earth))

# Same meeting already counted on another field's census (checked by society, 2026-09-14):
# SIOP / ESA / BPS / APA-Asia collisions are acronym lookalikes of DIFFERENT societies and stay.
SOC_DUPES = {
    'ASHA Convention': 'Census - Medicine & Health (row 234 — same American Speech-Language-Hearing Association convention)',
    'TRB Annual Meeting': 'Census - Engineering (row 79 — same Transportation Research Board annual meeting)',
    'ECSS Annual Congress': 'Census - Medicine & Health (row 157 — same European College of Sport Science congress)',
}
soc_census = [n for n in soc if n['conference'] not in SOC_DUPES]
soc_parked = [{'conference': c, 'counted_on': on} for c, on in SOC_DUPES.items()]
assert len(soc_census) == 197 and len(soc_parked) == 3

for label, names in (('Social', soc), ('Earth', earth)):
    hits = [(n['conference'], existing[norm(n['conference'])]) for n in names if norm(n['conference']) in existing]
    print(f'{label}: {len(hits)} name collisions with existing sheets')
    for c, where in hits:
        print('   COLLISION:', c, '->', where)

r1 = chemlib.build_field(fieldload.to_build_records(soc_census), soc_parked, 'Social Sciences', today=TODAY)
r2 = chemlib.build_field(fieldload.to_build_records(earth), [], 'Earth Sciences', today=TODAY)
print('built:', r1, r2)
assert r1 == {'census_rows': 197, 'deleted_rows': 3} and r2 == {'census_rows': 127, 'deleted_rows': 0}

# reload (build_field saved) and move APA/APS across
wb = openpyxl.load_workbook(WB)
life = wb['Census - Life Sciences']
assert 'APA Convention' in str(life.cell(APA_ROW, 5).value)
assert 'APS Annual Convention' in str(life.cell(APS_ROW, 5).value)
for src_row in (APA_ROW, APS_ROW):
    dst_row = fieldload.move_row(wb, 'Census - Life Sciences', src_row, 'Census - Social Sciences', 'Social Sciences')
    dst = wb['Census - Social Sciences']
    note = dst.cell(dst_row, 19).value
    dst.cell(dst_row, 19).value = (f'MOVED from Census - Life Sciences row {src_row} on {TODAY} '
                                   f'(psychology belongs here — Rupert). | {note or ""}')
    print(f'moved life r{src_row} -> social r{dst_row}: {dst.cell(dst_row, 5).value} [{dst.cell(dst_row, 14).value}]')
wb.save(WB)

wb = openpyxl.load_workbook(WB)
after = {s: counted_totals(wb, s) for s in wb.sheetnames if s.startswith('Census - ')}
print('AFTER:', json.dumps(after, indent=1))

# the move must be exactly neutral workbook-wide: life loses APA (V 1.0) + APS (B 1.0), social gains both
lv, lvb = before['Census - Life Sciences']
av, avb = after['Census - Life Sciences']
sv, svb = after['Census - Social Sciences']
assert (av, avb) == (round(lv - 1.0, 2), round(lvb - 2.0, 2)), ('life', before['Census - Life Sciences'], after['Census - Life Sciences'])
assert (sv, svb) == (1.0, 2.0), ('social', after['Census - Social Sciences'])
assert after['Census - Earth Sciences'] == (0.0, 0.0)
for s in census_sheets:
    if s != 'Census - Life Sciences':
        assert after[s] == before[s], (s, before[s], after[s])
print('TOTALS CHECK PASSED: move was neutral, all other sheets untouched')

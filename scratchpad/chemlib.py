"""Build a new field's census + deleted sheet pair, shaped like the existing ones.

Phase 1 ends by writing every candidate name into the sheet with Tier = NOT YET CENSUSED
and every number column empty: complete in names, empty in numbers, which is what makes
Phase 2 progress measurable.
"""
import openpyxl

WB = '/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/tam-sam-som-v3.xlsx'

CENSUS_COLS = ['Field', 'Umbrella', 'Society', 'Country', 'Conference', 'Events/yr',
               'Abstracts (exact, as published)', 'Abstr. yr', 'Abstracts source (click)',
               'Attendance', 'Attendance source (click)', 'Venue', 'Agent verdict', 'Tier',
               'Include (1/0)', 'SOM (1/0)', 'US (1/0)', 'Rev/yr @ $5k', 'Notes',
               'Method — which escalation-ladder rung produced the number, and exactly how',
               'Phase-2 priority', 'Attendance basis', 'Attendance rung + how',
               'Programme character', "Rupert's call"]

DELETED_COLS = CENSUS_COLS[:19] + ['Deleted on', 'Why deleted',
                                   'Method — which escalation-ladder rung produced the number, '
                                   'and exactly how']

HEADROOM = 400   # spare rows inside the totals ranges, so Phase 2 can add rows without re-widening


def _write_header(ws, cols, title):
    ws.cell(1, 1).value = title
    ws.cell(2, 1).value = ('Phase 1 complete: names only. Every number column is deliberately empty '
                           'until Phase 2 fills it.')
    for i, h in enumerate(cols, 1):
        ws.cell(4, i).value = h


def _totals_block(ws, first_row, last_row):
    """Totals carry FIXED ranges and openpyxl re-points nothing, so give them headroom."""
    end = last_row + HEADROOM
    rows = [
        ('VERIFIED conferences >=1,500 abstracts — events/yr',
         f'=SUMPRODUCT((N5:N{end}="VERIFIED")*(F5:F{end}))'),
        ('VERIFIED + BORDERLINE (generous) — events/yr',
         f'=SUMPRODUCT(((N5:N{end}="VERIFIED")+(N5:N{end}="BORDERLINE"))*(F5:F{end}))'),
        ('Conferences VERIFIED (count)', f'=COUNTIF(N5:N{end},"VERIFIED")'),
        ('Conferences BORDERLINE (count)', f'=COUNTIF(N5:N{end},"BORDERLINE")'),
        ('Candidates NOT YET CENSUSED (count)', f'=COUNTIF(N5:N{end},"NOT YET CENSUSED")'),
        ('CENSUS PROGRESS (censused / total candidates)',
         f'=COUNTIF(N5:N{end},"VERIFIED")+COUNTIF(N5:N{end},"BORDERLINE")&" / "&COUNTA(E5:E{end})'),
    ]
    at = end + 2
    for i, (label, formula) in enumerate(rows):
        ws.cell(at + i, 5).value = label
        ws.cell(at + i, 6).value = formula


def build_field(names, duplicates, field, path=WB, today='2026-09-12'):
    """Create `Census - <field>` and `Deleted - <field>` and fill in the candidate names.

    `duplicates` are meetings already counted in ANOTHER field's census. They are parked on
    the deleted sheet with the reason, never listed on the census sheet — otherwise the same
    meeting is counted twice into SAM.
    Idempotent: rebuilding replaces the two sheets rather than appending to them.
    """
    wb = openpyxl.load_workbook(path)
    census, deleted = f'Census - {field}', f'Deleted - {field}'
    for name in (census, deleted):
        if name in wb.sheetnames:
            del wb[name]
    c = wb.create_sheet(census)
    d = wb.create_sheet(deleted)
    _write_header(c, CENSUS_COLS, f'{field} census — candidate names from Phase 1')
    _write_header(d, DELETED_COLS, f'{field} — removed list')

    row = 5
    for n in names:
        c.cell(row, 1).value = field
        c.cell(row, 2).value = n.get('subfield')
        c.cell(row, 3).value = n.get('society')
        c.cell(row, 4).value = n.get('country_or_region')
        c.cell(row, 5).value = n.get('conference')
        c.cell(row, 14).value = 'NOT YET CENSUSED'
        c.cell(row, 15).value = 0
        c.cell(row, 16).value = 0
        c.cell(row, 17).value = 0
        note = []
        if n.get('implied'):
            note.append('IMPLIED NAME — the society or group is confirmed but this meeting title '
                        'was never verified. Phase 2 must resolve it to a real name or drop the row.')
        if n.get('frequency_note'):
            note.append(str(n['frequency_note']))
        if n.get('why_listed'):
            note.append(str(n['why_listed']))
        if n.get('source_url'):
            note.append(f"Phase 1 source: {n['source_url']}")
        c.cell(row, 19).value = ' | '.join(note) if note else None
        row += 1
    _totals_block(c, 5, row - 1)

    drow = 5
    for dup in duplicates:
        d.cell(drow, 1).value = field
        d.cell(drow, 5).value = dup.get('conference')
        d.cell(drow, 14).value = 'OUT'
        d.cell(drow, 15).value = 0
        d.cell(drow, 20).value = today
        d.cell(drow, 21).value = (f"Already counted on {dup.get('counted_on')} — parked here so it is "
                                  f"not double counted into SAM. This is a bookkeeping exclusion, NOT "
                                  f"a judgement that the meeting is small.")
        drow += 1

    wb.save(path)
    return {'census_rows': row - 5, 'deleted_rows': drow - 5}

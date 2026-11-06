"""Phase-1 exclusion list: every conference name already known to the census.

existing_names(wb_path) -> [{sheet, society, conference, abstracts}]   every row on any
    `Census - *` / `Deleted - *` sheet (header on row 4), totals rows skipped.
crossref_titles(json_path, floor) -> [(container_title, n)]             Crossref proceedings
    container facets at or above `floor`, largest first.
"""
import json
import openpyxl

HEADER_ROW = 4


def existing_names(wb_path):
    wb = openpyxl.load_workbook(wb_path, read_only=True, data_only=True)
    out = []
    for sn in wb.sheetnames:
        if not (sn.startswith('Census -') or sn.startswith('Deleted -')):
            continue
        rows = wb[sn].iter_rows(min_row=HEADER_ROW, values_only=True)
        hdr = list(next(rows))
        c_soc, c_conf, c_abs = hdr.index('Society'), hdr.index('Conference'), hdr.index('Abstracts (exact, as published)')
        for r in rows:
            if not r or not r[c_conf]:
                continue
            if all(v is None for i, v in enumerate(r) if i not in (c_conf, c_conf + 1)):
                continue   # totals row: only Conference (and its figure) filled
            out.append({'sheet': sn, 'society': r[c_soc], 'conference': r[c_conf], 'abstracts': r[c_abs]})
    return out


def crossref_titles(json_path, floor):
    vals = json.load(open(json_path))['message']['facets']['container-title']['values']
    return sorted(((t, n) for t, n in vals.items() if n >= floor), key=lambda x: -x[1])

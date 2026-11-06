"""Independent recompute of chemistry Include x Events/yr across both sheets + tier counts."""
import openpyxl, collections, sys
def snap(path):
    wb = openpyxl.load_workbook(path, read_only=True)
    out = {}
    for sn in ["Census - Chemistry", "Deleted - Chemistry"]:
        rows = list(wb[sn].iter_rows(values_only=True))
        hi = next(i for i, r in enumerate(rows) if "Country" in r); h = rows[hi]
        C, T, I, E = h.index("Conference"), h.index("Tier"), h.index("Include (1/0)"), h.index("Events/yr")
        s = 0.0; tiers = collections.Counter(); n = 0
        for r in rows[hi + 1:]:
            if not r[C] or not r[T]: continue
            n += 1; tiers[r[T]] += 1
            try: s += float(r[I] or 0) * float(r[E] or 0)
            except (TypeError, ValueError): pass
        out[sn] = dict(rows=n, include_x_events=round(s, 3), tiers=dict(tiers))
    return out
if __name__ == "__main__":
    import json; print(json.dumps(snap(sys.argv[1]), indent=1))

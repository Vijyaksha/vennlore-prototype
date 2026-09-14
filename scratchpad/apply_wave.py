"""Writeback for one phase-2 wave: glue over the tested writers (writeback, attlib, dedupe, wavelib).

Usage:
  python3 apply_wave.py --dir eng/wave1 --sheet "Census - Engineering" --deleted "Deleted - Engineering" \
      --tag "[eng wave 1, 2026-09-14]" --today 2026-09-14 --results results_1.json --queue queue_1.json --dry
  (drop --dry to write; several --results/--queue pairs may be given, in order)

Optional files in --dir, each a JSON object keyed by queue-time row number:
  r5_notes.json        orchestrator rung-5 results / tier overrides (see wavelib.plan)
  dupes.json           {row: why}  rows to park on the deleted sheet as duplicates
  events_override.json {row: events_per_yr}
Writes write_plan.json to --dir on every run (dry or not).
"""
import argparse, collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attlib, writeback, dedupe, wavelib

ap = argparse.ArgumentParser()
ap.add_argument('--dir', required=True); ap.add_argument('--sheet', required=True); ap.add_argument('--deleted', required=True)
ap.add_argument('--tag', required=True); ap.add_argument('--today', required=True)
ap.add_argument('--results', action='append', required=True); ap.add_argument('--queue', action='append', required=True)
ap.add_argument('--dry', action='store_true')
a = ap.parse_args()
D = a.dir if os.path.isabs(a.dir) else os.path.join(os.path.dirname(os.path.abspath(__file__)), a.dir)

attlib.SHEET = a.sheet
attlib.CALL_DATE = attlib.TODAY = a.today
attlib.RATIO_NOTE = (f'{a.tag} — ratio judged per conference by the researcher from the programme\'s own wording '
                     f'(see the rationale above); no default or borrowed ratio')


def opt(name):
    p = os.path.join(D, name)
    return {int(k): v for k, v in json.load(open(p)).items()} if os.path.exists(p) else {}


recs = [x for f in a.results for x in json.load(open(os.path.join(D, f)))]
queued = {x['conference'] for f in a.queue for x in json.load(open(os.path.join(D, f)))}
got = {r['conference'] for r in recs}
missing = queued - got
if missing:
    print(f'WARNING {len(missing)} queued rows have no record (left NOT YET CENSUSED): {sorted(missing)}')
assert len(recs) == len(got), 'duplicate records for one conference'
extra = got - queued
assert not extra, f'records for conferences not in the queue: {sorted(extra)}'

qrow = {r['conference']: r['row'] for r in recs}
mapped = attlib.remap(recs)
assert len(mapped) == len(recs), 'a conference name no longer matches the sheet'
for r in mapped:
    r['_row_q'] = qrow[r['conference']]

out = wavelib.plan(mapped, tag=a.tag, r5=opt('r5_notes.json'), dupes=opt('dupes.json'), events_override=opt('events_override.json'))
json.dump(out['plan'], open(os.path.join(D, 'write_plan.json'), 'w'), ensure_ascii=False, indent=1)
print(len(out['wb_recs']), 'rows;', len(out['calls']), 'rung-9 calls;', len(out['moves']), 'moves;',
      dict(collections.Counter(p['tier'] for p in out['plan'])))
if out['problems']:
    print('PROBLEMS — fix before writing:')
    for p in out['problems']:
        print('  ', p)
if a.dry or out['problems']:
    sys.exit(1 if out['problems'] else 0)

writeback.apply(out['wb_recs'], sheet=a.sheet)
attlib.apply(mapped)
attlib.write_inferred_abstracts(out['calls'])
attlib.log_inclusion(out['calls'])
if out['moves']:
    dedupe.move_to_deleted(out['moves'], today=a.today, census=a.sheet, deleted=a.deleted)
print('written', len(out['wb_recs']), 'rung9', len(out['calls']), 'moved', len(out['moves']))

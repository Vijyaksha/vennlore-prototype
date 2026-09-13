import json, glob, collections, statistics, re, sys, openpyxl
S='/private/tmp/claude-501/-Users-rupertlim-AI-Projects-ConferenceApp/31c1fe24-6901-4471-99b6-f7dd532d498d/scratchpad/att'
recs=[]
for f in sorted(glob.glob(S+'/out*.json')):
    try: recs += json.load(open(f))
    except Exception as e: print('skip',f,e)
print('records', len(recs))
got=[r for r in recs if r.get('attendance_numeric') is not None]
print('with a number', len(got), f'({100*len(got)//max(1,len(recs))}%)')
print('rung mix   ', dict(collections.Counter(r.get('attendance_rung') for r in got)))
print('basis mix  ', dict(collections.Counter(r.get('attendance_basis') for r in got)))
print('character  ', dict(collections.Counter(r.get('character') for r in recs)))
print('confidence ', dict(collections.Counter(r.get('confidence') for r in got)))
print('searches   ', sum(r.get('searches_used',0) or 0 for r in recs))
dis=[r for r in recs if r.get('alt_figures')]
print('rows with disagreement', len(dis))
# spread
sp=[]
for r in dis:
    vs=[r['attendance_numeric']]+[a['value'] for a in r['alt_figures'] if isinstance(a.get('value'),(int,float))]
    vs=[v for v in vs if v]
    if len(vs)>1 and min(vs)>0: sp.append(max(vs)/min(vs))
if sp: print('  median spread factor %.2fx  max %.2fx'%(statistics.median(sp),max(sp)))
# ratio calibration against counted abstracts
wb=openpyxl.load_workbook('/Users/rupertlim/AI_Projects/ConferenceApp/docs/business/tam-sam-som-v3.xlsx')
C=wb['Census - Medicine & Health']
name2row={str(C.cell(r,5).value).strip():r for r in range(5,C.max_row+1) if C.cell(r,5).value}
def absnum(row):
    v=str(C.cell(row,7).value or '')
    m=re.search(r'([\d,]{3,})',v)
    return int(m.group(1).replace(',','')) if m and 'UNKNOWN' not in v.upper() else None
ratios=[]
for r in got:
    row=name2row.get(str(r.get('conference','')).strip())
    if not row: continue
    a=absnum(row)
    if a and r['attendance_numeric']: ratios.append((a/r['attendance_numeric'], r['conference'], a, r['attendance_numeric']))
ratios.sort()
print('\nabstracts:attendance ratio, n=%d'%len(ratios))
if ratios:
    vals=[x[0] for x in ratios]
    print('  median %.3f  p10 %.3f  p90 %.3f'%(statistics.median(vals), vals[len(vals)//10], vals[-max(1,len(vals)//10)]))
    print('  lowest (most curated):'); [print('   %.3f  %s  %s abs / %s att'%x) for x in ratios[:6]]
    print('  highest (most contributed):'); [print('   %.3f  %s  %s abs / %s att'%x) for x in ratios[-6:]]

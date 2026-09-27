"""Join brands with SmartScout hits (exact brand name first, then up to 2 variants). Writes phase3_work/match_table.csv and fit chunks."""
import pandas as pd, glob, json, sys
from build_ss_brand_batches import auto
N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
b = pd.concat([pd.read_csv(f, dtype=str).fillna('') for f in sorted(glob.glob('phase3_work/brands_out_*.csv'))], ignore_index=True)
d = pd.read_excel('phase2_domains_ALL.xlsx', sheet_name='All', dtype=str).fillna('')
ctx = d.drop_duplicates('Exhibitor Key').set_index('Exhibitor Key')
hits, queried = {}, set()
for f in glob.glob('phase3_work/ss_*.jsonl'):
    for l in open(f):
        r = json.loads(l); queried |= {q.lower() for q in r['queried']}
        for x in r['rows']: hits[x['SmartScout Brand'].lower()] = x
rows = []
for i, r in b.iterrows():
    o = {'Row ID': i, 'Exhibitor Key': r['Exhibitor Key'], 'Brand': r['Brand'], 'Brand Source': r['Brand Source'], 'Search Variants': r['Search Variants'], 'Brand Notes': r['Notes']}
    if r['Brand']:
        h, on = hits.get(r['Brand'].lower()), 'brand name'
        tried = [r['Brand']]
        if not h:
            vs = [v.strip() for v in r['Search Variants'].split(';') if v.strip()] + auto(r['Brand'])
            vs = [v for v in dict.fromkeys(vs) if v.lower() != r['Brand'].lower()][:2]
            tried += vs
            for v in vs:
                if v.lower() in hits: h, on = hits[v.lower()], f'variant "{v}"'; break
        o['Names Tried'] = ' ; '.join(tried)
        o['All Tried Queried'] = all(t.lower() in queried for t in tried)
        if h: o.update({'SmartScout Brand': h['SmartScout Brand'], 'SmartScout Category': h['Primary Category'], 'SmartScout Subcategory': h['Primary Subcategory'],
                        'Total Products': h['Total Products'], 'Monthly Revenue': h['Total Monthly Revenue'], 'Matched On': on})
    rows.append(o)
m = pd.DataFrame(rows)
m.to_csv('phase3_work/match_table.csv', index=False)
hit = m[m['SmartScout Brand'].fillna('') != ''].copy()
k = ctx.reindex(hit['Exhibitor Key'])
hit['Exhibitor Name'] = k['Exhibitor Name'].values
hit['What the exhibitor sells'] = (k['Exhibitor Type'] + ' | ' + k['Categories'].str[:150] + ' | ' + k['Type Reason'] + ' | ' + k['About Summary'].str[:250]).values
cols = ['Row ID','Exhibitor Name','Brand','What the exhibitor sells','SmartScout Brand','SmartScout Category','SmartScout Subcategory','Total Products','Monthly Revenue','Matched On']
for j in range(N): hit[cols].iloc[j::N].to_csv(f'phase3_work/fit_chunk_{j+1}.csv', index=False)
print('brand rows', (m['Brand']!='').sum(), '| with SmartScout hit', len(hit), '| exact', (hit['Matched On']=='brand name').sum(), '| variant', (hit['Matched On']!='brand name').sum(),
      '| not all names queried yet', ((m['Brand']!='') & (m['All Tried Queried']==False)).sum())

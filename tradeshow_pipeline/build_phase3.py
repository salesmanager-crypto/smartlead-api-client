import pandas as pd, glob, json, os, re
from common import norm_name
nz = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower().replace('&', 'and'))
m = pd.read_csv('phase3_work/match_table.csv', dtype=str).fillna('')
fit = pd.concat([pd.read_csv(f, dtype=str).fillna('') for f in glob.glob('phase3_work/fit_out_*.csv')]).drop_duplicates('Row ID', keep='last').set_index('Row ID')
amz = {}
if os.path.exists('phase3_work/amz_results.jsonl'):
    for l in open('phase3_work/amz_results.jsonl'):
        r = json.loads(l); amz[r['Brand'].lower()] = r
d = pd.read_excel('phase2_domains_ALL.xlsx', sheet_name='All', dtype=str).fillna('')
ex = d[d['Phase 3 Scope'] == 'Research']
def sold_by(merchant, brand):
    t = (merchant or '').lower()
    if not t: return 'Unknown'
    if 'amazon.com' in t and 'sold by amazon' in t: return 'Amazon'
    mm = re.search(r'sold by\s+(.+?)(?:\s+and\s+fulfilled|$)', t)
    seller = mm.group(1) if mm else t
    return 'Brand' if nz(brand)[:6] and nz(brand)[:6] in nz(seller) else 'Third-party reseller'
out, requeue = [], set()
for _, r in m.iterrows():
    o = {'Exhibitor Key': r['Exhibitor Key'], 'Brand': r['Brand'], 'Brand Source': r['Brand Source'], 'Notes': [r['Brand Notes']] if r['Brand Notes'] else []}
    if not r['Brand']:
        o.update({'On Amazon': 'No', 'Amazon Check Method': 'not checked (no owned brand)'}); out.append(o); continue
    ss_ok = False
    if r['SmartScout Brand']:
        f = fit.loc[r['Row ID']] if r['Row ID'] in fit.index else None
        good = f is not None and f['Fit'] == 'fits'
        o.update({'SmartScout Brand': r['SmartScout Brand'], 'SmartScout Category': r['SmartScout Category'], 'SmartScout Subcategory': r['SmartScout Subcategory'],
                  'SmartScout Products': float(r['Total Products'] or 0), 'SmartScout Monthly Revenue (phase 3 snapshot)': float(r['Monthly Revenue'] or 0),
                  'SmartScout Match': ('exact' if r['Matched On'] == 'brand name' else 'close') if good else 'wrong match',
                  'SmartScout Match Note': (r['Matched On'] + '; ' + (f['Fit Reason'] if f is not None else 'fit not checked'))})
        ss_ok = good and float(r['Total Products'] or 0) > 0
        if good and not ss_ok: o['Notes'].append('In SmartScout but 0 active products')
    else:
        o['SmartScout Match'] = 'not found'; o['SmartScout Match Note'] = 'names tried: ' + r['Names Tried']
    a = amz.get(r['Brand'].lower())
    if ss_ok:
        o['On Amazon'], o['Amazon Check Method'] = 'Yes', 'SmartScout'
    else:
        requeue.add(r['Brand'])
        if a and a.get('status') in ('hit', 'not found'):
            if a['status'] == 'hit':
                o['Amazon URL'] = a.get('Amazon URL', '')
                o['Amazon Confidence'] = 'confirmed' if a.get('byline_match') else 'possible'
                o['Amazon Sold By'] = sold_by(a.get('merchant'), r['Brand']) if a.get('byline_match') else 'Unknown'
                o['Amazon Evidence'] = ('byline: ' + a.get('byline', '') + ' | ' + a.get('breadcrumbs', '') + ' | ' + a.get('title', ''))[:300]
            else:
                o['Amazon Confidence'] = 'not found'
            o['Amazon Check Method'] = ('SmartScout (' + o['SmartScout Match'] + ') + amazon.com')
            if o.get('Amazon Confidence') == 'confirmed': o['On Amazon'] = 'Yes'
            elif o.get('Amazon Confidence') == 'possible' or o['SmartScout Match'] in ('exact', 'close'): o['On Amazon'] = 'Possible'
            else: o['On Amazon'] = 'No'
        else:
            o['Amazon Check Method'] = 'SmartScout (' + o['SmartScout Match'] + '); amazon.com pending'
            o['Amazon Confidence'] = 'Amazon check pending'
            o['Notes'].append('Amazon check pending: amazon.com blocked automated access from this environment')
            o['On Amazon'] = 'Possible' if o['SmartScout Match'] in ('exact', 'close') else 'No'
    out.append(o)
b = pd.DataFrame(out); b['Notes'] = b['Notes'].map(lambda n: '; '.join(dict.fromkeys(x for x in n if x)))
# amazon queue for future runs: everything not settled by SmartScout, in show order
first = d.groupby('Exhibitor Key')['Show ID'].min()
q = b[b['Brand'].isin(requeue)].assign(show=lambda x: x['Exhibitor Key'].map(first)).sort_values('show').drop_duplicates('Brand')
q[['Brand']].assign(Variants='').to_csv('phase3_work/amz_queue_full.csv', index=False)
# expand to show rows
exr = ex[['Show ID','Show Name','Exhibitor ID','Exhibitor Key','Exhibitor Name','Exhibitor Type','Domain','Parent Company']]
B = exr.merge(b, on='Exhibitor Key', how='left')
cols = ['Show ID','Show Name','Exhibitor ID','Exhibitor Key','Exhibitor Name','Exhibitor Type','Domain','Parent Company','Brand','Brand Source','On Amazon','Amazon Check Method',
        'SmartScout Brand','SmartScout Match','SmartScout Match Note','SmartScout Category','SmartScout Subcategory','SmartScout Products','SmartScout Monthly Revenue (phase 3 snapshot)',
        'Amazon URL','Amazon Sold By','Amazon Confidence','Amazon Evidence','Notes']
for c in cols:
    if c not in B: B[c] = ''
B = B[cols]
B.fillna({c: '' for c in cols if c not in ('SmartScout Products','SmartScout Monthly Revenue (phase 3 snapshot)')}, inplace=True)
B.drop_duplicates(['Exhibitor ID', 'Brand'], inplace=True)
B[['Exhibitor ID','Brand','On Amazon','SmartScout Match','Amazon Confidence']].to_csv('phase3_checkpoint.csv', index=False)
def roll(g):
    br = g[g['Brand'] != '']
    yes = br[br['On Amazon'] == 'Yes']; pos = br[br['On Amazon'] == 'Possible']
    return pd.Series({'Brands Found': len(br), 'Brands On Amazon': len(yes), 'Brands Possible': len(pos),
                      'Amazon Brand List': '; '.join(yes['Brand']), 'Possible Brand List': '; '.join(pos['Brand']),
                      'Any Brand On Amazon': 'Yes' if len(yes) else ('Possible' if len(pos) else 'No'),
                      'Amazon Checks Pending': (br['Amazon Confidence'] == 'Amazon check pending').sum()})
R = B.groupby(['Show ID','Show Name','Exhibitor ID','Exhibitor Key','Exhibitor Name','Exhibitor Type'], sort=False).apply(roll).reset_index()
with pd.ExcelWriter('phase3_brands_amazon_ALL.xlsx', engine='openpyxl') as w:
    B.to_excel(w, sheet_name='Brands', index=False); R.to_excel(w, sheet_name='Exhibitor Rollup', index=False)
S = []
for sid, g in B.groupby('Show ID'):
    br = g[g['Brand'] != '']; rr = R[R['Show ID'] == sid]
    S.append([sid, g['Exhibitor ID'].nunique(), br['Brand'].str.lower().nunique(), br.loc[br['On Amazon']=='Yes','Brand'].str.lower().nunique(),
              br.loc[br['On Amazon']=='Possible','Brand'].str.lower().nunique(), (rr['Any Brand On Amazon']=='Yes').sum(), (rr['Any Brand On Amazon']=='Possible').sum(),
              (br['Amazon Confidence']=='Amazon check pending').sum()])
S = pd.DataFrame(S, columns=['Show','Exhibitors researched','Brands found','Brands on Amazon (Yes)','Brands Possible','Exhibitors w/ Amazon brand','Exhibitors Possible only','Rows pending amazon.com'])
S.loc['All'] = ['All'] + [S[c].sum() for c in S.columns[1:]]
print(S.to_string(index=False)); print('amazon queue for later runs:', len(q))

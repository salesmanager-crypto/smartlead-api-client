import pandas as pd, glob, json, re, datetime
nz = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower().replace('&', 'and'))
prof, br = {}, {}
for f in glob.glob('phase4_work/profile_*.jsonl'):
    for l in open(f):
        r = json.loads(l)
        for x in r['rows']: prof[x['Brand Name'].lower()] = {**x, 'pulled_at': r['pulled_at']}
for f in glob.glob('phase4_work/brand_*.jsonl'):
    for l in open(f):
        r = json.loads(l); br[r['key'].lower()] = r
json.dump({'profiles': prof, 'sellers_subcats': br}, open('smartscout_cache.json', 'w'))
B = pd.read_excel('phase3_brands_amazon_ALL.xlsx', sheet_name='Brands').fillna('')
P = B[B['On Amazon'].isin(['Yes', 'Possible'])].copy()
def stype(seller, brand, exhibitor, parent):
    s = nz(seller)
    if not s: return ''
    if s in ('amazoncom', 'amazon'): return 'Amazon 1P'
    for n in (brand, exhibitor, parent):
        k = nz(re.sub(r'\b(inc|llc|co|corp|ltd|usa|us|home|brands?|group|company)\b', '', (n or '').lower()))
        if len(k) >= 4 and (k in s or s in k): return 'Brand direct'
    return 'Third-party reseller'
rows = []
for _, r in P.iterrows():
    o = r.to_dict(); notes = [r['Notes']] if r['Notes'] else []
    ssb = r['SmartScout Brand']
    if r['SmartScout Match'] not in ('exact', 'close') or not ssb:
        notes.append('Not in SmartScout'); o['Notes'] = '; '.join(notes); rows.append(o); continue
    p = prof.get(ssb.lower())
    if not p:
        notes.append('SmartScout profile not returned'); o['Notes'] = '; '.join(notes); rows.append(o); continue
    g = lambda k: p.get(k) if p.get(k) not in ('', None) else None
    o.update({'Monthly Revenue': g('Total Monthly Revenue'), 'Annual Revenue (TTM)': g('Trailing 12-Month Revenue'), 'Primary Category': p['Primary Category'],
              'Primary Subcategory': p['Primary Subcategory'], 'Total Products': g('Total Products'), 'Total Reviews': g('Total Reviews'), 'Average Rating': g('Average Rating'),
              'Average Price': g('Average Price'), 'Seller Count': g('Average Sellers'), 'Amazon 1P %': round(g('Average Amazon Revenue %') * 100, 1) if g('Average Amazon Revenue %') is not None else None,
              'MoM Growth': round(g('Average MoM Growth') * 100, 1) if isinstance(g('Average MoM Growth'), (int, float)) else None,
              'Has Storefront': 'Yes' if p.get('Has Storefront') in (True, 'true') else 'No', 'Data Pulled At': p['pulled_at']})
    notes.append('12-Month MoM Growth and Storefront URL not returned by SmartScout Business plan profile')
    b = br.get(ssb.lower())
    if b:
        s = sorted(b['sellers'], key=lambda x: -(x['Brand Revenue Estimate'] or 0))
        if s:
            d = s[0]
            o.update({'Dominant Seller': d['Seller Name'], 'Dominant Seller Sales %': d['Estimated Brand Share'],
                      'Dominant Seller Type': stype(d['Seller Name'], r['Brand'], r['Exhibitor Name'], r['Parent Company'])})
            types = [stype(x['Seller Name'], r['Brand'], r['Exhibitor Name'], r['Parent Company']) for x in s]
            o['Reseller Share %'] = round(sum((x['Estimated Brand Share'] or 0) for x, t in zip(s, types) if t == 'Third-party reseller'), 1)
            o['Top 5 Sellers'] = '; '.join(f"{x['Seller Name']} ({x['Estimated Brand Share']:.1f}%)" for x in s[:5])
            notes.append('Reseller Share % from top 5 sellers; Dominant Seller Type by name match')
        for i, sc in enumerate(sorted(b['subcats'], key=lambda x: -(x['Revenue'] or 0))[:3], 1):
            o[f'Top Subcategory {i}'] = sc['Subcategory']; o[f'Sub {i} Market Share'] = round((sc['Marketshare'] or 0) * 100, 2); o[f'Sub {i} Brand Rank'] = sc['Rank']
    elif (o['Monthly Revenue'] or 0) > 0:
        notes.append('Seller and subcategory pull missing')
    else:
        notes.append('No current monthly revenue; sellers and subcategories not pulled')
    o['Notes'] = '; '.join(dict.fromkeys(n for n in notes if n)); rows.append(o)
Q = pd.DataFrame(rows)
lead = ['Show ID','Show Name','Exhibitor ID','Exhibitor Name','Brand','On Amazon','Monthly Revenue','Annual Revenue (TTM)','Dominant Seller','Dominant Seller Sales %','Dominant Seller Type',
        'Top Subcategory 1','Sub 1 Market Share','Sub 1 Brand Rank','Top Subcategory 2','Sub 2 Market Share','Sub 2 Brand Rank','Top Subcategory 3','Sub 3 Market Share','Sub 3 Brand Rank',
        'Primary Category','Primary Subcategory','Total Products','Total Reviews','Average Rating','Average Price','Seller Count','Reseller Share %','Amazon 1P %','MoM Growth','12-Month MoM Growth',
        'Has Storefront','Storefront URL','Top 5 Sellers','Data Pulled At']
rest = ['Exhibitor Key','Exhibitor Type','Domain','Parent Company','Brand Source','Amazon Check Method','SmartScout Brand','SmartScout Match','SmartScout Match Note','Amazon URL','Amazon Sold By','Amazon Confidence','Notes']
for c in lead + rest:
    if c not in Q: Q[c] = None
Q = Q[lead + rest].sort_values(['Show ID', 'Monthly Revenue'], ascending=[True, False])
Q.to_csv('phase4_checkpoint.csv', index=False)
def roll(g):
    u = g.drop_duplicates('SmartScout Brand')
    tot = u['Monthly Revenue'].fillna(0).astype(float).sum()
    top = u.sort_values('Monthly Revenue', ascending=False).iloc[0] if len(u) else None
    return pd.Series({'Amazon Brands': len(g), 'Combined Monthly Revenue': round(tot, 2), 'Combined Annual Revenue (TTM)': round(u['Annual Revenue (TTM)'].fillna(0).astype(float).sum(), 2),
                      'Largest Brand': top['Brand'] if top is not None else '', 'Largest Brand Monthly Revenue': top['Monthly Revenue'] if top is not None else None,
                      'Brand List': '; '.join(g['Brand'])})
R = Q.groupby(['Show ID','Show Name','Exhibitor ID','Exhibitor Name','Exhibitor Type','Parent Company'], sort=False).apply(roll).reset_index().sort_values(['Show ID','Combined Monthly Revenue'], ascending=[True, False])
with pd.ExcelWriter('phase4_smartscout_ALL.xlsx', engine='openpyxl') as w:
    Q.to_excel(w, sheet_name='Brands', index=False); R.to_excel(w, sheet_name='Exhibitor Rollup', index=False)
for sid, g in Q.groupby('Show ID'):
    pulled = g['Data Pulled At'].notna().sum(); notin = g['Notes'].str.contains('Not in SmartScout|profile not returned', na=False).sum()
    r = R[R['Show ID'] == sid].head(10)
    print(f"\n{sid}: brands pulled {pulled}, not in SmartScout {notin}")
    for _, x in r.iterrows(): print(f"   {x['Exhibitor Name'][:40]:40s} ${x['Combined Monthly Revenue']:>13,.0f}/mo  largest: {x['Largest Brand']}")
print('\nTOTAL brands', len(Q), 'pulled', Q['Data Pulled At'].notna().sum())

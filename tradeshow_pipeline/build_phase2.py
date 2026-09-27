import pandas as pd, glob, json, os, hashlib
from common import domain_of
GENERIC = {'facebook.com','instagram.com','linktr.ee','etsy.com','linkedin.com','twitter.com','x.com','tiktok.com','youtube.com','amazon.com','ebay.com','whatnot.com','jewelry.org.hk','andmorehighpointmarket.com','pinterest.com','threads.net','gmail.com'}
TYPES = ['Brand / Manufacturer','Distributor / Wholesaler','Retailer / Reseller','Artist / Individual','Service / Software / Media / Association','Equipment / Supplier','Unclear']
RESEARCH = {'Brand / Manufacturer','Distributor / Wholesaler','Unclear'}
a = pd.read_excel('phase1_exhibitors_ALL.xlsx', sheet_name='All', dtype=str).fillna('')
rd = lambda pat: pd.concat([pd.read_csv(f, dtype=str).fillna('') for f in sorted(glob.glob(pat))]).drop_duplicates('Exhibitor Key', keep='last').set_index('Exhibitor Key') if glob.glob(pat) else pd.DataFrame()
srch, cls = rd('phase2_work/search_out_*.csv'), rd('phase2_work/classify_out_*.csv')
pending = set(pd.concat([pd.read_csv(f, dtype=str) for f in glob.glob('phase2_work/search_chunk_*.csv')])['Exhibitor Key']) - set(srch.index)
# best show-page domain per key
a['_d'] = a['Website'].map(domain_of)
showdom = a[a['_d'].ne('') & ~a['_d'].isin(GENERIC)].groupby('Exhibitor Key')['_d'].first()
art_keys = set(a.groupby('Exhibitor Key')['Categories'].apply(lambda s: s.str.contains('Artists Alley').all()).loc[lambda s: s].index)
out = []
for i, r in a.iterrows():
    k = r['Exhibitor Key']; notes = [r['Notes']] if r['Notes'] else []
    o = {}
    if r['Exhibitor Name'] == '':
        o = dict(Domain='', **{'Domain Confidence': 'not found', 'Exhibitor Type': '', 'Type Reason': '', 'Phase 3 Scope': 'Skip'}); out.append(o); continue
    if k in showdom.index: o['Domain'], o['Domain Confidence'] = showdom[k], 'from show page'
    elif k in srch.index and srch.loc[k, 'Domain']:
        o['Domain'], o['Domain Confidence'] = domain_of(srch.loc[k, 'Domain']), 'found by search'
    else:
        o['Domain'], o['Domain Confidence'] = '', 'not found'
        if k in art_keys: notes.append('Artist; domain not searched')
        elif k in pending: notes.append('Domain search pending (session web search cap reached)')
        elif k in srch.index and srch.loc[k, 'Notes']: notes.append(srch.loc[k, 'Notes'])
    if k in srch.index and srch.loc[k, 'Domain Evidence'] and o['Domain Confidence'] == 'found by search': o['Domain Evidence'] = srch.loc[k, 'Domain Evidence']
    if not r['LinkedIn'] and k in srch.index and srch.loc[k, 'Company LinkedIn']: o['LinkedIn (found by search)'] = srch.loc[k, 'Company LinkedIn']
    pc = ps = pd_ = ''
    if k in cls.index and cls.loc[k, 'Parent Company']: pc, pd_, ps = cls.loc[k, 'Parent Company'], cls.loc[k, 'Parent Domain'], cls.loc[k, 'Parent Source']
    elif k in srch.index and srch.loc[k, 'Parent Company']: pc, ps = srch.loc[k, 'Parent Company'], 'search result: ' + srch.loc[k, 'Parent Source']
    if pc and 'copyright' in ps.lower() and not any(w in ps.lower() for w in ['about', 'site text', 'show about', 'search', 'name']):
        notes.append(f'Site copyright names {pc} (not counted as parent: copyright line only)'); pc = pd_ = ps = ''
    o.update({'Parent Company': pc, 'Parent Domain': pd_, 'Parent Source': ps})
    if k in art_keys: t, why = 'Artist / Individual', 'Listed in Artists Alley'
    elif k in cls.index: t, why = cls.loc[k, 'Exhibitor Type'], cls.loc[k, 'Type Reason']; notes += [cls.loc[k, 'Notes']] if cls.loc[k, 'Notes'] else []
    else: t, why = 'Unclear', ''; notes.append('Not yet classified')
    if t not in TYPES: notes.append(f'Type value "{t}" not in list'); t = 'Unclear'
    o.update({'Exhibitor Type': t, 'Type Reason': why, 'Phase 3 Scope': 'Research' if t in RESEARCH else 'Skip', 'Notes': '; '.join(dict.fromkeys(n for n in notes if n))})
    out.append(o)
o = pd.DataFrame(out, index=a.index)
cols = ['Show ID','Show Name','Exhibitor ID','Exhibitor Key','Exhibitor Name','Booth','Website','Domain','Domain Confidence','Domain Evidence','LinkedIn','LinkedIn (found by search)',
        'Parent Company','Parent Domain','Parent Source','Exhibitor Type','Type Reason','Phase 3 Scope','About Summary','Categories','City','State','Country','About','Detail URL','Source','List Status','Notes']
res = pd.concat([a.drop(columns=['Notes','_d']), o], axis=1)
for c in cols:
    if c not in res: res[c] = ''
res = res[cols].fillna('')
res[['Exhibitor Key','Domain','Domain Confidence','Exhibitor Type','Phase 3 Scope']].drop_duplicates('Exhibitor Key').to_csv('phase2_checkpoint.csv', index=False)
with pd.ExcelWriter('phase2_domains_ALL.xlsx', engine='openpyxl') as w:
    res.to_excel(w, sheet_name='All', index=False)
    for sid, g in res.groupby('Show ID'): g.to_excel(w, sheet_name=sid, index=False)
real = res[res['Exhibitor Name'] != '']
print(pd.crosstab(real['Show ID'], real['Exhibitor Type'], margins=True).to_string())
print(pd.crosstab(real['Show ID'], real['Phase 3 Scope'], margins=True).to_string())
print(pd.crosstab(real['Show ID'], real['Domain Confidence'], margins=True).to_string())
print('parents found', (real['Parent Company'] != '').sum(), '| unique in-scope keys', real[real['Phase 3 Scope']=='Research']['Exhibitor Key'].nunique())

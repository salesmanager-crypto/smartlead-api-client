import json, os, glob, pandas as pd
from common import norm_name, domain_of
st = json.load(open('run_state.json'))
COLS = ['Show ID','Show Name','Exhibitor ID','Exhibitor Key','Exhibitor Name','Booth','Website','LinkedIn','About','About Summary',
        'Categories','City','State','Country','Detail URL','Source','List Status','Notes']
GENERIC = {'gmail.com','yahoo.com','hotmail.com','facebook.com','instagram.com','linktr.ee','etsy.com','outlook.com','aol.com','icloud.com','linkedin.com','twitter.com','x.com','tiktok.com','youtube.com','shopify.com','amazon.com'}
frames, summary = [], []
for sid in sorted(st['shows']):
    info = st['shows'][sid]
    f = f'raw/{sid}_exhibitors.csv'; m = f'raw/{sid}_meta.json'
    if not os.path.exists(f):
        summary.append([sid, info['name'], 'not run', '', 0,0,0,0]); continue
    df = pd.read_csv(f, dtype=str, keep_default_na=False)
    meta = json.load(open(m)) if os.path.exists(m) else {}
    df['Show ID'] = sid; df['Show Name'] = info['name']
    for c in COLS:
        if c not in df: df[c] = ''
    real = df['Exhibitor Name'].str.strip() != ''
    # within-show dedupe safety net: by normalized name, then by domain
    df['_n'] = df['Exhibitor Name'].map(norm_name); df['_d'] = df['Website'].map(domain_of)
    df['_rich'] = df[['Website','LinkedIn','About','Booth','Categories']].apply(lambda r: sum(bool(x.strip()) for x in r), axis=1)
    d_real = df[real].sort_values('_rich', ascending=False)
    d_real = d_real.drop_duplicates('_n')
    has_d = d_real['_d'].ne('') & ~d_real['_d'].isin(GENERIC)
    d_real = pd.concat([d_real[has_d].drop_duplicates('_d'), d_real[~has_d]])
    d_real = d_real.sort_values('Exhibitor Name', key=lambda s: s.str.lower())
    df = pd.concat([d_real, df[~real]])
    df = df.reset_index(drop=True)
    df['Exhibitor ID'] = [f'{sid}-{i+1:04d}' for i in range(len(df))]
    frames.append(df)
    r = df[df['Exhibitor Name'].str.strip() != '']
    ls = meta.get('list_status') or (df['List Status'].iloc[0] if len(df) else '')
    summary.append([sid, info['name'], ls, meta.get('exhibitor_list_url',''), len(r), (r['Website']!='').sum(), (r['LinkedIn']!='').sum(), (r['About']!='').sum()])
    info['phase1'] = 'done'; info['list_status'] = ls; info['exhibitor_list_url'] = meta.get('exhibitor_list_url',''); info['exhibitors'] = len(r)
    info['phase1_notes'] = meta.get('notes','')
allx = pd.concat(frames, ignore_index=True)
# cross-show Exhibitor Key: domain when real, else normalized name; unify so that name-or-domain match shares a key
allx['_d'] = allx['Website'].map(domain_of); allx['_n'] = allx['Exhibitor Name'].map(norm_name)
key_by_n, key_by_d = {}, {}
keys = []
for _, r in allx.iterrows():
    d = r['_d'] if r['_d'] and r['_d'] not in GENERIC else ''
    n = r['_n']
    k = (key_by_d.get(d) if d else None) or (key_by_n.get(n) if n else None) or (d or n or r['Exhibitor ID'])
    if d: key_by_d.setdefault(d, k)
    if n: key_by_n.setdefault(n, k)
    keys.append(k)
allx['Exhibitor Key'] = keys
allx = allx[COLS]
with pd.ExcelWriter('phase1_exhibitors_ALL.xlsx', engine='openpyxl') as w:
    allx.to_excel(w, 'All', index=False)
    for sid, g in allx.groupby('Show ID'):
        g.to_excel(w, sid, index=False)
json.dump(st, open('run_state.json','w'), indent=1)
multi = allx[allx['Exhibitor Name']!=''].groupby('Exhibitor Key')['Show ID'].nunique()
print(pd.DataFrame(summary, columns=['Show','Name','List Status','Exhibitor List URL','Exhibitors','With website','With LinkedIn','With About']).to_string(index=False))
print('total exhibitor rows', (allx['Exhibitor Name']!='').sum(), '| unique keys', allx.loc[allx['Exhibitor Name']!='','Exhibitor Key'].nunique(), '| keys at 2+ shows', (multi>1).sum())

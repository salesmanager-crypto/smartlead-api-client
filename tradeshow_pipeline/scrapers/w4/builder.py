import sys, os, csv, json, re
sys.path.insert(0,'/home/user/smartlead-api-client/tradeshow_pipeline')
from common import norm_name, domain_of
BASE='/home/user/smartlead-api-client/tradeshow_pipeline'
COLS=['Show ID','Show Name','Exhibitor Name','Booth','Website','LinkedIn','About','About Summary','Categories','City','State','Country','Detail URL','Source','List Status','Notes']
def clean(v):
    if v is None: return ''
    v=str(v).replace('—',' - ').replace('–','-').replace('\r\n','\n').replace('\r','\n').replace('\xa0',' ')
    v=re.sub(r'[ \t]+',' ',v); v=re.sub(r'\n{3,}','\n\n',v)
    return v.strip()
SKIP_DOM={'jewelry.org.hk'}
SOCIAL=re.compile(r'(facebook|instagram|twitter|x\.com|linkedin|youtube|tiktok|pinterest)\.', re.I)
def good_site(w):
    w=(w or '').strip()
    if not w or ' ' in w.strip() or '.' not in w or SOCIAL.search(w): return False
    return True
def linkedin_company(urls):
    for u in urls or []:
        if u and re.search(r'linkedin\.com/company/', u, re.I): return u.strip()
    return ''
def merge_rows(rows):
    out=[]; idx={}
    for r in rows:
        dom=domain_of(r['Website']) if r['Website'] else ''
        keys=[k for k in ('n:'+norm_name(r['Exhibitor Name']), 'd:'+dom if dom and dom not in SKIP_DOM else None) if k and k not in ('n:','d:')]
        hit=next((idx[k] for k in keys if k in idx), None)
        if hit is None:
            out.append(dict(r)); i=len(out)-1
        else:
            i=hit; m=out[i]
            for c in COLS:
                a, b = m.get(c,''), r.get(c,'')
                if c=='Booth' and b and a and b not in a.split('; '): m[c]=a+'; '+b
                elif c=='Notes' and b and b not in a: m[c]=(a+' '+b).strip() if a else b
                elif len(b)>len(a) and c not in ('Booth','Notes','Exhibitor Name'): m[c]=b
            if norm_name(r['Exhibitor Name'])!=norm_name(m['Exhibitor Name']):
                m['Notes']=(m['Notes']+f" Also listed as '{r['Exhibitor Name']}' (booth {r['Booth'] or 'n/a'}, same website); merged.").strip()
            elif 'Merged duplicate listing' not in m['Notes']:
                m['Notes']=(m['Notes']+' Merged duplicate listing.').strip()
        for k in keys: idx.setdefault(k, i)
    return out
def write(sid, rows, meta):
    rows=[{c:clean(r.get(c,'')) for c in COLS} for r in rows]
    for r in rows:
        if r['State'] and r['State']==r['Country']: r['State']=''
    rows=merge_rows(rows)
    for r in rows:
        for c in COLS: assert '—' not in r[c]
    p=f'{BASE}/raw/{sid}_exhibitors.csv'
    with open(p,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
    meta=dict(meta); meta['exhibitors']=len([r for r in rows if r['Exhibitor Name']])
    meta={k:(clean(v) if isinstance(v,str) else v) for k,v in meta.items()}
    json.dump(meta, open(f'{BASE}/raw/{sid}_meta.json','w'), indent=1, ensure_ascii=False)
    st=dict(n=len(rows), web=sum(1 for r in rows if r['Website']), li=sum(1 for r in rows if r['LinkedIn']), about=sum(1 for r in rows if r['About']), summ=sum(1 for r in rows if r['About Summary']))
    print(sid, st); return rows

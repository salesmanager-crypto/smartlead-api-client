import json, sys, re, os
sys.path.insert(0,'/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad/w4')
from builder import *
SID='S11'; NAME='JA New York International Jewelry Show (Fall)'
LIST='https://s36.a2zinc.net/clients/SWM/JAFall2026/Public/eventmap.aspx?ID=757'
SWL='https://jafall2026.smallworldlabs.com/exhibitors'
A=[json.loads(l) for l in open(f'{BASE}/cache/pages/S11/a2z_details.jsonl')]
W={}
LAB={'Name','Founded','Website','Address','Facebook','Instagram','LinkedIn','Twitter','YouTube','Description','Phone','Email','[Cancel]'}
for l in open(f'{BASE}/cache/pages/S11/swl_details.jsonl'):
    d=json.loads(l); t=d.get('text','')
    seg=t.split(' | About | ',1)[1] if ' | About | ' in t else ''
    seg=seg.split(' | [Cancel]')[0]
    toks=seg.split(' | '); f={}; cur=None
    for tk in toks:
        k='Categories' if tk.startswith('Categories') and len(tk)<16 else tk
        if k in LAB or k=='Categories': cur=k; f.setdefault(cur,[]); continue
        if cur: f[cur].append(tk)
    d['f']=f; W[d['boothid']]=d
rows=[]
for a in A:
    notes=[]; w=W.get(a['boothid'],{}); f=w.get('f',{})
    web=a.get('website') or ' '.join(f.get('Website',[]))
    if web and not good_site(web): notes.append(f"Website field read '{web}'."); web=''
    cats=[]
    for c in ', '.join(f.get('Categories',[])).split(','):
        c=c.strip()
        if not c: continue
        if cats and c[0].islower(): cats[-1]+=', '+c
        else: cats.append(c)
    li=linkedin_company(w.get('links',[]))
    if f.get('Founded'): notes.append('Founded '+f['Founded'][0]+'.')
    if not web: notes.append('No website shown on a2z or Small World Labs profile.')
    notes.append('Profiles carry no description.')
    rows.append({'Show ID':SID,'Show Name':NAME,'Exhibitor Name':a.get('h1') or a['name'],'Booth':a['booth'],'Website':web,'LinkedIn':li,'About':'','About Summary':'',
      'Categories':'; '.join(cats[:5]),'City':a.get('city',''),'State':a.get('state',''),'Country':a.get('country',''),
      'Detail URL':w.get('url') or a['detail_url'],'Source':LIST,'List Status':'current list','Notes':' '.join(notes)})
print('a2z',len(A),'swl matched',sum(1 for a in A if a['boothid'] in W))
meta={'show_id':SID,'show_name':NAME,'list_status':'current list','exhibitor_list_url':LIST,'platform':'a2z (a2zinc.net, Smartwork Media) + Small World Labs directory (jafall2026.smallworldlabs.com)',
 'notes':'JA New York Fall 2026 (Smartwork Media, not Emerald) lists 167 exhibitors on its a2z floor plan; the same list is mirrored on the Small World Labs attendee directory ('+SWL+'). Opened every a2z eBooth page (name, city/state/country, booth, sometimes website) and every Small World Labs company page (adds website, categories, founded year for a few). Very sparse profiles: most exhibitors show no website, and none show a description or LinkedIn. Detail URL points to the Small World Labs profile.'}
write(SID, rows, meta)

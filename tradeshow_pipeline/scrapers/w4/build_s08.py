import json, sys, re, os
sys.path.insert(0,'/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad/w4')
from builder import *
SID='S08'; NAME='Jewelers International Showcase (JIS) Fall'
LIST='https://www.jisshow.com/fall/en-us/attend/exhibitor-directory.html'
SUMF='/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad/w4/sum_S08.json'
SUM=json.load(open(SUMF)) if os.path.exists(SUMF) else {}
hits=json.load(open(f'{BASE}/cache/pages/S08/algolia_hits.json'))
det={}
for l in open(f'{BASE}/cache/pages/S08/details.jsonl'):
    d=json.loads(l); det[d['org']]=d['data']
def li_clean(u):
    if not u: return ''
    m=re.findall(r'linkedin\.com/(?:company|organization-guest/company)/([^/?#\s]+)', u)
    if not m: return ''
    slug=m[-1]
    if slug.startswith('http') or not slug: return ''
    return 'https://www.linkedin.com/company/'+slug
rows=[]
for h in hits:
    org=h['organisationGuid']; d=det.get(org) or {}
    ml=(d.get('multilingual') or [{}])[0]
    notes=[]
    name=h.get('exhibitorName') or h.get('companyName')
    desc=ml.get('description') or h.get('exhibitorDescription') or ''
    obj=ml.get('showObjective') or h.get('showObjective') or ''
    about=desc.strip()
    if not about and obj: about=obj.strip(); notes.append('No company description; About is the show objective text.')
    web=d.get('website') or h.get('website') or ''
    if web and not good_site(web): notes.append(f"Website field read '{web}'."); web=''
    li=''
    for s in d.get('socialMedia') or []:
        if s.get('name')=='LINKEDIN':
            li=li_clean(s.get('url'))
            if not li: notes.append(f"LinkedIn link on page was not a company page ({s.get('url')}).")
    cats=[]; pav=[]
    for fc in d.get('filterCategories') or []:
        nm=fc['multilingual'][0]['name']
        vals=[r['multilingual'][0]['name'] for r in fc.get('responses') or []]
        if nm=='Pavilion': pav+=vals
        else: cats+=vals
    if not d:
        for k,v in (h.get('exhibitorFilters') or {}).items():
            if isinstance(v,dict):
                vals=[re.sub(r'^\d+:\d+: ','',x) for x in v.get('lvl0',[])]
                (pav if k=='Pavilion' else cats).extend(vals)
    catl=(['Pavilion: '+p for p in pav[:1]]+cats)[:5]
    city=state=''
    if d and not d.get('hideAddress'):
        city=ml.get('city') or ''; state=ml.get('stateProvince') or ''
    elif d.get('hideAddress'): notes.append('Exhibitor hid its address.')
    country=ml.get('country') or h.get('countryName') or ''
    booth=h.get('standReference') or '; '.join(s['name'] for s in d.get('stands') or [])
    if h.get('mainStandHolderName'): notes.append(f"Shares stand with {h['mainStandHolderName']}.")
    rb=[b['name'] for b in ml.get('representedBrands') or []] or [b if isinstance(b,str) else b.get('name','') for b in h.get('representedBrands') or []]
    if rb: notes.append('Brands: '+', '.join(rb[:8])+'.')
    if not web: notes.append('Detail page had no website.')
    if not d: notes.append('Detail API call failed; fields from directory index only.')
    rows.append({'Show ID':SID,'Show Name':NAME,'Exhibitor Name':name,'Booth':booth,'Website':web,'LinkedIn':li,'About':about,
        'About Summary':SUM.get(org,'') if about else '','Categories':'; '.join(catl),'City':city,'State':state,'Country':country,
        'Detail URL':f'https://www.jisshow.com/fall/en-us/attend/exhibitor-directory/exhibitor-details.{org}.html','Source':LIST,'List Status':'current list','Notes':' '.join(notes),'_org':org})
PRI={'Marathon Company':0,'Sanghavi Solitaire Inc.':0}
rows.sort(key=lambda r:PRI.get(r['Exhibitor Name'],1))
if '--dump' in sys.argv:
    json.dump([{'k':r['_org'],'n':r['Exhibitor Name'],'a':r['About']} for r in rows if r['About']], open('/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad/w4/abouts_S08.json','w'))
meta={'show_id':SID,'show_name':NAME,'list_status':'current list','exhibitor_list_url':LIST,'platform':'RX (Reed Exhibitions) exhibitor directory on Algolia + RX GraphQL API',
 'notes':'JIS is run by RX (not Emerald/Map Your Show). Pulled all exhibitors of the Fall 2026 edition from the Algolia index that powers the jisshow.com exhibitor directory, then the per-exhibitor RX GraphQL record behind each detail page (website, social links, address, categories, description). Categories start with the pavilion. About is the company description; where empty, the show objective text is used and noted. Emails and phones exist in the source but were not required.'}
write(SID, rows, meta)

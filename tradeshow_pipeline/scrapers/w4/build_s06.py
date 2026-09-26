import json, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad/w4')
from builder import *
SID='S06'; NAME='Premiere Columbus'
LIST='https://s19.a2zinc.net/clients/informabeauty/premierecolumbus2026/Public/EventMap.aspx?shMode=E&ID=1095'
R=[json.loads(l) for l in open(f'{BASE}/cache/pages/S06/a2z_details.jsonl')]
FIX={'www/modologie.com':'www.modologie.com'}
rows=[]
for r in R:
    notes=[]
    w=r.get('website','')
    if w in FIX: notes.append(f"Page showed website as '{w}'; corrected obvious typo."); w=FIX[w]
    elif w and not good_site(w): notes.append(f"Website field on page read '{w}' (not a URL); left blank."); w=''
    if not w: notes.append('Detail page had no website.') if not notes else None
    city, state = r.get('city',''), r.get('state','')
    if r['name']=='Morfose': notes.append('City field on page holds a street address; Istanbul appears in the state field.')
    notes.append('a2z detail page shows only name, location, website and booth (no description, categories or LinkedIn).')
    rows.append({'Show ID':SID,'Show Name':NAME,'Exhibitor Name':r.get('h1') or r['name'],'Booth':r['booth'],'Website':w,'LinkedIn':linkedin_company(r.get('social')),
        'About':'','About Summary':'','Categories':'','City':city,'State':state,'Country':r.get('country',''),'Detail URL':r['detail_url'],'Source':LIST,'List Status':'current list','Notes':' '.join(notes)})
meta={'show_id':SID,'show_name':NAME,'list_status':'current list','exhibitor_list_url':LIST,'platform':'a2z (a2zinc.net, Informa Beauty)',
 'notes':'Exhibitor list from the a2z interactive floor plan linked on premierecolumbusshow.com (103 listings, 2026 edition). Opened every eBooth detail page: they show only company name, city/state/country, website and booth. No descriptions, product categories or LinkedIn are published, so About, Categories and LinkedIn are blank. One company (Beaute Tsuru DBA KSK Enterprise) had two booths and was merged. A few website fields held non-URLs (e.g. "Instagram/ Facebook") and were left blank.'}
write(SID, rows, meta)

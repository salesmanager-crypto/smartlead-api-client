import json, sys, re, os
sys.path.insert(0,'/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad/w4')
from builder import *
from bs4 import BeautifulSoup
SID='S09'; NAME='Coffee Fest Dallas / Ft. Worth'
LIST='https://cofdfw1026.mapyourshow.com/8_0/explore/exhibitor-gallery.cfm?featured=false'
SUMF='/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad/w4/sum_S09.json'
SUM=json.load(open(SUMF)) if os.path.exists(SUMF) else {}
hits=json.load(open(f'{BASE}/cache/pages/S09/gallery_hits.json'))
rows=[]
for h in hits:
    f=h['fields']; exhid=f['exhid_l']; notes=[]
    url=f'https://cofdfw1026.mapyourshow.com/8_0/exhibitor/exhibitor-details.cfm?exhid={exhid}'
    fp=f'{BASE}/cache/pages/S09/details/{exhid}.html'
    web=li=''; cats=[]; city=state=country=''; about=(f.get('exhdesc_t') or '').strip(); booths=[]
    if os.path.exists(fp):
        s=BeautifulSoup(open(fp).read(),'html.parser')
        ci=s.select_one('#js-vue-contactinfo')
        if ci:
            a=ci.select_one('a[title^="Visit"]')
            if a: web=a['href']
            links=[x['href'] for x in ci.select('a[href]')]
            li=linkedin_company(links)
            if not li and any('linkedin.com' in x for x in links): notes.append('LinkedIn link on page is not a company page.')
            adr=ci.select_one('.showcase-address, address, .address')
            if adr: notes.append('Address shown: '+adr.get_text(', ',strip=True))
        de=s.select_one('#js-vue-description .section-description')
        if de and len(de.get_text(' ',strip=True))>len(about): about=de.get_text('\n',strip=True)
        pc=s.select_one('#js-vue-products')
        if pc:
            for x in pc.select('li'):
                t=x.get_text(' ',strip=True); p=[y.strip() for y in t.split('>')]
                t=p[0] if len(p)==2 and p[0]==p[1] else ' > '.join(p)
                if t not in cats: cats.append(t)
        for x in s.select('aside a[href*="floorplan_link"]'):
            booths.append(x.get_text(' ',strip=True))
    else:
        notes.append('Detail page could not be loaded.')
    booth='; '.join(re.sub(r'^.*?—\s*','',b) for b in booths) or '; '.join(x.replace('randomstring','') for x in f.get('boothsdisplay_la',[]))
    if not web: notes.append('Detail page had no website.')
    if os.path.exists(fp) and not cats: notes.append('No product categories listed.')
    rows.append({'Show ID':SID,'Show Name':NAME,'Exhibitor Name':f['exhname_t'],'Booth':booth,'Website':web,'LinkedIn':li,'About':about,
      'About Summary':SUM.get(exhid,'') if about else '','Categories':'; '.join(cats[:5]),'City':city,'State':state,'Country':country,
      'Detail URL':url,'Source':LIST,'List Status':'current list','Notes':' '.join(notes)+(' ' if notes else '')+'Detail page shows no city/state/country.','_k':exhid})
if '--dump' in sys.argv:
    json.dump([{'k':r['_k'],'n':r['Exhibitor Name'],'a':r['About']} for r in rows if r['About']], open('/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad/w4/abouts_S09.json','w'))
meta={'show_id':SID,'show_name':NAME,'list_status':'current list','exhibitor_list_url':LIST,'platform':'Map Your Show (cofdfw1026.mapyourshow.com)',
 'notes':'Pulled the full exhibitor gallery JSON from Map Your Show (128 exhibitors for Oct 2026 Dallas/Fort Worth), then rendered every exhibitor detail page with Playwright (plain requests get an empty 202 bot check). Detail pages show website, social links, description and product categories; no city/state/country or address is published, so those columns are blank. About 65 of 128 exhibitors have basic listings (name and booth only, no website, description or categories); these are marked in Notes. 4 exhibitors show no booth.'}
write(SID, rows, meta)

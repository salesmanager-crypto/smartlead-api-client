import sys, json, os, re, html
sys.path.insert(0,'/home/user/smartlead-api-client/tradeshow_pipeline'); os.chdir('/home/user/smartlead-api-client/tradeshow_pipeline')
from common import fetch
from bs4 import BeautifulSoup
sid, mapurl = sys.argv[1], sys.argv[2]
base = mapurl.rsplit('/',1)[0] + '/'
h = fetch(mapurl)
s = BeautifulSoup(h, 'html.parser')
rows = []
for tr in s.select('tr[data-boothid]'):
    nm = tr.select_one('td.exhibitorName, a.exhibitorName')
    if not nm: continue
    bl = tr.select_one('a.boothLabel')
    rows.append({'boothid': tr['data-boothid'], 'name': nm.get_text(' ', strip=True), 'booth': bl.get_text(strip=True) if bl else ''})
print(sid, 'list rows', len(rows), flush=True)
out = f'cache/pages/{sid}/a2z_details.jsonl'
done = set()
if os.path.exists(out):
    for l in open(out): done.add(json.loads(l)['boothid'])
f = open(out, 'a')
for i, r in enumerate(rows):
    if r['boothid'] in done: continue
    url = base + f"eBooth.aspx?BoothID={r['boothid']}&Nav=False"
    d = fetch(url)
    rec = dict(r, detail_url=url)
    if d:
        b = BeautifulSoup(d, 'html.parser')
        c = b.select_one('#eboothContainer')
        if c:
            g = lambda sel: (c.select_one(sel).get_text(' ', strip=True).rstrip(',').strip() if c.select_one(sel) else '')
            rec['h1'] = g('h1'); rec['city'] = g('.BoothContactCity'); rec['state'] = g('.BoothContactState'); rec['country'] = g('.BoothContactCountry')
            rec['website'] = g('.BoothContactUrl')
            rec['social'] = [a.get('href') for a in c.select('.SocialMediaContainer a[href]')]
            p = c.select_one('.BoothPrintProfile') or c.select_one('#BoothPrintProfile')
            rec['about'] = p.get_text('\n', strip=True) if p else ''
            rec['cats'] = [x.get_text(' ', strip=True) for x in c.select('.ProductCategoryLi, .ProductCategoryContainer li, #Category li')]
            rec['text'] = re.sub(r'\s+', ' ', c.get_text(' ', strip=True))[:4000]
    else:
        rec['error'] = 'fetch failed'
    f.write(json.dumps(rec) + '\n'); f.flush()
    if i % 20 == 0: print(i, r['name'], flush=True)
print('DONE', flush=True)

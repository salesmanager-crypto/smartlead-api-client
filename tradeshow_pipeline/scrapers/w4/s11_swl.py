import asyncio, sys, json, re, os
sys.path.insert(0,'/home/user/smartlead-api-client/tradeshow_pipeline'); os.chdir('/home/user/smartlead-api-client/tradeshow_pipeline')
from browser import new_browser
from common import fetch
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
LP='cache/pages/S11/swl_list.json'
async def listing():
    items={}
    async with async_playwright() as p:
        b, ctx = await new_browser(p); page = await ctx.new_page()
        await page.goto('https://jafall2026.smallworldlabs.com/exhibitors', wait_until='networkidle', timeout=90000)
        for pg in range(1, 10):
            h = await page.content()
            open(f'cache/pages/S11/swl_list_p{pg}.html','w').write(h)
            s = BeautifulSoup(h, 'html.parser')
            n0=len(items)
            for tr in s.select('tr'):
                a = tr.select_one('a[href^="/co/"]')
                if not a: continue
                m = tr.select_one('a[href*="MapItBoothID"]')
                bid = re.search(r'MapItBoothID=(\d+)', m['href']).group(1) if m else ''
                bt = m.get_text(' ', strip=True) if m else ''
                items[a['href']] = {'slug': a['href'], 'name': a.get_text(' ', strip=True), 'boothid': bid, 'booth_text': bt}
            print('page', pg, len(items)-n0, flush=True)
            nxt = await page.query_selector('.pager-right-next')
            if not nxt or len(items)==n0: break
            cls = await nxt.get_attribute('class') or ''
            if 'disabled' in cls: break
            await nxt.click(); await page.wait_for_timeout(3500)
        await b.close()
    return list(items.values())
if not os.path.exists(LP):
    json.dump(asyncio.run(listing()), open(LP,'w'))
items=json.load(open(LP)); print('items', len(items), flush=True)
out='cache/pages/S11/swl_details.jsonl'
done=set(json.loads(l)['slug'] for l in open(out)) if os.path.exists(out) else set()
f=open(out,'a')
for i,it in enumerate(items):
    if it['slug'] in done: continue
    url='https://jafall2026.smallworldlabs.com'+it['slug']
    h=fetch(url); rec=dict(it, url=url)
    if h:
        s=BeautifulSoup(h,'html.parser')
        for x in s(['script','style','nav','header','footer']): x.decompose()
        rec['text']=re.sub(r'\s+',' ',s.body.get_text(' | ', strip=True))[:6000]
        rec['links']=[a['href'] for a in s.select('a[href^=http]') if 'smallworldlabs' not in a['href'] and 'a2zinc' not in a['href'] and 'mya2zevents' not in a['href']]
    f.write(json.dumps(rec)+'\n'); f.flush()
    if i%20==0: print(i, it['name'], flush=True)
print('DONE', flush=True)

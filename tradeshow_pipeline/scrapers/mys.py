import sys, os, json, re, asyncio, random, html, time
sys.path.insert(0, '/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad')
from out import *
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
sys.path.insert(0, BASE)
from browser import new_browser
SID, HOST, SHOW = sys.argv[1], sys.argv[2], sys.argv[3]
ROOT = f'https://{HOST}/8_0'
GAL = f'{ROOT}/explore/exhibitor-gallery.cfm?featured=false'
CD = os.path.join(BASE, 'cache', 'pages', SID); os.makedirs(CD, exist_ok=True)
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
async def solve(page, url):
    await page.goto(url, wait_until='domcontentloaded', timeout=90000); await page.wait_for_timeout(5000)
async def get(ctx, page, url, cachefile):
    if os.path.exists(cachefile) and os.path.getsize(cachefile) > 1000:
        return open(cachefile, encoding='utf-8').read()
    back = 5
    for attempt in range(5):
        await asyncio.sleep(random.uniform(1.0, 2.0))
        try:
            r = await ctx.request.get(url, headers={'X-Requested-With': 'XMLHttpRequest', 'Referer': GAL}, timeout=60000)
            t = await r.text()
        except Exception as e:
            log('err', url, e); await asyncio.sleep(back); back *= 2; continue
        if r.status == 429:
            log('429 pause 600'); await asyncio.sleep(600); continue
        if r.status == 202 or (r.status == 200 and len(t) < 50):
            log('waf challenge, re-solving'); await solve(page, url); await asyncio.sleep(back); back *= 2; continue
        if r.status >= 500: await asyncio.sleep(back); back *= 2; continue
        if r.status >= 400: log('status', r.status, url); return None
        open(cachefile, 'w', encoding='utf-8').write(t); return t
    return None
def jsval(t, name):
    m = re.search(name + r':\s*"((?:[^"\\]|\\.)*)"', t)
    if not m: return ''
    s = m.group(1).replace("\\'", "'")
    try: return json.loads('"' + s + '"')
    except Exception: return s.replace('\\/', '/')
def parse_detail(t):
    if t.lstrip().startswith('{'):
        try:
            j = json.loads(t)['DATA']
            t = '\n'.join(v for v in j.values() if isinstance(v, str))
        except Exception: pass
    d = {}
    d['website'] = jsval(t, 'websiteValue'); d['linkedin'] = jsval(t, 'linkedInValue')
    m = re.search(r'addressValues:\s*(\{.*?\}),\s*\n', t)
    addr = {}
    if m:
        try: addr = json.loads(m.group(1))
        except Exception: pass
    d['city'] = addr.get('CITY', ''); d['state'] = addr.get('STATE', ''); d['country'] = addr.get('COUNTRY', '')
    m = re.search(r"component\('company-description'.*?description:\s*\"((?:[^\"\\]|\\.)*)\"", t, re.S)
    desc = ''
    if m:
        s = m.group(1).replace("\\'", "'")
        try: desc = json.loads('"' + s + '"')
        except Exception: desc = s
    d['about'] = strip_html(desc)
    s = BeautifulSoup(t, 'html.parser')
    for sc in s.find_all('script'): sc.decompose()
    cats = []
    for a in s.select('a[href*="searchtype/category"]'):
        c = a.get_text(' ', strip=True)
        if c and c not in cats: cats.append(c)
    d['cats'] = cats
    booths = []
    for a in s.select('a[href*="floorplan_link.cfm"]'):
        mm = re.search(r'booth=([^&]+)', a.get('href', ''))
        if mm and mm.group(1) not in booths: booths.append(html.unescape(mm.group(1)))
    d['booths'] = booths
    h = s.select_one('h1.exhibitor-name'); d['name'] = h.get_text(' ', strip=True) if h else ''
    return d
async def main():
    async with async_playwright() as p:
        b, ctx = await new_browser(p); page = await ctx.new_page()
        await solve(page, GAL)
        hits = []; start = 0; total = None
        while True:
            u = f'{ROOT}/ajax/remote-proxy.cfm?action=search&searchtype=exhibitorgallery&searchsize=557&start={start}'
            t = await get(ctx, page, u, os.path.join(CD, f'gallery_{start}.json'))
            ex = json.loads(t)['DATA']['results']['exhibitor']
            total = int(ex['found']); hits += ex['hit']; log('gallery', start, len(ex['hit']), total)
            start += len(ex['hit'])
            if not ex['hit'] or start >= total: break
        exh = {}
        for h in hits:
            f = h['fields']; i = f['exhid_l']
            if i in exh: continue
            exh[i] = f
        log('unique exhibitors', len(exh))
        done = {r['Detail URL'] for r in read_rows(SID)}
        for n, (i, f) in enumerate(exh.items()):
            durl = f'{ROOT}/exhibitor/exhibitor-details.cfm?exhid={i}'
            if durl in done: continue
            t = await get(ctx, page, durl, os.path.join(CD, f'exh_{i}.html'))
            notes = []
            gb = [re.sub('randomstring', '', x) for x in f.get('boothsdisplay_la', [])]
            if t:
                d = parse_detail(t)
            else:
                d = dict(website='', linkedin='', city='', state='', country='', about='', cats=[], booths=[], name='')
                notes.append('detail page could not be loaded')
            about = d['about'] or strip_html(f.get('exhdesc_t', ''))
            li = linkedin_ok(d['linkedin'])
            if d['linkedin'] and not li: notes.append('LinkedIn link on page was not a company page: ' + d['linkedin'])
            if t and not d['website']: notes.append('detail page had no website')
            row = {'Show ID': SID, 'Show Name': SHOW, 'Exhibitor Name': f.get('exhname_t') or d['name'],
                   'Booth': ', '.join(d['booths'] or gb), 'Website': fix_url(d['website']), 'LinkedIn': li,
                   'About': about, 'About Summary': summarize(about), 'Categories': '; '.join(d['cats'][:5]),
                   'City': d['city'], 'State': d['state'], 'Country': d['country'], 'Detail URL': durl,
                   'Source': GAL, 'List Status': 'current list', 'Notes': '; '.join(notes)}
            append_row(SID, row)
            if n % 25 == 0: log('detail', n, len(exh), row['Exhibitor Name'])
        await b.close()
    rows = finalize(SID); log('FINAL', stats(rows))
asyncio.run(main())

"""MapYourShow (8_0) exhibitor scraper, used for the Emerald souvenir/resort shows
(S03 lv1026, S14 smg1126, S16 ocg1126, S19 gsr1226).

Gallery list: /8_0/ajax/remote-proxy.cfm?action=search&searchtype=exhibitorgallery (plain requests via common.fetch).
Detail pages sit behind a JS challenge (HTTP 202 empty body to requests), so they are rendered in Playwright.
Per-exhibitor extracted JSON (+ trimmed HTML) cached at cache/pages/<SID>/.
Stage 1 (this script): gallery + details, CSV appended incrementally (checkpoint, resumable).
Usage: python3 mys_emerald_scraper.py S14 [S16 ...]
"""
import asyncio, csv, json, os, random, re, sys, time
from common import fetch, norm_name, domain_of
from browser import new_browser
from playwright.async_api import async_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
SHOWS = {
    'S03': ('Las Vegas Souvenir & Resort Gift Show', 'lv1026'),
    'S14': ('Smoky Mountain Gift Show', 'smg1126'),
    'S16': ('Ocean City Resort Gift Expo', 'ocg1126'),
    'S19': ('Grand Strand Gift & Resort Merchandise Show', 'gsr1226'),
}
COLS = ['Show ID', 'Show Name', 'Exhibitor Name', 'Booth', 'Website', 'LinkedIn', 'About', 'About Summary', 'Categories',
        'City', 'State', 'Country', 'Detail URL', 'Source', 'List Status', 'Notes']

JS = r'''() => {
 const q=(s)=>document.querySelector(s);
 const txt=(e)=>e?e.innerText.trim():'';
 const sb=q('#myssidebar');
 const booths=sb?[...sb.querySelectorAll('ul.ma0 li')].map(e=>e.innerText.trim()).filter(Boolean):[];
 const ci=q('#js-vue-contactinfo');
 const links=ci?[...ci.querySelectorAll('a[href]')].map(a=>({href:a.href,title:a.title||'',text:a.innerText.trim()})):[];
 const cols=ci?[...ci.querySelectorAll('.column')].map(e=>e.innerText.trim()):[];
 const desc=txt(q('#section-description'));
 const cats=[...document.querySelectorAll('#js-vue-products li')].map(e=>e.innerText.trim());
 const main=q('section.section-wrapper-main_exhibitor');
 return {name:txt(q('h1')),booths,links,cols,desc,cats,sidebar:txt(sb),html:main?main.outerHTML.replace(/<svg[\s\S]*?<\/svg>/g,''):''};
}'''


def gallery(sid):
    code = SHOWS[sid][1]
    cdir = os.path.join(BASE, 'cache', 'pages', sid); os.makedirs(cdir, exist_ok=True)
    gp = os.path.join(cdir, 'gallery.json')
    if os.path.exists(gp):
        return json.load(open(gp))
    hits, start = [], 0
    ref = f'https://{code}.mapyourshow.com/8_0/explore/exhibitor-gallery.cfm?featured=false'
    while True:
        u = f'https://{code}.mapyourshow.com/8_0/ajax/remote-proxy.cfm?action=search&searchtype=exhibitorgallery&searchsize=100&start={start}'
        d = json.loads(fetch(u, headers={'Referer': ref, 'X-Requested-With': 'XMLHttpRequest'}))
        r = d['DATA']['results']['exhibitor']
        hits += [h['fields'] for h in r['hit']]
        start += 100
        if start >= r['found'] or not r['hit']:
            break
    json.dump(hits, open(gp, 'w'))
    print(sid, 'gallery', len(hits), flush=True)
    return hits


async def details(sid, hits):
    code = SHOWS[sid][1]
    cdir = os.path.join(BASE, 'cache', 'pages', sid)
    todo = [h for h in hits if not os.path.exists(os.path.join(cdir, f"det_{h['exhid_l']}.json"))]
    print(sid, 'details todo', len(todo), 'of', len(hits), flush=True)
    if not todo:
        return
    async with async_playwright() as p:
        b, ctx = await new_browser(p); page = await ctx.new_page()
        await page.route('**/*', lambda r: r.abort() if r.request.resource_type in ('image', 'font', 'media') else r.continue_())
        for i, h in enumerate(todo):
            ex = h['exhid_l']
            url = f'https://{code}.mapyourshow.com/8_0/exhibitor/exhibitor-details.cfm?exhid={ex}'
            data = None
            for attempt in range(3):
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    await page.wait_for_selector('#js-vue-contactinfo, #js-vue-description, h1', timeout=30000)
                    await page.wait_for_timeout(800)
                    data = await page.evaluate(JS)
                    if data.get('name'):
                        break
                    body = (await page.inner_text('body'))[:300]
                    print('no name', ex, body.replace('\n', ' '), flush=True)
                except Exception as e:
                    print('err', ex, attempt, str(e)[:200], flush=True)
                await asyncio.sleep(10 * (attempt + 1))
            if data and data.get('name'):
                data['url'] = url
                json.dump(data, open(os.path.join(cdir, f'det_{ex}.json'), 'w'))
                append_row(sid, row_for(sid, h, data))
            if i % 25 == 0:
                print(sid, i, len(todo), ex, flush=True)
            await asyncio.sleep(random.uniform(1.0, 2.0))
        await b.close()


def clean(s):
    s = (s or '').replace('—', ' - ').replace('–', '-').replace('\xa0', ' ')
    return re.sub(r'[ \t]+', ' ', s).strip()


def row_for(sid, h, d):
    name, code = SHOWS[sid]
    web = ''; li = ''; other = []
    for a in d.get('links', []):
        href = a['href']
        if 'on the web' in a.get('title', '') and not web:
            web = href
        elif re.search(r'linkedin\.com/company/', href, re.I) and not li:
            li = href.split('?')[0]
        else:
            other.append(href)
    booths = []
    for t in d.get('booths', []):
        m = re.split(r'\s[—–-]\s', t)
        booths.append(m[-1].strip())
    if not booths:
        booths = [re.sub('randomstring', '', x) for x in h.get('boothsdisplay_la', []) or []]
    cats = []
    for c in d.get('cats', []):
        parts = [x.strip() for x in c.split('>')]
        c2 = parts[0] if len(parts) == 2 and parts[0] == parts[1] else ' > '.join(parts)
        if c2 not in cats:
            cats.append(c2)
    about = clean(d.get('desc') or '')
    # contact column text other than the website line (address lines if any)
    contact_lines = []
    for col in d.get('cols', []):
        for ln in col.split('\n'):
            ln = ln.strip()
            if ln and domain_of(ln) != domain_of(web):
                contact_lines.append(ln)
    city = state = country = ''
    notes = []
    if not web: notes.append('detail page had no website')
    if not about: notes.append('detail page had no description')
    if not booths: notes.append('no booth shown')
    return {
        'Show ID': sid, 'Show Name': name, 'Exhibitor Name': clean(d.get('name') or h.get('exhname_t')),
        'Booth': '; '.join(booths), 'Website': web, 'LinkedIn': li, 'About': about, 'About Summary': '',
        'Categories': '; '.join(cats[:5]), 'City': city, 'State': state, 'Country': country,
        'Detail URL': d['url'],
        'Source': f'https://{code}.mapyourshow.com/8_0/explore/exhibitor-gallery.cfm?featured=false',
        'List Status': 'current list', 'Notes': '; '.join(notes), '_contact': ' | '.join(contact_lines),
    }


def append_row(sid, row):
    p = os.path.join(BASE, 'raw', f'{sid}_exhibitors.csv')
    new = not os.path.exists(p)
    with open(p, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
        if new: w.writeheader()
        w.writerow(row)


async def main(sids):
    for sid in sids:
        hits = gallery(sid)
        await details(sid, hits)
        print(sid, 'DONE', flush=True)

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:]))

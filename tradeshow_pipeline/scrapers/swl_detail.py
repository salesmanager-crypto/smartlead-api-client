import sys, os, re, json, glob, urllib.parse, html, time
sys.path.insert(0, '/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad')
from out import *
sys.path.insert(0, BASE)
from common import fetch
from bs4 import BeautifulSoup
SID, HOST, SHOW = sys.argv[1], sys.argv[2], sys.argv[3]
CD = os.path.join(BASE, 'cache', 'pages', SID)
LIST = f'https://{HOST}/exhibitors'
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def list_html():
    out = []
    for f in sorted(glob.glob(f'{CD}/list_*.html'), key=lambda x: int(re.search(r'list_(\d+)', x).group(1))):
        t = open(f, encoding='utf-8').read()
        if t.lstrip().startswith('{'):
            try: t = urllib.parse.unquote(json.loads(t).get('data') or '')
            except Exception: t = ''
        out.append(t)
    return out
entries = {}
for t in list_html():
    s = BeautifulSoup(t, 'html.parser')
    for tr in s.select('tr'):
        a = tr.select_one('a[href^="/co/"]')
        if not a: continue
        slug = a['href']
        booth = ''
        for b in tr.select('a'):
            m = re.search(r'Booth\s*#\s*(.+)', b.get_text(' ', strip=True))
            if m: booth = m.group(1).strip(); break
        if slug not in entries: entries[slug] = dict(name=a.get_text(' ', strip=True), booth=booth)
log('entries', len(entries))
labels = {}
def parse_addr(lines):
    lines = [l.strip() for l in lines if l.strip()]
    city = state = country = ''
    if not lines: return city, state, country
    if len(lines) >= 2:
        country = lines[-1]; loc = lines[-2]
    else:
        loc = lines[0]
    m = re.match(r'^(.+?),\s*(.+?)(?:\s+[\dA-Z]{3,}[\d\- A-Z]*)?$', loc)
    if m: city, state = m.group(1).strip(), m.group(2).strip()
    else: city = re.sub(r'\s*[\d\-]{3,}$', '', loc).strip()
    if re.search(r'\d', city) and len(lines) >= 2: city = ''
    return city, state, country
done = {r['Detail URL'] for r in read_rows(SID)}
for n, (slug, e) in enumerate(entries.items()):
    durl = f'https://{HOST}{slug}'
    if durl in done: continue
    t = fetch(durl)
    notes = []; f = {}
    if not t: notes.append('detail page could not be loaded')
    else:
        s = BeautifulSoup(t, 'html.parser')
        for r in s.select('div.row.no-gutters'):
            lab = r.select_one('.text-secondary'); val = r.select_one('.profileResponse')
            if not (lab and val): continue
            k = lab.get_text(' ', strip=True); k = re.sub(r'\s*\(\d+\)$', '', k)
            labels[k] = labels.get(k, 0) + 1
            if k in f: continue
            links = [a.get('href', '') for a in val.select('a')]
            vhtml = str(val)
            f[k] = dict(text=strip_html(re.sub(r'^<div[^>]*>|</div>$', '', vhtml)), links=links,
                        lines=[strip_html(x) for x in re.split(r'<br\s*/?>', re.sub(r'^<div[^>]*>|</div>$', '', vhtml))])
        booth_links = re.findall(r'MapItBooth=([^&"]+)', t)
        if not e['booth'] and booth_links: e['booth'] = ', '.join(dict.fromkeys(html.unescape(b) for b in booth_links))
    about = ''
    for k in ('Company Description', 'What We Do', 'Description', 'About', 'About Us', 'Overview'):
        if k in f and f[k]['text']: about = f[k]['text']; break
    web = ''
    if 'Website' in f: web = (f['Website']['links'] or [f['Website']['text']])[0]
    li_raw = ''
    if 'LinkedIn' in f: li_raw = (f['LinkedIn']['links'] or [f['LinkedIn']['text']])[0]
    li = linkedin_ok(li_raw)
    if li_raw and not li: notes.append('LinkedIn link on page was not a company page: ' + li_raw)
    cats = []
    for k in ('Categories', 'Product Categories', 'Categories:'):
        if k in f: cats = [c.strip() for c in f[k]['text'].split(',') if c.strip()]; break
    city = state = country = ''
    for k in ('Address', 'Location'):
        if k in f: city, state, country = parse_addr(f[k]['lines']); break
    if 'City' in f: city = f['City']['text']
    if 'State' in f: state = f['State']['text']
    if 'Country' in f: country = f['Country']['text']
    if t and not web: notes.append('detail page had no website')
    row = {'Show ID': SID, 'Show Name': SHOW, 'Exhibitor Name': (f.get('Name') or {}).get('text') or e['name'], 'Booth': e['booth'],
           'Website': fix_url(web), 'LinkedIn': li, 'About': about, 'About Summary': summarize(about),
           'Categories': '; '.join(cats[:5]), 'City': city, 'State': state, 'Country': country, 'Detail URL': durl,
           'Source': LIST, 'List Status': 'current list', 'Notes': '; '.join(notes)}
    append_row(SID, row)
    if n % 25 == 0: log('detail', n, len(entries), row['Exhibitor Name'])
log('labels', labels)
rows = finalize(SID); log('FINAL', stats(rows))

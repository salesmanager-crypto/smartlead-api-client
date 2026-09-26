"""S12 IGES scraper. Roster = SmallWorldLabs directory (iges2026.smallworldlabs.com/exhibitors, paged via
in-browser POST, cached at cache/pages/S12/swl_list_*.html) + a2z list (iges.a2zinc.net Exhibitors.aspx, venue + booths).
Detail = SWL /co/<slug> pages via common.fetch. Writes raw/S12_exhibitors.csv incrementally (stage 1)."""
import csv, glob, html, json, os, re
from common import fetch, norm_name, domain_of

BASE = os.path.dirname(os.path.abspath(__file__))
SID, SNAME = 'S12', 'IGES, International Gift Exposition in the Smokies'
LIST_URL = 'https://iges2026.smallworldlabs.com/exhibitors'
A2Z_URL = 'https://iges.a2zinc.net/IGES2026/Public/Exhibitors.aspx?Index=All'
COLS = ['Show ID', 'Show Name', 'Exhibitor Name', 'Booth', 'Website', 'LinkedIn', 'About', 'About Summary', 'Categories',
        'City', 'State', 'Country', 'Detail URL', 'Source', 'List Status', 'Notes']
CD = os.path.join(BASE, 'cache', 'pages', SID)


def txt(v):
    v = re.sub(r'<script.*?</script>', '', v, flags=re.S)
    v = re.sub(r'<br\s*/?>', '\n', v)
    v = html.unescape(re.sub(r'<[^>]+>', '', v))
    v = v.replace('—', ' - ').replace('–', '-').replace('\xa0', ' ')
    lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in v.split('\n')]
    out = '\n'.join(lines)
    return re.sub(r'\n{3,}', '\n\n', out).strip()


def cat_options():
    h = fetch(LIST_URL)
    m = re.search(r'field_4:\{id:"4",label:"Categories".*?options:\{(.*?)\}', h, re.S)
    opts = [html.unescape(x) for x in re.findall(r'"\d+":"(.*?)"', m.group(1))]
    return sorted([o for o in opts if o != 'All Categories'], key=len, reverse=True)


def split_cats(s, opts):
    out, rest = [], s
    while rest:
        rest = rest.strip(' ,')
        if not rest: break
        for o in opts:
            if rest.startswith(o) and (len(rest) == len(o) or rest[len(o)] == ','):
                out.append(o); rest = rest[len(o):]; break
        else:
            part, _, rest = rest.partition(',')
            out.append(part.strip())
    return out


def roster():
    rows = []
    for p in sorted(glob.glob(os.path.join(CD, 'swl_list_*.html')), key=lambda x: int(re.findall(r'_(\d+)\.html', x)[0])):
        d = open(p).read()
        for tr in re.findall(r'<tr[ >].*?</tr>', d, re.S):
            if '<th' in tr: continue
            tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
            name = txt(tds[1]) if len(tds) > 1 else ''
            booth = re.sub(r'^Booth\s*#\s*', '', txt(tds[2])) if len(tds) > 2 else ''
            co = re.findall(r'href="(/co/[^"]+)"', tr)
            rows.append(dict(name=name, booth=booth, slug=co[0] if co else ''))
    by = {}
    for r in rows:
        k = norm_name(r['name'])
        e = by.setdefault(k, dict(name=r['name'], booths=[], slug=''))
        if r['booth'] and r['booth'] not in e['booths']: e['booths'].append(r['booth'])
        if r['slug'] and not e['slug']: e['slug'] = r['slug']
    a2z = json.load(open(os.path.join(CD, 'a2z_list.json')))
    for a in a2z:
        k = norm_name(a['name'])
        e = by.get(k)
        if e is None:
            e = by[k] = dict(name=a['name'], booths=[], slug='', a2z_only=True)
        if a['booth'] and a['booth'] not in e['booths']: e['booths'].append(a['booth'])
        e.setdefault('venues', [])
        if a['venue'] and a['venue'] not in e['venues']: e['venues'].append(a['venue'])
    return list(by.values())


def parse_detail(h):
    pairs = re.findall(r'<div class="text-secondary">\s*(.*?)\s*</div>\s*</div>\s*<div class="col-8">\s*<div class="profileResponse">(.*?)</div>\s*</div>\s*</div>', h, re.S)
    f = {}
    for k, v in pairs:
        k = txt(k)
        if k not in f: f[k] = (v, txt(v))
    return f


def main():
    opts = cat_options()
    ros = roster()
    print('roster', len(ros), 'with slug', sum(1 for r in ros if r['slug']), flush=True)
    out = os.path.join(BASE, 'raw', f'{SID}_exhibitors.csv')
    done = set()
    if os.path.exists(out):
        with open(out, encoding='utf-8') as f:
            done = {norm_name(r['Exhibitor Name']) for r in csv.DictReader(f)}
    new = not os.path.exists(out)
    fh = open(out, 'a', newline='', encoding='utf-8'); w = csv.DictWriter(fh, fieldnames=COLS)
    if new: w.writeheader()
    for i, r in enumerate(sorted(ros, key=lambda x: x['name'].lower())):
        if norm_name(r['name']) in done: continue
        row = {c: '' for c in COLS}
        row.update({'Show ID': SID, 'Show Name': SNAME, 'Exhibitor Name': r['name'], 'Booth': '; '.join(r['booths']),
                    'Source': LIST_URL, 'List Status': 'current list'})
        notes = []
        if r.get('venues'): notes.append('Venue: ' + ' / '.join(r['venues']))
        if r['slug']:
            url = 'https://iges2026.smallworldlabs.com' + r['slug']
            h = fetch(url)
            row['Detail URL'] = url
            if h:
                f = parse_detail(h)
                raw_name = f.get('Name', (None, ''))[1]
                if raw_name: row['Exhibitor Name'] = raw_name
                web = f.get('Website')
                if web:
                    m = re.search(r'href="([^"]+)"', web[0]); row['Website'] = html.unescape(m.group(1)) if m else web[1]
                li = f.get('LinkedIn')
                if li:
                    m = re.search(r'href="([^"]*linkedin\.com/company/[^"]*)"', li[0])
                    if m: row['LinkedIn'] = html.unescape(m.group(1)).split('?')[0]
                if not row['LinkedIn']:
                    m = re.search(r'href="(https?://[^"]*linkedin\.com/company/[^"]*)"', h)
                    if m: row['LinkedIn'] = html.unescape(m.group(1)).split('?')[0]
                row['About'] = f.get('What We Do', (None, ''))[1]
                cats = split_cats(f.get('Categories', (None, ''))[1], opts) if f.get('Categories') else []
                row['Categories'] = '; '.join(cats[:5])
                addr = [l.strip() for l in f.get('Address', (None, ''))[1].split('\n') if l.strip()]
                if addr:
                    m = re.match(r'^(.*?),\s*([A-Za-z .]+?)(?:\s+[\d-]+)?$', addr[0])
                    if len(addr) >= 2:
                        row['Country'] = addr[-1]
                    if m and len(addr) >= 1:
                        row['City'], row['State'] = m.group(1).strip(), m.group(2).strip()
                    elif len(addr) == 1:
                        row['Country'] = addr[0]
                extra = []
                for k in ('Pavilions', 'Exhibitor Identification', 'New Exhibitor', 'Founded'):
                    if f.get(k) and f[k][1]: extra.append(f'{k}: ' + f[k][1].replace('\n', ', '))
                notes += extra
                if not row['Website']: notes.append('detail page had no website')
                if not row['About']: notes.append('detail page had no description')
            else:
                notes.append('detail page failed to load')
        else:
            notes.append('no SWL profile page linked; listed in ' + ('a2z list only' if r.get('a2z_only') else 'directory without profile link'))
        row['Notes'] = '; '.join(notes)
        w.writerow(row); fh.flush()
        if i % 25 == 0: print(i, len(ros), r['name'], flush=True)
    fh.close()
    print('DONE', flush=True)


if __name__ == '__main__':
    main()

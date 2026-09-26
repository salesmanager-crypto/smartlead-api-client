"""S10 High Point Market (Fall 2026) exhibitor directory scraper.
Phases: list pages -> category filters -> country filters -> detail pages (CSV written incrementally).
All HTTP via common.fetch (polite + cached)."""
import csv, json, os, re, sys, html as H, urllib.parse as up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch, norm_name, domain_of

SID = 'S10'
SHOW = 'High Point Market, Fall 2026'
BASE_URL = 'https://www.highpointmarket.org'
LIST_URL = BASE_URL + '/ExhibitorDirectory'
OUT_CSV = os.path.join('raw', f'{SID}_exhibitors.csv')
OUT_META = os.path.join('raw', f'{SID}_meta.json')
STATE = os.path.join('cache', 'pages', SID, 'state.json')
COLS = ['Show ID', 'Show Name', 'Exhibitor Name', 'Booth', 'Website', 'LinkedIn', 'About', 'About Summary',
        'Categories', 'City', 'State', 'Country', 'Detail URL', 'Source', 'List Status', 'Notes']


def log(*a):
    print(*a, flush=True)


def txt(s):
    s = re.sub(r'<br\s*/?>', '\n', s or '', flags=re.I)
    s = re.sub(r'</p>\s*<p[^>]*>', '\n\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = H.unescape(s).replace('\xa0', ' ')
    s = s.replace('—', ', ').replace('–', '-')
    s = re.sub(r'[ \t\r\f\v]+', ' ', s)
    s = re.sub(r' *\n *', '\n', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()


def dir_url(page, filt=None):
    u = BASE_URL + f'/exhibitordirectory?pageindex={page}'
    if filt:
        u += '&filters=' + up.quote(json.dumps(filt, separators=(',', ':')))
    return u


def parse_list(h):
    """returns list of (id, name, location_text, neighborhood), total_pages"""
    rows = []
    for blk in re.split(r'<div class="d-flex flex-column exhibitor-block', h)[1:]:
        m = re.search(r'<h2><a href="/exhibitor/(\d+)"[^>]*>(.*?)</a></h2>', blk, re.S)
        if not m:
            continue
        loc = re.search(r'<span class="d-flex flex-row">(.*?)</span>', blk, re.S)
        nb = re.search(r'class="neighborhood">(.*?)</span>', blk, re.S)
        rows.append((m.group(1), txt(m.group(2)), txt(loc.group(1)) if loc else '', txt(nb.group(1)) if nb else ''))
    tp = re.search(r'PAGINATION_TOTAL\s*=\s*(\d+)', h)
    if tp:
        total = int(tp.group(1))
    else:
        pg = [int(x) for x in re.findall(r'pageindex=(\d+)', h)]
        total = max(pg) if pg else 1
    return rows, total


def crawl_filter(filt, label):
    ids = []
    page, total = 1, 1
    while page <= total:
        h = fetch(dir_url(page, filt))
        if not h:
            log('  fail', label, page); break
        rows, total = parse_list(h)
        ids += [r[0] for r in rows]
        if not rows:
            break
        page += 1
    return ids


def summarize(about):
    if not about:
        return ''
    a = re.sub(r'\s+', ' ', about).strip()
    sents = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"“])', a)
    out = sents[0]
    if len(out) < 90 and len(sents) > 1:
        out += ' ' + sents[1]
    if len(out) > 300:
        cut = out[:300].rsplit(' ', 1)[0].rstrip(',;:')
        out = cut + '...'
    return out.replace('—', ', ')


def parse_detail(h):
    d = {}
    ib = re.search(r'<div class="info-block">(.*?)<div class="col-md-8">', h, re.S)
    ib = ib.group(1) if ib else ''
    p1 = re.search(r'<p>(.*?)</p>', ib, re.S)
    locs, extra = [], {}
    if p1:
        for m in re.finditer(r'<span class="d-flex flex-row">(.*?</span>)\s*</span>', p1.group(1), re.S):
            for s in re.findall(r'<span>(.*?)</span>', m.group(1), re.S):
                if txt(s):
                    locs.append(txt(s))
        for s in re.findall(r'<span>([^<]*?:[^<]*)</span>', p1.group(1)):
            k, v = s.split(':', 1)
            extra[txt(k)] = txt(v)
    d['locs'] = locs
    d['neighborhood'] = extra.get('Neighborhood', '')
    socials = re.findall(r'<a href="([^"]+)"[^>]*class="(\w+)"', ib)
    li = [u for u, c in socials if 'linkedin.com/company' in u.lower()]
    d['linkedin'] = li[0].strip() if li else ''
    d['linkedin_other'] = [u for u, c in socials if 'linkedin' in u.lower() and 'linkedin.com/company' not in u.lower()]
    web = ''
    for m in re.finditer(r'<p>\s*<a href="([^"]+)" target="_blank">([^<]*)</a>\s*</p>', ib):
        web = m.group(1).strip()
    d['website'] = web
    nm = re.search(r'<div class="exhibitor-contain">\s*<h1>(.*?)</h1>', h, re.S)
    d['name'] = txt(nm.group(1)) if nm else ''
    ww = re.search(r'id="whoweare" role="tabpanel"[^>]*>(.*?)<div class="tab-pane', h, re.S)
    if not ww:
        ww = re.search(r'id="whoweare" role="tabpanel"[^>]*>(.*?)</section>', h, re.S)
    d['about'] = txt(ww.group(1)) if ww else ''
    br = re.search(r'id="brands" role="tabpanel"[^>]*>(.*?)<div class="tab-pane', h, re.S)
    d['linked'] = [txt(x) for x in re.findall(r'<a href="/exhibitor/\d+"[^>]*>(.*?)</a>', br.group(1), re.S)] if br else []
    d['linked'] = [x for x in d['linked'] if x]
    return d


def main():
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    # Phase 1: main list
    if 'list' not in st:
        items, page, total = [], 1, 1
        while page <= total:
            h = fetch(dir_url(page))
            if not h:
                log('list page fail', page); page += 1; continue
            rows, total = parse_list(h)
            items += rows
            if page % 20 == 0:
                log('list page', page, '/', total, len(items))
            page += 1
        st['list'] = items; st['list_pages'] = total
        json.dump(st, open(STATE, 'w'))
    log('list rows', len(st['list']), 'pages', st['list_pages'])
    # filters from page 1
    h1 = fetch(dir_url(1))
    fs = [json.loads(H.unescape(x)) for x in dict.fromkeys(re.findall(r'data-filter="([^"]+)"', h1))]
    tops = list(dict.fromkeys(f['Values'][0] for f in fs if f['Type'] == 'Categories'))
    countries = [f['Values'][0] for f in fs if f['Type'] == 'Country']
    # Phase 2: categories (top level)
    st.setdefault('cats', {})
    for c in tops:
        if c in st['cats']:
            continue
        st['cats'][c] = crawl_filter({'Type': 'Categories', 'Values': [c]}, c)
        log('cat', c, len(st['cats'][c]))
        json.dump(st, open(STATE, 'w'))
    # Phase 3: countries
    st.setdefault('countries', {})
    for c in countries:
        if c in st['countries']:
            continue
        st['countries'][c] = crawl_filter({'Type': 'Country', 'Values': [c]}, c)
        log('country', c, len(st['countries'][c]))
        json.dump(st, open(STATE, 'w'))
    cat_of, ctry_of = {}, {}
    for c, ids in st['cats'].items():
        for i in ids:
            cat_of.setdefault(i, [])
            if c not in cat_of[i]:
                cat_of[i].append(c)
    for c, ids in st['countries'].items():
        for i in ids:
            ctry_of.setdefault(i, [])
            if c not in ctry_of[i]:
                ctry_of[i].append(c)
    # Phase 4: detail pages -> CSV (incremental)
    done = set()
    if os.path.exists(OUT_CSV):
        with open(OUT_CSV, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                done.add(r['Detail URL'])
    seen = {}
    uniq = []
    for eid, name, loc, nb in st['list']:
        if eid in seen:
            seen[eid][2].append(loc) if loc and loc not in seen[eid][2] else None
            continue
        seen[eid] = [eid, name, [loc] if loc else [], nb]
        uniq.append(seen[eid])
    log('unique exhibitor ids', len(uniq), 'already written', len(done))
    newfile = not os.path.exists(OUT_CSV)
    f = open(OUT_CSV, 'a', newline='', encoding='utf-8')
    w = csv.DictWriter(f, fieldnames=COLS)
    if newfile:
        w.writeheader()
    for n, (eid, name, locs, nb) in enumerate(uniq):
        durl = f'{BASE_URL}/exhibitor/{eid}'
        if durl in done:
            continue
        h = fetch(durl)
        notes = []
        d = parse_detail(h) if h else {}
        if not h:
            notes.append('detail page failed to load')
        booth_locs = d.get('locs') or locs
        booth = ' | '.join(dict.fromkeys(booth_locs))
        cats = cat_of.get(eid, [])
        if len(cats) > 5:
            notes.append(f'{len(cats)} top-level categories listed; first 5 kept')
        ctry = ctry_of.get(eid, [])
        if h and not d.get('website'):
            notes.append('detail page had no website')
        if h and not d.get('about'):
            notes.append('detail page had no description')
        if d.get('linked'):
            notes.append('Linked profiles: ' + '; '.join(d['linked'][:10]))
        if d.get('linkedin_other') and not d.get('linkedin'):
            notes.append('LinkedIn link is not a company page: ' + d['linkedin_other'][0])
        about = d.get('about', '')
        w.writerow({
            'Show ID': SID, 'Show Name': SHOW, 'Exhibitor Name': d.get('name') or name, 'Booth': booth,
            'Website': d.get('website', ''), 'LinkedIn': d.get('linkedin', ''), 'About': about,
            'About Summary': summarize(about), 'Categories': '; '.join(cats[:5]), 'City': '', 'State': '',
            'Country': '; '.join(ctry), 'Detail URL': durl, 'Source': LIST_URL, 'List Status': 'current list',
            'Notes': '. '.join(notes)})
        f.flush()
        if n % 50 == 0:
            log('detail', n, '/', len(uniq), name)
    f.close()
    log('DONE details')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()

"""S02 White & Private Label World Expo, New York 2026 (ASP events platform). List page + detail pages."""
import csv, json, os, re, sys, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch, norm_name, domain_of

SID = 'S02'
SHOW = 'White & Private Label World Expo'
BASE = 'https://www.whitelabelexpo.com'
LIST_URL = BASE + '/ny-exhibitors'
OUT_CSV = os.path.join('raw', f'{SID}_exhibitors.csv')
OUT_META = os.path.join('raw', f'{SID}_meta.json')
COLS = ['Show ID', 'Show Name', 'Exhibitor Name', 'Booth', 'Website', 'LinkedIn', 'About', 'About Summary',
        'Categories', 'City', 'State', 'Country', 'Detail URL', 'Source', 'List Status', 'Notes']
US_STATES = set('AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC PR'.split())
CA_PROV = set('AB BC MB NB NL NS NT NU ON PE QC SK YT'.split())
STATE_NAMES = {'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware', 'florida', 'georgia',
               'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts',
               'michigan', 'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire', 'new jersey',
               'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode island',
               'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia',
               'wisconsin', 'wyoming', 'ontario', 'quebec', 'british columbia', 'alberta', 'manitoba', 'nova scotia', 'zhejiang',
               'guangdong', 'henan', 'jiangsu', 'shandong', 'fujian', 'gujarat', 'maharashtra', 'florida'}


def txt(s):
    s = re.sub(r'<br\s*/?>', '\n', s or '', flags=re.I)
    s = re.sub(r'</p>\s*<p[^>]*>', '\n\n', s, flags=re.I)
    s = re.sub(r'</li>\s*', '\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = H.unescape(s).replace('\xa0', ' ')
    s = s.replace('—', ', ').replace('–', '-')
    s = re.sub(r'[ \t\r\f\v]+', ' ', s)
    s = re.sub(r' *\n *', '\n', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()


def summarize(about):
    if not about:
        return ''
    a = re.sub(r'\s+', ' ', about).strip()
    sents = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"“])', a)
    out = sents[0]
    if len(out) < 90 and len(sents) > 1:
        out += ' ' + sents[1]
    if len(out) > 300:
        out = out[:300].rsplit(' ', 1)[0].rstrip(',;:') + '...'
    return out


def parse_list(h):
    out = []
    for art in re.findall(r'<article class="m-exhibitors-list__list__items__item.*?</article>', h, re.S):
        nm = re.search(r'__header__title__link[^>]*href="([^"]+)"[^>]*>(.*?)</a>', art, re.S)
        stand = re.search(r'__header__meta__stand[^>]*>(.*?)</span>', art, re.S)
        cats = re.search(r'__body__categories">(.*?)</div>', art, re.S)
        ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', art, re.S)
        out.append({
            'href': nm.group(1) if nm else '', 'name': txt(nm.group(2)) if nm else '',
            'stand': re.sub(r'^Stand:\s*', '', txt(stand.group(1))) if stand else '',
            'cats': [txt(c) for c in re.findall(r'<(?:li|span)[^>]*>(.*?)</(?:li|span)>', cats.group(1), re.S)] if cats else [],
            'ld': json.loads(ld.group(1)).get('mainEntity', {}) if ld else {}})
    return out


def parse_detail(h):
    d = {}
    st = re.search(r'm-exhibitor-entry__item__header__stand[^>]*>(.*?)</', h, re.S)
    d['stand'] = re.sub(r'^Stand:\s*', '', txt(st.group(1))) if st else ''
    ds = re.search(r'<section class="m-exhibitor-entry__item__body__description[^"]*"[^>]*>(.*?)</section>', h, re.S)
    adn = re.search(r'<section class="m-exhibitor-entry__item__body__additional">(.*?)</section>', h, re.S)
    d['additional'] = txt(adn.group(1)) if adn else ''
    d['about'] = txt(ds.group(1)) if ds else ''
    ad = re.search(r'<address class="m-exhibitor-entry__item__body__contacts__address"[^>]*>(.*?)</address>', h, re.S)
    lines = []
    if ad:
        body = re.sub(r'<h4>.*?</h4>', '', ad.group(1), flags=re.S)
        for ln in body.split('\n'):
            ln = ln.rstrip('\r')
            v = H.unescape(re.sub(r'<br\s*/?>', '', ln)).strip()
            if v:
                lines.append((len(ln) - len(ln.lstrip('\t')), v))
    d['addr_lines'] = lines
    soc = re.search(r'<ul class="m-exhibitor-entry__item__body__contacts__additional__social">(.*?)</ul>', h, re.S)
    d['socials'] = re.findall(r'href="([^"]+)"', soc.group(1)) if soc else []
    web = re.search(r'aria-label="Visit website" href="([^"]+)"', h)
    d['website'] = web.group(1).strip() if web else ''
    ld = re.search(r'<script type="application/ld\+json">(\{"@context":"https://schema.org","@type":"ProfilePage".*?)</script>', h, re.S)
    d['ld'] = json.loads(ld.group(1)).get('mainEntity', {}) if ld else {}
    return d


def split_addr(lines, ld):
    """lines = [(indent, text)]. The ASP template indents street lines one tab deeper than city/state/postal/country."""
    a = ld.get('address', {}) or {}
    postal, country = (a.get('postalCode') or '').strip(), (a.get('addressCountry') or '').strip()
    if not lines:
        return '', '', country, ''
    base = min(i for i, _ in lines)
    slots = [t for i, t in lines if i == base]
    if slots and country and slots[-1] == country:
        slots = slots[:-1]
    elif slots and not country:
        country = slots[-1]; slots = slots[:-1]
    if slots and postal and slots[-1] == postal:
        slots = slots[:-1]
    slots = [x.strip().rstrip(',').strip() for x in slots]
    city = state = ''
    if len(slots) >= 2:
        city, state = slots[-2], slots[-1]
    elif len(slots) == 1:
        r = slots[0]
        if r.upper() in US_STATES | CA_PROV or r.lower() in STATE_NAMES:
            state = r
        else:
            city = r
    note = ''
    if re.match(r'^\d', city):
        note = 'city field on profile holds a street address (' + city + '); left blank'
        city = ''
    return city, state, country, note


def main():
    h = fetch(LIST_URL)
    items = parse_list(h)
    print('list items', len(items))
    rows, seen = [], {}
    done = {}
    if os.path.exists(OUT_CSV):
        with open(OUT_CSV, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                done[r['Detail URL']] = r
    for it in items:
        durl = BASE + '/' + it['href'].lstrip('/') if not it['href'].startswith('http') else it['href']
        if durl in done:
            rows.append(done[durl]); continue
        dh = fetch(durl)
        d = parse_detail(dh) if dh else {'ld': {}, 'addr_lines': [], 'socials': [], 'website': '', 'about': '', 'stand': ''}
        ld = d['ld'] or it['ld']
        notes = []
        if not dh:
            notes.append('detail page failed to load; used list data')
        about = d['about'] or txt(ld.get('description', ''))
        website = d['website'] or ld.get('url', '') or it['ld'].get('url', '')
        if 'whitelabelexpo.com' in website:
            website = ''
        website = re.sub(r'[?&]srsltid=[^&]*$', '', website)
        socials = d['socials'] + list(ld.get('sameAs', []) or [])
        li = [u for u in socials if 'linkedin.com/company' in u.lower()]
        li_other = [u for u in socials if 'linkedin' in u.lower() and 'linkedin.com/company' not in u.lower()]
        city, state, country, anote = split_addr(d['addr_lines'], ld)
        if anote:
            notes.append(anote)
        booth = d['stand'] or it['stand']
        if not booth:
            notes.append('no stand number shown')
        if not website:
            notes.append('detail page had no website')
        if not about:
            notes.append('no description on profile')
        if li_other and not li:
            notes.append('LinkedIn link is not a company page: ' + li_other[0])
        if d.get('additional'):
            notes.append('Profile extra info: ' + d['additional'].replace('\n', ' / ')[:300])
        rows.append({'Show ID': SID, 'Show Name': SHOW, 'Exhibitor Name': it['name'] or ld.get('name', ''), 'Booth': booth,
                     'Website': website, 'LinkedIn': li[0] if li else '', 'About': about, 'About Summary': summarize(about),
                     'Categories': '; '.join(it['cats'][:5]), 'City': city, 'State': state, 'Country': country,
                     'Detail URL': durl, 'Source': LIST_URL, 'List Status': 'current list', 'Notes': '. '.join(notes)})
        # checkpoint
        with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
    print('rows', len(rows))


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()

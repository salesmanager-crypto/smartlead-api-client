import sys, os, csv, json, re, html
sys.path.insert(0, '/home/user/smartlead-api-client/tradeshow_pipeline')
from common import norm_name, domain_of
BASE = '/home/user/smartlead-api-client/tradeshow_pipeline'
RAW = os.path.join(BASE, 'raw')
COLS = ['Show ID','Show Name','Exhibitor Name','Booth','Website','LinkedIn','About','About Summary','Categories','City','State','Country','Detail URL','Source','List Status','Notes']
def clean(s):
    if s is None: return ''
    s = str(s).replace('—', ' - ').replace('–', '-').replace('\xa0', ' ')
    s = re.sub(r'[ \t\r\f\v]+', ' ', s)
    s = re.sub(r'\s*\n\s*', '\n', s)
    return s.strip()
def strip_html(s):
    if not s: return ''
    s = re.sub(r'(?i)<br\s*/?>|</p>|</li>|</div>', '\n', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    return clean(html.unescape(s))
def summarize(about):
    a = clean(about).replace('\n', ' ')
    a = re.sub(r'\s+', ' ', a).strip()
    if not a: return ''
    sents = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"])', a)
    out = sents[0]
    if len(out) < 80 and len(sents) > 1: out += ' ' + sents[1]
    if len(out) > 280:
        out = out[:280].rsplit(' ', 1)[0].rstrip(',;:') + '...'
    return out
def linkedin_ok(u):
    u = (u or '').strip()
    return u if re.search(r'linkedin\.com/(company|showcase|school)/', u, re.I) else ''
def fix_url(u):
    u = (u or '').strip()
    if not u: return ''
    if not re.match(r'^https?://', u, re.I): u = 'http://' + u.lstrip('/')
    return u
def csv_path(sid): return os.path.join(RAW, f'{sid}_exhibitors.csv')
def read_rows(sid):
    p = csv_path(sid)
    if not os.path.exists(p): return []
    with open(p, encoding='utf-8', newline='') as f: return list(csv.DictReader(f))
def append_row(sid, row):
    p = csv_path(sid); new = not os.path.exists(p)
    with open(p, 'a', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new: w.writeheader()
        w.writerow({k: clean(row.get(k, '')) for k in COLS})
def richness(r): return sum(1 for k in COLS if r.get(k))
def finalize(sid, rows=None):
    rows = rows if rows is not None else read_rows(sid)
    groups = []; idx = {}
    for r in rows:
        r = {k: clean(r.get(k, '')) for k in COLS}
        if not r['About Summary'] and r['About']: r['About Summary'] = summarize(r['About'])
        keys = []
        nn = norm_name(r['Exhibitor Name']);
        if nn: keys.append('n:' + nn)
        d = domain_of(r['Website'])
        if d and d not in ('facebook.com','instagram.com','linkedin.com'): keys.append('d:' + d)
        gi = next((idx[k] for k in keys if k in idx), None)
        if gi is None:
            groups.append(r); gi = len(groups) - 1
        else:
            g = groups[gi]
            base, other = (r, g) if richness(r) > richness(g) else (g, r)
            m = dict(base)
            for k in COLS:
                if not m.get(k) and other.get(k): m[k] = other[k]
            bs = [b for b in dict.fromkeys((g['Booth'] + ', ' + r['Booth']).split(', ')) if b]
            m['Booth'] = ', '.join(bs)
            if norm_name(g['Exhibitor Name']) != norm_name(r['Exhibitor Name']):
                o = other['Exhibitor Name']; extra = 'also listed as %s (same website, merged)' % o
                if o and extra not in m['Notes']: m['Notes'] = '; '.join(x for x in [m['Notes'], extra] if x)
            groups[gi] = m
        for k in keys: idx[k] = gi
    groups.sort(key=lambda r: r['Exhibitor Name'].lower())
    with open(csv_path(sid), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
        for r in groups: w.writerow(r)
    return groups
def write_meta(sid, show_name, status, url, platform, n, notes):
    with open(os.path.join(RAW, f'{sid}_meta.json'), 'w', encoding='utf-8') as f:
        json.dump({'show_id': sid, 'show_name': show_name, 'list_status': status, 'exhibitor_list_url': url,
                   'platform': platform, 'exhibitors': n, 'notes': clean(notes)}, f, indent=1, ensure_ascii=False)
def stats(rows):
    return dict(n=len([r for r in rows if r['Exhibitor Name']]), web=sum(1 for r in rows if r['Website']),
                li=sum(1 for r in rows if r['LinkedIn']), about=sum(1 for r in rows if r['About']))

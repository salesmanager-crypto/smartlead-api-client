"""Post-process raw/S10_exhibitors.csv: dedupe, flag social-media 'websites', write meta."""
import csv, json, os, re, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')
from common import norm_name, domain_of
from scrape_S10 import COLS, OUT_CSV, OUT_META, SID, SHOW, LIST_URL

rows = list(csv.DictReader(open(OUT_CSV, encoding='utf-8')))
SOCIAL = re.compile(r'(instagram|facebook|pinterest|twitter|x\.com|tiktok|youtube|linkedin)\.com', re.I)
for r in rows:
    for k in COLS:
        r[k] = (r.get(k) or '').replace('—', ', ')
    if r['Website'] and SOCIAL.search(r['Website']):
        n = 'website field on profile is a social media link'
        if n not in r['Notes']:
            r['Notes'] = (r['Notes'] + '. ' if r['Notes'] else '') + n
    if not r['Categories']:
        n = 'no category filter matched this exhibitor'
        if n not in r['Notes']:
            r['Notes'] = (r['Notes'] + '. ' if r['Notes'] else '') + n


def richness(r):
    return sum(1 for k in ('Website', 'LinkedIn', 'About', 'Categories', 'Country', 'Booth') if r[k])


out, idx = [], {}
for r in rows:
    keys = [('n', norm_name(r['Exhibitor Name']))]
    d = domain_of(r['Website'])
    if d and not SOCIAL.search(d):
        keys.append(('d', d))
    hit = next((idx[k] for k in keys if k in idx), None)
    if hit is None:
        out.append(r)
        for k in keys:
            idx[k] = len(out) - 1
        continue
    a = out[hit]
    if keys[0] != ('n', norm_name(a['Exhibitor Name'])):
        # same domain, different name: separate brands of one company; keep both rows
        out.append(r)
        idx[keys[0]] = len(out) - 1
        continue
    best, other = (a, r) if richness(a) >= richness(r) else (r, a)
    for k in COLS:
        if not best[k] and other[k]:
            best[k] = other[k]
    if other['Booth'] and other['Booth'] not in best['Booth']:
        best['Booth'] += ' | ' + other['Booth']
    best['Notes'] = (best['Notes'] + '. ' if best['Notes'] else '') + 'merged duplicate profile ' + other['Detail URL']
    out[hit] = best

with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(out)

c = lambda k: sum(1 for r in out if r[k])
meta = {
    'show_id': SID, 'show_name': SHOW, 'list_status': 'current list', 'exhibitor_list_url': LIST_URL,
    'platform': 'custom (highpointmarket.org ASP.NET directory, server-rendered, 10 per page)',
    'exhibitors': len(out),
    'notes': (f'Full Fall 2026 directory, all buildings: {len(rows)} exhibitor profiles over 175 list pages '
              '(highpointmarket.org/exhibitordirectory?pageindex=N; /api/exhibitors/autocomplete gives the same 1,743 names and IDs). '
              'Every profile page (/exhibitor/<id>) was opened for showroom location, website, LinkedIn, and the Who We Are text (About). '
              'Booth = building/address + showroom space and floor as shown. '
              'Categories: the site does not show categories on profiles, so they come from re-crawling the directory with each of the 26 top-level '
              'category filters; when an exhibitor is in more than 5, the first 5 in alphabetical filter order are kept (noted per row). '
              'Country comes from the directory Country filter; City and State are not shown anywhere (the showroom is in High Point, not the company HQ), so they are blank. '
              'About Summary is an extractive 1 to 2 sentence summary of the About text. '
              f'Counts: website {c("Website")}, LinkedIn company page {c("LinkedIn")}, About {c("About")}, categories {c("Categories")}, country {c("Country")}. '
              'Some Website values are Instagram or other social links as entered by the exhibitor (flagged in Notes). '
              'Many rows are multi-line showrooms or galleries (e.g. 200 Steele, 313.Space); their Notes list the linked brand profiles.')}
json.dump(meta, open(OUT_META, 'w'), indent=1, ensure_ascii=False)
print(json.dumps(meta, indent=1))

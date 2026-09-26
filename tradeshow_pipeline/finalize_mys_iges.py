"""Stage 2 for S03/S14/S16/S19 (MapYourShow) and S12 (IGES): dedupe, merge, add About Summary, write meta.
Summaries come from a JSON store keyed by sha1(About)[:10] (written by the worker, not generated here).
Usage: python3 finalize_mys_iges.py <summary_dir> S03 S14 ..."""
import csv, glob, hashlib, json, os, re, sys
from common import norm_name, domain_of

BASE = os.path.dirname(os.path.abspath(__file__))
COLS = ['Show ID', 'Show Name', 'Exhibitor Name', 'Booth', 'Website', 'LinkedIn', 'About', 'About Summary', 'Categories',
        'City', 'State', 'Country', 'Detail URL', 'Source', 'List Status', 'Notes']
GENERIC = {'gmail.com', 'yahoo.com', 'hotmail.com', 'facebook.com', 'instagram.com', 'linktr.ee', 'etsy.com', 'outlook.com',
           'aol.com', 'icloud.com', 'linkedin.com', 'twitter.com', 'x.com', 'tiktok.com', 'youtube.com', 'shopify.com', 'amazon.com'}
MYS = {'S03': 'lv1026', 'S14': 'smg1126', 'S16': 'ocg1126', 'S19': 'gsr1226'}


def nodash(s):
    return (s or '').replace('—', ' - ').replace('–', '-')


def rich(r):
    return sum(bool(r[c].strip()) for c in ('Website', 'LinkedIn', 'About', 'Booth', 'Categories', 'City'))


def merge(a, b):
    keep, other = (a, b) if rich(a) >= rich(b) else (b, a)
    out = dict(keep)
    for c in COLS:
        if not out[c].strip() and other[c].strip():
            out[c] = other[c]
    if other['Booth'] and other['Booth'] != out['Booth']:
        bs = [x for x in (out['Booth'] + '; ' + other['Booth']).split('; ') if x]
        out['Booth'] = '; '.join(dict.fromkeys(bs))
    return out


def main(sumdir, sids):
    summ = {}
    for f in glob.glob(os.path.join(sumdir, 'batch_*.json')):
        summ.update(json.load(open(f)))
    for sid in sids:
        p = os.path.join(BASE, 'raw', f'{sid}_exhibitors.csv')
        rows = list(csv.DictReader(open(p, encoding='utf-8')))
        raw_n = len(rows)
        merged, by_n, by_d = [], {}, {}
        for r in rows:
            r = {c: nodash(r.get(c, '')) for c in COLS}
            n = norm_name(r['Exhibitor Name']); d = domain_of(r['Website'])
            d = d if d and d not in GENERIC else ''
            idx = by_n.get(n)
            if idx is None and d: idx = by_d.get(d)
            if idx is None:
                merged.append(r); idx = len(merged) - 1
            else:
                merged[idx] = merge(merged[idx], r)
            by_n.setdefault(n, idx)
            if d: by_d.setdefault(d, idx)
        missing = 0
        for r in merged:
            a = r['About'].strip()
            if a:
                k = hashlib.sha1(a.encode()).hexdigest()[:10]
                s = summ.get(k, '')
                if not s:
                    # About text changed by nodash; try original key
                    missing += 1
                r['About Summary'] = nodash(s)
            else:
                r['About Summary'] = ''
            if sid in MYS and not r['Website'] and not a and not r['Categories']:
                notes = [x for x in r['Notes'].split('; ') if x and x not in ('detail page had no website', 'detail page had no description')]
                r['Notes'] = '; '.join(['detail page shows name and booth only (no website, description or categories)'] + notes)
        merged.sort(key=lambda r: r['Exhibitor Name'].lower())
        with open(p, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(merged)
        n = len(merged)
        cnt = lambda c: sum(1 for r in merged if r[c].strip())
        print(sid, 'raw rows', raw_n, '-> exhibitors', n, '| website', cnt('Website'), '| linkedin', cnt('LinkedIn'),
              '| about', cnt('About'), '| summary missing', missing, '| booth', cnt('Booth'), '| city', cnt('City'))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])

"""Phase 4 savers.
profile: python3 p4_save.py profile <batch_index> <out.jsonl>  stdin lines:
  Brand Name|Primary Category|Primary Subcategory|Total Monthly Revenue|Trailing 12-Month Revenue|Total Products|Total Reviews|Average Rating|Average Price|Average Sellers|Has Storefront|Average Amazon Revenue %|Average MoM Growth|Has Single Seller|Single Seller Name
brand:   python3 p4_save.py brand "<brand name>" <out.jsonl>  stdin: a line 'SELLERS' then lines Seller Name|Number of Offers|Brand Revenue Estimate|Estimated Brand Share|Month Over Month Change,
         then a line 'SUBCATS' then lines Sub Category Context|Marketshare|Revenue|Subcategory Rank   (sections may be empty)"""
import sys, json, os, datetime
kind, key, out = sys.argv[1], sys.argv[2], sys.argv[3]
now = datetime.datetime.utcnow().isoformat(timespec='seconds')
def num(x):
    x = (x or '').strip()
    if x.lower() in ('true', 'false'): return x.lower() == 'true'
    try: return float(x)
    except ValueError: return x if x else None
if os.path.exists(out):
    for l in open(out):
        if json.loads(l).get('key') == key: print(f'{key} already saved'); sys.exit(0)
lines = [l.rstrip('\n') for l in sys.stdin.read().strip().splitlines() if l.strip()]
if kind == 'profile':
    F = ['Brand Name','Primary Category','Primary Subcategory','Total Monthly Revenue','Trailing 12-Month Revenue','Total Products','Total Reviews','Average Rating','Average Price','Average Sellers','Has Storefront','Average Amazon Revenue %','Average MoM Growth','Has Single Seller','Single Seller Name']
    rows = []
    for l in lines:
        p = [x.strip() for x in l.split('|')]
        if len(p) != len(F): print('BAD FIELD COUNT', len(p), l[:80]); sys.exit(1)
        rows.append({f: (p[i] if i in (0, 1, 2, 14) else num(p[i])) for i, f in enumerate(F)})
    rec = {'key': key, 'kind': 'profile', 'batch': int(key), 'queried': json.load(open('phase4_work/profile_batches.json'))[int(key)], 'rows': rows, 'pulled_at': now}
else:
    sec, sellers, subs = None, [], []
    for l in lines:
        if l.strip() in ('SELLERS', 'SUBCATS'): sec = l.strip(); continue
        p = [x.strip() for x in l.split('|')]
        if sec == 'SELLERS' and len(p) == 5: sellers.append({'Seller Name': p[0], 'Number of Offers': num(p[1]), 'Brand Revenue Estimate': num(p[2]), 'Estimated Brand Share': num(p[3]), 'Month Over Month Change': num(p[4])})
        elif sec == 'SUBCATS' and len(p) == 4: subs.append({'Subcategory': p[0], 'Marketshare': num(p[1]), 'Revenue': num(p[2]), 'Rank': num(p[3])})
        else: print('BAD LINE', sec, l[:80]); sys.exit(1)
    rec = {'key': key, 'kind': 'brand', 'sellers': sellers, 'subcats': subs, 'pulled_at': now}
open(out, 'a').write(json.dumps(rec) + '\n')
print('saved', kind, key, len(rec.get('rows', rec.get('sellers', []))), len(rec.get('subcats', [])))

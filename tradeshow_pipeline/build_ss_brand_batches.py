"""Collect brands from phase3_work/brands_out_*.csv, make SmartScout batches for names not yet queried.
round=1: brand names as written. round=2: up to 2 variants (worker variants first, then auto) for brands with no hit yet."""
import pandas as pd, glob, json, re, sys
rnd = int(sys.argv[1]) if __name__ == '__main__' else 0
b = pd.concat([pd.read_csv(f, dtype=str).fillna('') for f in sorted(glob.glob('phase3_work/brands_out_*.csv'))])
b = b[b['Brand'].str.strip() != '']
queried, hits = set(), set()
for f in glob.glob('phase3_work/ss_*.jsonl'):
    for l in open(f):
        r = json.loads(l); queried |= {q.lower() for q in r['queried']}; hits |= {x['SmartScout Brand'].lower() for x in r['rows']}
def auto(v):
    out = []
    a = re.sub(r'\s+', '', v)
    if a != v: out.append(a)
    if '&' in v: out.append(v.replace('&', 'and'))
    s = re.sub(r'\b(Home|Homes|USA|US|America|Designs?|Furniture|Jewelry|Jewellery|Collection|Brands?|Group|International|Industries|Apparel)\b', '', v, flags=re.I).strip(' -&,')
    if s and s.lower() != v.lower() and len(s) > 2: out.append(s)
    return out
names = []
if __name__ != '__main__':
    pass
elif rnd == 1:
    names = sorted({x.strip() for x in b['Brand']} , key=str.lower)
    names = [n for n in names if n.lower() not in queried]
else:
    for _, r in b.drop_duplicates('Brand').iterrows():
        if r['Brand'].lower() in hits: continue
        vs = [v.strip() for v in r['Search Variants'].split(';') if v.strip()] + auto(r['Brand'])
        vs = [v for v in dict.fromkeys(vs) if v.lower() != r['Brand'].lower()][:2]
        names += [v for v in vs if v.lower() not in queried]
    names = sorted(set(names), key=str.lower)
if __name__ == '__main__':
  batches = [names[i:i+100] for i in range(0, len(names), 100)]
  json.dump(batches, open(f'phase3_work/ss_brand_batches_r{rnd}.json', 'w'))
  print('brands', b['Brand'].nunique(), 'to query', len(names), 'batches', len(batches))

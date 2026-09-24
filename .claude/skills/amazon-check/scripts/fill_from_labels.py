#!/usr/bin/env python3
"""Second pass over verify_brands.py output: fill the brand from Amazon's search-result brand label when the
product pages loaded but carried no byline (common on Amazon-sold listings: Garmin, Dometic, Cressi, vineyard vines).

Rule: at least two non-sponsored search results share the same label, the label's normalised form contains a
core piece of the company name (or the company's contains the label's), and the label is not a generic word.
Anything else stays unnamed for human review. Records source so the sheet notes can say where the name came from.

Usage: fill_from_labels.py out.json [out2.json ...]   (edits in place; prints what it filled)
"""
import sys, json, re, collections

STOP = {'inc','llc','co','corp','corporation','ltd','limited','company','the','and','group','brands','brand','international',
        'usa','us','designs','design','apparel','clothing','nutrition','foods','products','wholesale','sales','com','llp','plc'}
GENERIC = {'generic','sponsored','amazon','basics','unbranded','handmade'}

def norm(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
def words(s): return [w for w in re.split(r'[^A-Za-z0-9]+', s or '') if len(w) >= 3 and w.lower() not in STOP]

def label_ok(label, company):
    nl, nc = norm(label), norm(company)
    if not nl or nl in GENERIC or len(nl) < 3: return False
    if nl in nc or nc in nl: return True
    ws = [norm(w) for w in words(company)]
    return bool(ws) and all(w in nl for w in ws[:2])

for path in sys.argv[1:]:
    d = json.load(open(path)); filled = 0
    for k, v in d.items():
        if v.get('brand'): continue
        titles = v.get('search_titles') or []
        labels = collections.Counter()
        for t in titles:
            parts = [p.strip() for p in t.split('|')]
            if len(parts) < 2 or parts[0].lower().startswith('sponsored'): continue
            labels[parts[0]] += 1
        if not labels: continue
        label, n = labels.most_common(1)[0]
        pages_loaded = any(s.get('title') for s in v.get('steps', []))
        if n >= 2 and pages_loaded and label_ok(label, v.get('company') or k):
            ev = next((s.get('url') for s in v.get('steps', []) if s.get('title')), '')
            v.update(brand=label, store_url=v.get('store_url') or '', evidence=ev, name_match=True,
                     source='Amazon search result brand label (product page had no byline)')
            filled += 1; print(f'  {path}: {v.get("company") or k} -> {label}')
    json.dump(d, open(path, 'w'), indent=1, ensure_ascii=False)
    print(f'{path}: filled {filled}')

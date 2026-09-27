import pandas as pd, json, os, hashlib, re, glob
d = pd.read_excel('phase2_domains_ALL.xlsx', sheet_name='All', dtype=str).fillna('')
ins = d[d['Phase 3 Scope']=='Research']
def clean(n):
    n = re.sub(r'\(.*?\)', ' ', n)
    n = re.sub(r'\s*[/|]\s*.*$', '', n) if len(n) > 30 else n
    n = re.sub(r'[,.]?\s*\b(Inc|LLC|L\.L\.C|Corp|Corporation|Co|Ltd|Limited|Company|GmbH|S\.?A|S\.?r\.?l|Pvt|Private|B\.V|Pty|LTD|INC)\b\.?', '', n, flags=re.I)
    return re.sub(r'\s+', ' ', n).strip(' ,.-&')
ss = {}
for f in glob.glob('phase3_work/ss_names_*.jsonl'):
    for l in open(f):
        for r in json.loads(l)['rows']: ss[r['SmartScout Brand'].lower()] = r
rows = []
for k, x in ins.groupby('Exhibitor Key'):
    f = x.iloc[0]; dom = f['Domain']
    site, bp = {}, {}
    if dom:
        p = os.path.join('cache/site', hashlib.sha1(dom.encode()).hexdigest()+'.json')
        if os.path.exists(p): site = json.load(open(p))
        p = os.path.join('cache/brandpages', hashlib.sha1(dom.encode()).hexdigest()+'.json')
        if os.path.exists(p): bp = json.load(open(p))
    h = site.get('home', {}); ab = site.get('about', {})
    pages = [pg for pg in bp.get('pages', []) if pg.get('text')]
    hit = ss.get(clean(f['Exhibitor Name']).lower())
    rows.append({'Exhibitor Key': k, 'Exhibitor Name': f['Exhibitor Name'], 'Exhibitor Type': f['Exhibitor Type'],
      'Shows': ', '.join(sorted(set(x['Show ID']))), 'Categories': ' | '.join(sorted(set(c for c in x['Categories'] if c)))[:160],
      'About': max(x['About'], key=len)[:500], 'Website': dom, 'Site Title': h.get('title','')[:120], 'Site Description': h.get('desc','')[:250],
      'Site Text': ((ab.get('text') or '')[:400] + ' || ' + (h.get('text') or '')[:400]) if h else '',
      'Brand Page URL': ' ; '.join(pg['url'] for pg in pages)[:200],
      'Brand Page Text': ' || '.join(pg['text'][:700] for pg in pages)[:1200],
      'Brand Page Logos': ' ; '.join(dict.fromkeys(a for pg in pages for a in pg.get('img_alts', []) if 2 < len(a) < 50))[:500],
      'Parent Company': f['Parent Company'],
      'SmartScout Name Hit': f"{hit['SmartScout Brand']} | {hit['Primary Category']} > {hit['Primary Subcategory']} | products {int(hit['Total Products'])} | monthly revenue ${hit['Total Monthly Revenue']:,.0f}" if hit else ''})
df = pd.DataFrame(rows)
n = 14
for i in range(n): df.iloc[i::n].to_csv(f'phase3_work/brands_chunk_{i+1}.csv', index=False)
print(len(df), 'keys; with SS name hit', (df['SmartScout Name Hit']!='').sum(), '; with brand page', (df['Brand Page Text']!='').sum(), '; chunk', len(df.iloc[0::n]), '; avg chars', int(df.apply(lambda r: sum(len(str(v)) for v in r), axis=1).mean()))

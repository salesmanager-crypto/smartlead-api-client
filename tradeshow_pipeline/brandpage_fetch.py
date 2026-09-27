"""Phase 3: fetch brand/collection pages linked from in-scope exhibitor sites (max 2 per site). Per-host sequential, 1-2 s apart. Resumable."""
import json, os, hashlib, time, random, threading, re
from concurrent.futures import ThreadPoolExecutor
import pandas as pd, requests
from bs4 import BeautifulSoup
from common import UA
d = pd.read_excel('phase2_domains_ALL.xlsx', sheet_name='All', dtype=str).fillna('')
ins = d[d['Phase 3 Scope']=='Research'].drop_duplicates('Exhibitor Key')
jobs = []
for dom in sorted(set(ins['Domain']) - {''}):
    p = os.path.join('cache/site', hashlib.sha1(dom.encode()).hexdigest()+'.json')
    if os.path.exists(p):
        links = [u for u in json.load(open(p)).get('brand_links', []) if re.search(r'brand|label', u, re.I)] or json.load(open(p)).get('brand_links', [])
        if links: jobs.append((dom, links[:2]))
print('sites with brand links', len(jobs), flush=True)
def do(job):
    dom, links = job
    out = os.path.join('cache/brandpages', hashlib.sha1(dom.encode()).hexdigest()+'.json')
    if os.path.exists(out): return
    s = requests.Session(); s.headers['User-Agent'] = UA; s.verify = '/root/.ccr/ca-bundle.crt'
    pages = []
    for u in links:
        try:
            r = s.get(u, timeout=15)
            if r.ok and 'html' in r.headers.get('content-type', 'html'):
                b = BeautifulSoup(r.text[:800000], 'lxml')
                imgs = [i.get('alt','').strip() for i in b.find_all('img') if i.get('alt')][:60]
                for t in b(['script','style','noscript','svg']): t.decompose()
                txt = re.sub(r'\s+', ' ', b.get_text(' '))[:3000]
                pages.append({'url': r.url, 'text': txt, 'img_alts': imgs})
        except Exception as e:
            pages.append({'url': u, 'error': type(e).__name__})
        time.sleep(random.uniform(1, 2))
    json.dump({'domain': dom, 'pages': pages}, open(out, 'w'))
n = [0]; lock = threading.Lock()
def wrap(j):
    do(j)
    with lock:
        n[0] += 1
        if n[0] % 100 == 0: print('brand pages:', n[0], 'of', len(jobs), flush=True)
with ThreadPoolExecutor(24) as ex: list(ex.map(wrap, jobs))
print('DONE', flush=True)

"""Phase 2 step A: fetch homepage + about page per exhibitor domain; extract text and parent statements.
One thread per domain (sequential requests per host, 1-2 s apart); many hosts in parallel. Resumable: skips domains already in cache/site/."""
import json, os, re, sys, time, random, hashlib, threading
from concurrent.futures import ThreadPoolExecutor
import pandas as pd, requests
from bs4 import BeautifulSoup
from common import domain_of, UA
OUT = 'cache/site'
GENERIC = {'facebook.com','instagram.com','linktr.ee','etsy.com','linkedin.com','twitter.com','x.com','tiktok.com','youtube.com','amazon.com','ebay.com','whatnot.com','jewelry.org.hk','andmorehighpointmarket.com','pinterest.com','threads.net','gmail.com'}
PARENT_RE = re.compile(r"(?:a|an|the)?\s*(?:division|subsidiary|brand|member|part|company|business unit|affiliate)\s+of\s+(?:the\s+)?([A-Z][\w&.,' -]{2,60}?)(?:[.,;]|\s+(?:and|which|that|since|based|headquartered|family)\b)|(?:owned|acquired)\s+by\s+(?:the\s+)?([A-Z][\w&.,' -]{2,60}?)(?:[.,;]|\s+(?:in|and|since)\b)|(?:family|portfolio)\s+of\s+brands", re.S)
def clean(t): return re.sub(r'\s+', ' ', t or '').strip()
def get(sess, url):
    try:
        r = sess.get(url, timeout=15, allow_redirects=True)
        if r.status_code >= 400: return None, r.status_code, r.url
        if 'html' not in r.headers.get('content-type','html'): return None, 'nonhtml', r.url
        return r.text[:600000], r.status_code, r.url
    except Exception as e:
        return None, type(e).__name__, url
def extract(html):
    s = BeautifulSoup(html, 'lxml')
    title = clean(s.title.get_text()) if s.title else ''
    md = s.find('meta', attrs={'name': 'description'}) or s.find('meta', attrs={'property': 'og:description'})
    desc = clean(md.get('content')) if md else ''
    site = s.find('meta', attrs={'property': 'og:site_name'})
    links = [(clean(a.get_text())[:60], a.get('href') or '') for a in s.find_all('a')]
    for t in s(['script','style','noscript','svg']): t.decompose()
    text = clean(s.get_text(' '))
    copy = re.findall(r'(?:©|&copy;|Copyright)\s*(?:\d{4}\s*[-–]?\s*)?(?:\d{4})?\s*,?\s*([^|.©]{3,80})', text)
    return dict(title=title, desc=desc, site_name=clean(site.get('content')) if site else '', text=text[:4000], copyright=clean(copy[-1])[:80] if copy else '', links=links)
def parents(txt):
    out = []
    for m in PARENT_RE.finditer(txt):
        s = txt[max(0, m.start()-80): m.end()+40]
        out.append(clean(s))
    return out[:5]
def do(domain):
    p = os.path.join(OUT, hashlib.sha1(domain.encode()).hexdigest() + '.json')
    if os.path.exists(p): return
    sess = requests.Session(); sess.headers.update({'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'}); sess.verify = '/root/.ccr/ca-bundle.crt'
    rec = {'domain': domain}
    html, st, final = get(sess, 'https://' + domain)
    if html is None:
        time.sleep(random.uniform(1, 2)); html, st, final = get(sess, 'http://' + domain)
    rec['status'] = st; rec['final_url'] = final
    if html:
        h = extract(html); links = h.pop('links'); rec['home'] = h
        about = None
        for t, href in links:
            if re.search(r'about|our[- ]story|who[- ]we[- ]are|company', (t + ' ' + href), re.I) and not href.startswith(('mailto', 'tel', '#', 'javascript')):
                about = requests.compat.urljoin(final, href); break
        brands = [requests.compat.urljoin(final, href) for t, href in links if re.search(r'\bbrands?\b|our[- ]labels|collections?', t, re.I)][:3]
        rec['brand_links'] = sorted(set(brands))
        if about:
            time.sleep(random.uniform(1, 2)); ah, st2, af = get(sess, about)
            if ah: a = extract(ah); a.pop('links'); rec['about'] = a; rec['about_url'] = af
        alltxt = ' '.join([rec.get('home', {}).get('text', ''), rec.get('about', {}).get('text', '')])
        rec['parent_snippets'] = parents(alltxt)
    json.dump(rec, open(p, 'w'))
if __name__ == '__main__':
    a = pd.read_excel('phase1_exhibitors_ALL.xlsx', sheet_name='All', dtype=str).fillna('')
    doms = sorted({domain_of(w) for w in a['Website']} - {''} - GENERIC)
    doms = [d for d in doms if not any(d.endswith('.' + g) or d == g for g in GENERIC)]
    print('domains', len(doms), flush=True)
    done = [0]; lock = threading.Lock()
    def wrap(d):
        try: do(d)
        except Exception as e: print('ERR', d, e, flush=True)
        with lock:
            done[0] += 1
            if done[0] % 250 == 0: print('phase 2 site fetch:', done[0], 'of', len(doms), flush=True)
    with ThreadPoolExecutor(16) as ex: list(ex.map(wrap, doms))
    print('DONE', flush=True)

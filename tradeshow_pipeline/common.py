import hashlib, json, os, time, re, random
import requests
BASE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BASE, 'cache', 'pages')
os.makedirs(CACHE, exist_ok=True)
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36'
S = requests.Session(); S.headers.update({'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
S.verify = '/root/.ccr/ca-bundle.crt'
_last = {}
def _key(url, extra=''):
    return hashlib.sha1((url + extra).encode()).hexdigest()
def fetch(url, delay=(1.0, 2.0), method='GET', data=None, json_body=None, headers=None, force=False, binary=False, timeout=40):
    extra = json.dumps([method, data, json_body], sort_keys=True, default=str)
    p = os.path.join(CACHE, _key(url, extra) + ('.bin' if binary else '.html'))
    if os.path.exists(p) and not force:
        with open(p, 'rb') as f: b = f.read()
        return b if binary else b.decode('utf-8', 'replace')
    host = re.sub(r'^https?://([^/]+).*', r'\1', url)
    wait = random.uniform(*delay) - (time.time() - _last.get(host, 0))
    if wait > 0: time.sleep(wait)
    back = 5
    for attempt in range(4):
        try:
            r = S.request(method, url, data=data, json=json_body, headers=headers or {}, timeout=timeout)
            _last[host] = time.time()
            if r.status_code == 429:
                print('429 on', url, '-> pausing 600s'); time.sleep(600); continue
            if r.status_code >= 500:
                time.sleep(back); back *= 2; continue
            if r.status_code >= 400:
                return None
            with open(p, 'wb') as f: f.write(r.content)
            return r.content if binary else r.text
        except Exception as e:
            print('err', url, e); time.sleep(back); back *= 2
    return None
def norm_name(n):
    n = (n or '').lower()
    n = re.sub(r'[^\w\s]', ' ', n)
    n = re.sub(r'\b(inc|llc|l l c|corp|corporation|co|ltd|company|limited)\b', ' ', n)
    return re.sub(r'\s+', ' ', n).strip()
def domain_of(url):
    if not url: return ''
    u = url.strip().lower()
    u = re.sub(r'^https?://', '', u); u = re.sub(r'^www\.', '', u)
    return u.split('/')[0].split('?')[0].strip()

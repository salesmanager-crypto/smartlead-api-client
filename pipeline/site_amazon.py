"""First-pass Amazon flag from each exhibitor's own website.

  python3 pipeline/site_amazon.py run [threads]    fetch homepage (+ one where-to-buy page) per domain
  python3 pipeline/site_amazon.py status
  python3 pipeline/site_amazon.py build            -> site_amazon.csv

Used when Amazon itself can't be reached from this environment and SmartScout is out of credits. A brand
counts as "links to Amazon" only when its own site links to amazon.com (a store page, a product page or a
search for the brand) or to amzn.to / a.co. No link does not mean the brand is off Amazon: those rows stay
"Not checked on Amazon" for the SmartScout pass.
"""
import csv, html, json, os, random, re, ssl, sys, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse, unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, UA

WORK = os.path.join(ROOT, "pipeline", "work")
OUT = os.path.join(WORK, "site_amazon.jsonl")
MASTER = os.path.join(ROOT, "expowest_master.csv")
CSV_OUT = os.path.join(ROOT, "site_amazon.csv")
SSL = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
AMZ = re.compile(r'https?://(?:www\.|smile\.)?(?:amazon\.com|amzn\.to|a\.co|amzn\.com)/[^"\'\s<>]*', re.I)
WTB = re.compile(r'where[- ]?to[- ]?buy|store[- ]?locator|find[- ]?(?:us|a[- ]?store|in[- ]?store)|retailers?|buy[- ]?online|shop[- ]?online|stockists?', re.I)
lock = threading.Lock()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*;q=0.8",
                                               "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=25, context=SSL) as r:
        raw = r.read(3_000_000)
        enc = r.headers.get_content_charset() or "utf-8"
        return r.geturl(), raw.decode(enc, "ignore")


def amazon_links(h):
    out = []
    for m in AMZ.findall(html.unescape(h)):
        u = m.rstrip(").,;")
        if re.search(r"amazon\.com/(?:gp/help|ap/|gp/css|business|associates|primevideo|music|alexa)|"
                     r"amazon\.com/?$|aws\.amazon", u, re.I):
            continue
        out.append(u)
    return list(dict.fromkeys(out))


def store_hint(urls):
    """Brand name as it appears in an amazon.com/stores/<Name>/page/... link."""
    for u in urls:
        m = re.search(r"amazon\.com/stores/([^/]+)/page/", u, re.I)
        if m and m.group(1).lower() not in ("page", "node"):
            return unquote(m.group(1)).replace("+", " ")
    return ""


def check(row):
    url = row["Website"].strip()
    if not re.match(r"^https?://", url, re.I):
        url = "http://" + url
    res = {"id": row["Exhibitor ID"], "domain": row["Domain"], "url": url, "pages": 0,
           "amazon_links": [], "wtb_url": "", "error": ""}
    try:
        final, h = fetch(url)
        res["pages"] = 1
        res["final_url"] = final
        links = amazon_links(h)
        if not links:
            # one where-to-buy style page on the same site
            for href, text in re.findall(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', h, re.S | re.I):
                label = re.sub(r"<[^>]+>", " ", text)
                if WTB.search(href) or WTB.search(label):
                    u = urljoin(final, href)
                    if urlparse(u).netloc.split(":")[0].endswith(urlparse(final).netloc.split(":")[0].replace("www.", "")):
                        res["wtb_url"] = u
                        break
            if res["wtb_url"]:
                time.sleep(random.uniform(0.5, 1.2))
                try:
                    _, h2 = fetch(res["wtb_url"])
                    res["pages"] = 2
                    links = amazon_links(h2)
                except Exception as e:
                    res["error"] = f"wtb: {e.__class__.__name__}"
        res["amazon_links"] = links[:8]
    except Exception as e:
        res["error"] = f"{e.__class__.__name__}: {str(e)[:100]}"
    res["at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with lock:
        with open(OUT, "a") as f:
            f.write(json.dumps(res) + "\n")
    return res


def run(threads=12):
    rows = [r for r in csv.DictReader(open(MASTER, encoding="utf-8")) if r["Website"].strip() and r["Domain"]]
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["domain"] for l in open(OUT)}
    todo, seen = [], set()
    for r in rows:  # 2027 exhibitors come first in the master
        if r["Domain"] not in done and r["Domain"] not in seen:
            seen.add(r["Domain"])
            todo.append(r)
    print(f"{len(todo)} to do, {len(done)} done", flush=True)
    with ThreadPoolExecutor(threads) as ex:
        for i, _ in enumerate(ex.map(check, todo), 1):
            if i % 200 == 0:
                print(f"{i}/{len(todo)}", flush=True)


def load():
    res = {}
    if os.path.exists(OUT):
        for l in open(OUT):
            r = json.loads(l)
            res[r["domain"]] = r
    return res


def status():
    res = load()
    hit = sum(1 for r in res.values() if r["amazon_links"])
    err = sum(1 for r in res.values() if r["error"] and not r["pages"])
    print(f"{len(res)} checked, {hit} link to Amazon, {err} unreachable")


def build():
    res = load()
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Domain", "Site Links To Amazon", "Amazon Store Name (from link)",
                    "Amazon Link", "Pages Checked", "Site Error"])
        for r in res.values():
            w.writerow([r["domain"], "Yes" if r["amazon_links"] else ("No" if r["pages"] else ""),
                        store_hint(r["amazon_links"]), (r["amazon_links"] or [""])[0], r["pages"], r["error"]])
    status()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 12)
    elif cmd == "status":
        status()
    elif cmd == "build":
        build()
    else:
        print(__doc__)

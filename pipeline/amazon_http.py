"""Exact Amazon store name per exhibitor brand, over plain HTTP (no browser).

  python3 pipeline/amazon_http.py export      brand candidates from expowest_master.csv -> pipeline/work/amz_in.jsonl
  python3 pipeline/amazon_http.py run          one polite worker, resumable -> pipeline/work/amz_out_http.jsonl
  python3 pipeline/amazon_http.py status
  python3 pipeline/amazon_http.py collect      -> amazon_stores.csv (same columns as amazon_store.py collect)

Same rules as amazon_store.py (search the brand, open up to 3 product pages whose title names the brand, read
the byline): only the transport differs, because headless Chromium is refused from this environment while a
normal HTTP client is not. One worker, 4 to 8 seconds between brands, 1 to 2.5 seconds between pages. Robot
check pages are never recorded as a miss; the worker backs off 3, 6, 12 then 30 minutes.
"""
import csv, gzip, html as html_lib, http.cookiejar, json, os, random, re, ssl, sys, time, urllib.request, zlib
from urllib.parse import quote_plus, urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, UA
from amazon_store import is_block, norm, similar, squash, store_name

WORK = os.path.join(ROOT, "pipeline", "work")
IN = os.path.join(WORK, "amz_in.jsonl")
OUT = os.path.join(WORK, "amz_out_http.jsonl")
OUT_CSV = os.path.join(ROOT, "amazon_stores.csv")
MASTER = os.path.join(ROOT, "expowest_master.csv")
SSL = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
LEGAL = re.compile(r"\b(inc|llc|l\.l\.c|corp|corporation|co|company|ltd|limited|pbc|gmbh|s\.?a|srl|pty|dba)\b\.?", re.I)


def brand_candidates(name):
    """Brands to search for an exhibitor name: a parenthetical brand first ("10000 Inc (Magic Mind)"), then
    comma or slash separated brands ("Westbrae, The Good Bean, Beanitos"), then the name without legal words."""
    out = []
    for m in re.findall(r"\(([^)]+)\)", name):
        if not re.search(r"\b(formerly|dba|aka)\b", m, re.I):
            out.append(m)
    base = re.sub(r"\(.*?\)", " ", name)
    base = re.sub(r"\b(dba|d/b/a)\b.*$", "", base, flags=re.I)
    parts = [p for p in re.split(r"\s*[,/|]\s*|\s+&\s+(?=[A-Z])", base) if p.strip()] if re.search(r"[,/|]", base) else [base]
    for p in parts:
        p = LEGAL.sub(" ", p)
        p = re.sub(r"\s+", " ", p).strip(" .-,")
        if len(squash(p)) >= 2:
            out.append(p)
    seen, res = set(), []
    for b in out:
        k = squash(b)
        if k and k not in seen:
            seen.add(k)
            res.append(b.strip())
    return res[:3]


def export():
    rows = list(csv.DictReader(open(MASTER, encoding="utf-8")))
    items = []
    for r in rows:  # master order: 2027 exhibitors first, then most years shown
        for b in brand_candidates(r["Exhibitor"]):
            items.append({"key": f'{r["Exhibitor ID"]}|{squash(b)}', "id": r["Exhibitor ID"],
                          "exhibitor": r["Exhibitor"], "brand": b, "source": "exhibitor name", "domain": r["Domain"]})
    with open(IN, "w") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"exported {len(items)} brand candidates for {len(rows)} exhibitors")


class Http:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar),
                                              urllib.request.HTTPSHandler(context=SSL))

    def get(self, url):
        """GET with a retry when the body comes back cut short (no closing html tag)."""
        for attempt in range(4):
            code, h = self._get(url)
            if code != 200 or "</html>" in h[-5000:].lower() or len(h) > 50000:
                return code, h
            time.sleep(3 * (attempt + 1))
        return code, h

    def _get(self, url):
        req = urllib.request.Request(url, headers={
            "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip, deflate"})
        try:
            r = self.op.open(req, timeout=40)
            code, raw, enc = r.status, r.read(), r.headers.get("Content-Encoding", "")
        except urllib.error.HTTPError as e:
            code, raw, enc = e.code, e.read(), e.headers.get("Content-Encoding", "")
        if enc == "gzip":
            raw = gzip.decompress(raw)
        elif enc == "deflate":
            raw = zlib.decompress(raw)
        return code, raw.decode("utf-8", "ignore")


def title_of(h):
    m = re.search(r"<title[^>]*>(.*?)</title>", h, re.S)
    return html_lib.unescape(m.group(1)).strip() if m else ""


def blocked(code, h):
    return code in (503, 429) or is_block(h, title_of(h))


def search_results(h):
    out = []
    for m in re.finditer(r'<div[^>]+data-asin="([A-Z0-9]{10})"[^>]+data-component-type="s-search-result"', h):
        chunk = h[m.start():m.start() + 12000]
        t = re.search(r"<h2[^>]*>(.*?)</h2>", chunk, re.S)
        title = html_lib.unescape(re.sub(r"<[^>]+>", " ", t.group(1))) if t else ""
        out.append({"asin": m.group(1), "title": re.sub(r"\s+", " ", title).strip(),
                    "sponsored": "Sponsored" in chunk[:4000]})
        if len(out) >= 16:
            break
    return out


def product(s, asin):
    code, h = s.get(f"https://www.amazon.com/dp/{asin}")
    if blocked(code, h):
        return None
    byline, href = "", ""
    m = re.search(r'id="bylineInfo"[^>]*?(?:href="([^"]*)")?[^>]*>(.*?)</a>', h, re.S)
    if m:
        href = html_lib.unescape(m.group(1) or "")
        byline = re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
    brand_row = ""
    m = re.search(r'po-brand.*?po-break-word">\s*([^<]+)<', h, re.S)
    if m:
        brand_row = html_lib.unescape(m.group(1)).strip()
    sold = ""
    m = re.search(r'id="sellerProfileTriggerId"[^>]*>([^<]+)<', h)
    if m:
        sold = html_lib.unescape(m.group(1)).strip()
    elif re.search(r"Ships from and sold by Amazon|>Amazon\.com<", h):
        sold = "Amazon.com"
    return {"asin": asin, "title": title_of(h).replace("Amazon.com:", "").strip()[:200], "byline": byline,
            "store_url": urljoin("https://www.amazon.com", href.split("?")[0]) if href else "",
            "brand_row": brand_row, "sold_by": sold[:200]}


SERVICE = re.compile(r"\b(media|solutions|logistics|packaging|consult\w*|association|magazine|software|capital|"
                     r"insurance|printing|label(s|ing)?|equipment|machinery|brokers?|brokerage|agency|publishing|"
                     r"council|institute|university|bank|financial|freight|warehous\w*|fulfillment|staffing|"
                     r"recruit\w*|certification|laborator\w*|testing|analytics|marketing group|advisors?|"
                     r"partners|ventures|exhibits?|displays?|pavilion|chamber of commerce|trade commission|"
                     r"ministry|government|embassy|news|podcast)\b", re.I)
DOMAIN_FILLER = re.compile(r"^(get|try|drink|eat|shop|buy|the|my|go|we|love)|(foods?|inc|brands?|usa|co|shop|"
                           r"official|hq|online|store|company|global|group|llc|world|nutrition)$")


def domain_core(domain):
    lab = (domain or "").split(".")[0].replace("-", "")
    prev = None
    while prev != lab and len(lab) > 5:
        prev = lab
        lab = DOMAIN_FILLER.sub("", lab) if len(DOMAIN_FILLER.sub("", lab)) >= 4 else lab
    return lab if len(lab) >= 4 else ""


def check(s, item):
    q = item["brand"]
    dcore = domain_core(item.get("domain", ""))
    code, h = s.get(f"https://www.amazon.com/s?k={quote_plus(q)}")
    if blocked(code, h):
        return None
    time.sleep(random.uniform(1.0, 2.5))
    results = search_results(h)
    if not results and "s-search-result" not in h and "No results for" not in h:
        raise RuntimeError(f"search page without results ({len(h)} bytes)")
    nb = norm(q)
    cands = []
    for r in results:
        t = norm(r["title"])
        head = t[: len(nb) + 12]
        score = 2 if nb and t.startswith(nb) else (1 if nb and f" {nb} " in f" {head} " else 0)
        if not score and dcore and t.replace(" ", "").startswith(dcore):
            score = 1
        if score:
            cands.append((score, not r["sponsored"], r))
    cands.sort(key=lambda x: (-x[0], not x[1]))
    tried, best = [], None
    for _, _, r in cands[:3]:
        d = product(s, r["asin"])
        time.sleep(random.uniform(1.0, 2.5))
        if d is None:
            return None
        name, is_store = store_name(d["byline"])
        d.update({"store_name": name, "has_store": is_store,
                  "sim_brand": round(max(similar(name, q), similar(d["brand_row"], q)), 2),
                  "sim_exhibitor": round(max(similar(name, item["exhibitor"]), similar(d["brand_row"], item["exhibitor"]),
                                             1.0 if dcore and squash(name) == dcore else 0.0), 2)})
        tried.append(d)
        if d["sim_brand"] >= 0.85 or d["sim_exhibitor"] >= 0.85:
            best = d
            break
    if best is None and tried:
        best = max(tried, key=lambda d: max(d["sim_brand"], d["sim_exhibitor"]))
    status = "not found"
    if best:
        sc = max(best["sim_brand"], best["sim_exhibitor"])
        status = "verified" if sc >= 0.85 else ("possible" if sc >= 0.6 else "different brand")
        if status == "verified" and len(squash(q)) <= 3 and best["sim_exhibitor"] < 0.85 \
                and similar(best.get("sold_by", ""), item["exhibitor"]) < 0.6:
            status = "possible"
    return {"key": item["key"], "id": item["id"], "brand": q, "source": item["source"],
            "results": len(results), "title_matches": len(cands), "status": status,
            "best": best, "tried": len(tried), "at": time.strftime("%Y-%m-%d %H:%M:%S")}


def out_files():
    return [os.path.join(WORK, f) for f in sorted(os.listdir(WORK)) if f.startswith("amz_out_http")]


def run(w=0, n=1):
    items = [json.loads(l) for l in open(IN)]
    doms = {r["Exhibitor ID"]: r["Domain"] for r in csv.DictReader(open(MASTER, encoding="utf-8"))}
    out_path = os.path.join(WORK, f"amz_out_http_{w}.jsonl") if n > 1 else OUT
    done, verified_ids = set(), set()
    for path in out_files():
        for l in open(path):
            r = json.loads(l)
            if r["status"] != "error":
                done.add(r["key"])
                if r["status"] == "verified":
                    verified_ids.add(r["id"])
    todo = [it for i, it in enumerate(items) if it["key"] not in done and i % n == w]
    print(f"worker {w}: {len(todo)} to do, {len(done)} done", flush=True)
    time.sleep(w * 15)
    s = Http()
    backoff = [180, 360, 720, 1800]
    nb = 0
    i = 0
    while i < len(todo):
        it = todo[i]
        if it["id"] in verified_ids:  # a later brand candidate is not needed once one is verified
            i += 1
            continue
        if i % 100 == 0:
            doms = {r["Exhibitor ID"]: r["Domain"] for r in csv.DictReader(open(MASTER, encoding="utf-8"))}
        it["domain"] = doms.get(it["id"], it.get("domain", ""))
        if SERVICE.search(it["exhibitor"]):
            res = {"key": it["key"], "id": it["id"], "brand": it["brand"], "source": it["source"],
                   "status": "skipped service", "at": time.strftime("%Y-%m-%d %H:%M:%S")}
            with open(out_path, "a") as f:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")
            i += 1
            continue
        try:
            res = check(s, it)
        except Exception as e:
            res = {"key": it["key"], "id": it["id"], "brand": it["brand"], "source": it["source"],
                   "status": "error", "error": f"{e.__class__.__name__}: {str(e)[:120]}",
                   "at": time.strftime("%Y-%m-%d %H:%M:%S")}
        if res is None:
            wait = backoff[min(nb, len(backoff) - 1)]
            nb += 1
            print(f"robot check at {it['brand']!r}, sleeping {wait}s", flush=True)
            time.sleep(wait)
            s = Http()
            continue
        nb = 0
        if res["status"] == "verified":
            verified_ids.add(res["id"])
        with open(out_path, "a") as f:
            f.write(json.dumps(res, ensure_ascii=False) + "\n")
        i += 1
        if i % 25 == 0:
            print(f"{i}/{len(todo)}", flush=True)
        time.sleep(random.uniform(4, 8))


def load():
    rows = {}
    for path in out_files():
        for l in open(path):
            r = json.loads(l)
            if r["status"] != "error" or r["key"] not in rows:
                rows[r["key"]] = r
    return rows


def status():
    from collections import Counter
    rows = load()
    n_in = sum(1 for _ in open(IN))
    ids = {}
    order = {"verified": 0, "possible": 1, "different brand": 2, "not found": 3, "skipped service": 4, "error": 5}
    for r in rows.values():
        if r["id"] not in ids or order[r["status"]] < order[ids[r["id"]]]:
            ids[r["id"]] = r["status"]
    print(f"{len(rows)}/{n_in} brand candidates checked", dict(Counter(r["status"] for r in rows.values())))
    print(f"{len(ids)} exhibitors, best status:", dict(Counter(ids.values())))


def collect():
    rows = load()
    fields = ["Key", "Exhibitor ID", "Brand", "Brand Source", "Amazon Status", "Amazon Store Name",
              "Has Amazon Store", "Amazon Store URL", "Amazon Brand Field", "Sample ASIN", "Sample Product",
              "Sold By", "Match To Brand", "Match To Exhibitor", "Search Results", "Checked At", "Error"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows.values():
            b = r.get("best") or {}
            w.writerow({"Key": r["key"], "Exhibitor ID": r["id"], "Brand": r["brand"], "Brand Source": r["source"],
                        "Amazon Status": r["status"], "Amazon Store Name": html_lib.unescape(b.get("store_name", "")),
                        "Has Amazon Store": "Yes" if b.get("has_store") else ("No" if b else ""),
                        "Amazon Store URL": b.get("store_url", ""),
                        "Amazon Brand Field": html_lib.unescape(b.get("brand_row", "")),
                        "Sample ASIN": b.get("asin", ""), "Sample Product": b.get("title", ""),
                        "Sold By": b.get("sold_by", ""), "Match To Brand": b.get("sim_brand", ""),
                        "Match To Exhibitor": b.get("sim_exhibitor", ""), "Search Results": r.get("results", ""),
                        "Checked At": r.get("at", ""), "Error": r.get("error", "")})
    print(f"wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 0, int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    else:
        {"export": export, "status": status, "collect": collect}.get(cmd, lambda: print(__doc__))()

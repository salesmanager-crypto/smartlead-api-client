"""Verify each brand's exact Amazon store name ("Visit the X Store" under the product title).

  python amazon_store.py export          write pipeline/work/amz_in.jsonl: owned and licensed brands of
                                         Brand / Manufacturer exhibitors (distributors and unclear dropped),
                                         plus the exhibitor name for brand exhibitors with no brand found
  python amazon_store.py run W N         worker W of N: crawl its share of amz_in.jsonl into
                                         pipeline/work/amz_out_W.jsonl (resumable, skips done keys)
  python amazon_store.py status
  python amazon_store.py collect         merge worker files into amazon_stores.csv

Per brand: Amazon search for the brand, take up to 3 results whose title names the brand, open up to 2
product pages and read the byline (#bylineInfo). "Visit the X Store" gives the store name and store URL;
"Brand: X" gives a brand with no store. The store name is compared with the brand and the exhibitor name.
Robot check pages are detected and the worker backs off instead of recording a miss.
"""
import json, os, random, re, sys, time
from difflib import SequenceMatcher
from urllib.parse import quote_plus, urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CHROMIUM, ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
IN = os.path.join(WORK, "amz_in.jsonl")
OUT_CSV = os.path.join(ROOT, "amazon_stores.csv")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
STOP = {"inc", "llc", "ltd", "co", "corp", "corporation", "company", "the", "products", "usa", "us", "group",
        "industries", "international", "intl", "brand", "brands", "store", "official", "america", "na", "of",
        "and", "manufacturing", "mfg", "llc.", "inc.", "co.", "limited", "technology", "technologies"}


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"[’'`]", "", s)
    return " ".join(t for t in re.findall(r"[a-z0-9]+", s) if t not in STOP)


def squash(s):
    return norm(s).replace(" ", "")


def similar(a, b):
    a, b = squash(a), squash(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if len(min(a, b, key=len)) >= 4 and (a in b or b in a):
        return 0.9
    return SequenceMatcher(None, a, b).ratio()


def export():
    import pandas as pd
    p2 = pd.read_excel(os.path.join(ROOT, "phase2_domains.xlsx"), sheet_name="Exhibitors", dtype=str).fillna("")
    keep = p2[p2["Exhibitor Type"] == "Brand / Manufacturer"].set_index("Exhibitor ID")
    b = pd.read_excel(os.path.join(ROOT, "phase4_smartscout.xlsx"), sheet_name="Brands", dtype=str).fillna("")
    b = b[b["Exhibitor ID"].isin(keep.index) & b["Ownership"].isin(["Owned", "Licensed"])]
    rows, seen = [], set()
    for r in b.to_dict("records"):
        key = f'{r["Exhibitor ID"]}|{squash(r["Brand"])}'
        if key in seen:
            continue
        seen.add(key)
        rows.append({"key": key, "id": r["Exhibitor ID"], "exhibitor": keep.at[r["Exhibitor ID"], "Exhibitor Name"],
                     "brand": r["Brand"], "ownership": r["Ownership"], "source": "brand",
                     "domain": keep.at[r["Exhibitor ID"], "Domain"]})
    have = set(b["Exhibitor ID"])
    for eid, r in keep.iterrows():
        if eid in have:
            continue
        name = re.sub(r"\s*\(.*?\)", "", r["Exhibitor Name"]).strip()
        rows.append({"key": f"{eid}|{squash(name)}", "id": eid, "exhibitor": r["Exhibitor Name"], "brand": name,
                     "ownership": "Owned", "source": "exhibitor name", "domain": r["Domain"]})
    with open(IN, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"exported {len(rows)} brand candidates for {keep.shape[0]} brand / manufacturer exhibitors")


def is_block(html, title):
    h = html.lower()
    return ("validatecaptcha" in h or "enter the characters you see below" in h
            or "to discuss automated access to amazon data" in h or title.strip() in ("Sorry! Something went wrong!",))


def text_or(pg, sel):
    try:
        el = pg.query_selector(sel)
        return (el.inner_text() or "").strip() if el else ""
    except Exception:
        return ""


def product(pg, asin):
    """Byline, store URL, brand row and seller for one ASIN."""
    pg.goto(f"https://www.amazon.com/dp/{asin}", timeout=45000, wait_until="domcontentloaded")
    html, title = pg.content(), pg.title()
    if is_block(html, title):
        return None
    byline = text_or(pg, "#bylineInfo")
    href = ""
    try:
        el = pg.query_selector("#bylineInfo")
        href = el.get_attribute("href") or "" if el else ""
    except Exception:
        pass
    brand_row = ""
    m = re.search(r'po-brand.*?po-break-word">\s*([^<]+)<', html, re.S)
    if m:
        brand_row = m.group(1).strip()
    sold_by = text_or(pg, "#merchantInfo") or text_or(pg, "#sellerProfileTriggerId") or text_or(
        pg, "#merchant-info")
    return {"asin": asin, "title": title.replace("Amazon.com:", "").strip()[:200], "byline": byline,
            "store_url": urljoin("https://www.amazon.com", href) if href else "", "brand_row": brand_row,
            "sold_by": sold_by[:200]}


def store_name(byline):
    m = re.match(r"Visit the (.+?) Store$", byline.strip())
    if m:
        return m.group(1).strip(), True
    m = re.match(r"Brand:\s*(.+)$", byline.strip())
    if m:
        return m.group(1).strip(), False
    return "", False


def check(pg, item):
    q = item["brand"]
    pg.goto(f"https://www.amazon.com/s?k={quote_plus(q)}", timeout=45000, wait_until="domcontentloaded")
    time.sleep(random.uniform(1.0, 2.0))
    html, title = pg.content(), pg.title()
    if is_block(html, title):
        return None
    results = pg.eval_on_selector_all(
        "div[data-component-type='s-search-result'][data-asin]",
        "els => els.slice(0, 16).map(e => ({asin: e.getAttribute('data-asin'), "
        "title: (e.querySelector('h2') || {}).innerText || '', "
        "sponsored: /Sponsored/.test(e.innerText.slice(0, 200))}))")
    results = [r for r in results if r["asin"]]
    nb = norm(q)
    cands = []
    for r in results:
        t = norm(r["title"])
        head = t[: len(nb) + 12]
        score = 2 if nb and t.startswith(nb) else (1 if nb and f" {nb} " in f" {head} " else 0)
        if score:
            cands.append((score, not r["sponsored"], r))
    cands.sort(key=lambda x: (-x[0], not x[1]))
    tried, best = [], None
    for _, _, r in cands[:3]:
        d = product(pg, r["asin"])
        time.sleep(random.uniform(1.0, 2.5))
        if d is None:
            return None
        name, is_store = store_name(d["byline"])
        d.update({"store_name": name, "has_store": is_store,
                  "sim_brand": round(max(similar(name, q), similar(d["brand_row"], q)), 2),
                  "sim_exhibitor": round(similar(name, item["exhibitor"]), 2)})
        tried.append(d)
        if d["sim_brand"] >= 0.85 or d["sim_exhibitor"] >= 0.85:
            best = d
            break
    if best is None and tried:
        best = max(tried, key=lambda d: max(d["sim_brand"], d["sim_exhibitor"]))
    status = "not found"
    if best:
        s = max(best["sim_brand"], best["sim_exhibitor"])
        status = "verified" if s >= 0.85 else ("possible" if s >= 0.6 else "different brand")
        # short or generic names (SCC, Pro, Max) can match an unrelated brand: keep as possible unless the
        # store, brand field or seller also matches the exhibitor
        if status == "verified" and len(squash(q)) <= 3 and best["sim_exhibitor"] < 0.85 \
                and similar(best.get("sold_by", ""), item["exhibitor"]) < 0.6:
            status = "possible"
    return {"key": item["key"], "id": item["id"], "brand": q, "source": item["source"],
            "results": len(results), "title_matches": len(cands), "status": status,
            "best": best, "tried": len(tried), "at": time.strftime("%Y-%m-%d %H:%M:%S")}


def run(w, n):
    from playwright.sync_api import sync_playwright
    items = [json.loads(l) for l in open(IN)]
    items = [it for i, it in enumerate(items) if i % n == w]
    out = os.path.join(WORK, f"amz_out_{w}.jsonl")
    done = set()
    for f in os.listdir(WORK):
        if f.startswith("amz_out_"):
            for l in open(os.path.join(WORK, f)):
                r = json.loads(l)
                if r["status"] != "error":
                    done.add(r["key"])
    todo = [it for it in items if it["key"] not in done]
    print(f"worker {w}: {len(todo)} to do, {len(done)} done", flush=True)
    backoff = 60
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM, headless=True,
                              args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(user_agent=UA, locale="en-US", viewport={"width": 1366, "height": 900})
        ctx.route(re.compile(r".*\.(png|jpg|jpeg|gif|webp|svg|woff2?|mp4)(\?.*)?$"), lambda r: r.abort())
        pg = ctx.new_page()
        i = 0
        while i < len(todo):
            it = todo[i]
            try:
                res = check(pg, it)
            except Exception as e:
                res = {"key": it["key"], "id": it["id"], "brand": it["brand"], "source": it["source"],
                       "status": "error", "error": f"{e.__class__.__name__}: {str(e)[:120]}",
                       "at": time.strftime("%Y-%m-%d %H:%M:%S")}
            if res is None:
                print(f"worker {w}: robot check, sleeping {backoff}s", flush=True)
                time.sleep(backoff)
                backoff = min(backoff * 2, 900)
                ctx.clear_cookies()
                continue
            backoff = 60
            with open(out, "a") as fh:
                fh.write(json.dumps(res, ensure_ascii=False) + "\n")
            i += 1
            if i % 25 == 0:
                print(f"worker {w}: {i}/{len(todo)}", flush=True)
        b.close()


def status():
    n_in = sum(1 for _ in open(IN))
    rows = []
    for f in os.listdir(WORK):
        if f.startswith("amz_out_"):
            rows += [json.loads(l) for l in open(os.path.join(WORK, f))]
    from collections import Counter
    print(f"{len(rows)}/{n_in} done", dict(Counter(r["status"] for r in rows)))


def collect():
    import pandas as pd
    rows = {}
    for f in sorted(os.listdir(WORK)):
        if f.startswith("amz_out_"):
            for l in open(os.path.join(WORK, f)):
                r = json.loads(l)
                if r["status"] != "error" or r["key"] not in rows:
                    rows[r["key"]] = r
    out = []
    for r in rows.values():
        b = r.get("best") or {}
        out.append({"Key": r["key"], "Exhibitor ID": r["id"], "Brand": r["brand"], "Brand Source": r["source"],
                    "Amazon Status": r["status"], "Amazon Store Name": b.get("store_name", ""),
                    "Has Amazon Store": "Yes" if b.get("has_store") else ("No" if b else ""),
                    "Amazon Store URL": b.get("store_url", ""), "Amazon Brand Field": b.get("brand_row", ""),
                    "Sample ASIN": b.get("asin", ""), "Sample Product": b.get("title", ""),
                    "Sold By": b.get("sold_by", ""), "Match To Brand": b.get("sim_brand", ""),
                    "Match To Exhibitor": b.get("sim_exhibitor", ""), "Search Results": r.get("results", ""),
                    "Checked At": r.get("at", ""), "Error": r.get("error", "")})
    pd.DataFrame(out).to_csv(OUT_CSV, index=False)
    print(f"wrote {len(out)} rows to {OUT_CSV}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export()
    elif cmd == "run":
        run(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == "status":
        status()
    else:
        collect()

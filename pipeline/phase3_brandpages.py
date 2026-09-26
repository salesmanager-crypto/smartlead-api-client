"""Phase 3 prep: fetch up to two 'brand' pages per in-scope exhibitor (links found on the
homepage in phase 2) and extract candidate brand names (link text, image alt text, headings).

Cache: cache/brandpages/<sha1(url)>.json.gz. Output: pipeline/work/brand_pages.csv keyed by
Exhibitor ID. Several hosts in parallel, one request at a time per host.
"""
import gzip, hashlib, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import pandas as pd
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CACHE, ROOT
from phase2_fetch_sites import get

BP_CACHE = os.path.join(CACHE, "brandpages")
OUT = os.path.join(ROOT, "pipeline", "work", "brand_pages.csv")
os.makedirs(BP_CACHE, exist_ok=True)
SKIP = re.compile(r"(login|cart|account|privacy|terms|cookie|career|dealer|where-to-buy|wishlist|\.pdf$)", re.I)


def extract(html):
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "noscript", "svg", "iframe", "footer"]):
        t.decompose()
    alts = [i.get("alt", "").strip() for i in soup.find_all("img") if i.get("alt", "").strip()]
    heads = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3", "h4"])]
    links = [a.get_text(" ", strip=True) for a in soup.find_all("a") if 1 < len(a.get_text(" ", strip=True)) < 40]
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    uniq = lambda xs: list(dict.fromkeys(x for x in xs if x))
    return {"alts": uniq(alts)[:60], "heads": uniq(heads)[:40], "links": uniq(links)[:120], "text": text[:3000]}


def fetch(url):
    path = os.path.join(BP_CACHE, hashlib.sha1(url.encode()).hexdigest() + ".json.gz")
    if os.path.exists(path):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    status, final, html = get(url)
    rec = {"url": url, "status": status, "final_url": final}
    if html and not html.startswith("ERROR"):
        rec.update(extract(html))
    else:
        rec["error"] = html[:200]
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(rec, f)
    time.sleep(1)
    return rec


def main():
    p2 = pd.read_excel(os.path.join(ROOT, "phase2_domains.xlsx"), sheet_name="Exhibitors", dtype=str).fillna("")
    p2 = p2[p2["Phase 3 Scope"] == "Research"]
    jobs = {}
    for eid, links in zip(p2["Exhibitor ID"], p2["Site Brand Links"]):
        urls = []
        for part in links.split(" || "):
            if " -> " not in part:
                continue
            txt, url = part.rsplit(" -> ", 1)
            if SKIP.search(url) or url in urls:
                continue
            urls.append(url)
        if urls:
            jobs[eid] = urls[:2]
    print(f"{len(jobs)} exhibitors with brand links", flush=True)
    by_host = {}
    for eid, urls in jobs.items():
        for u in urls:
            by_host.setdefault(urlparse(u).netloc, []).append(u)
    results = {}

    def run_host(urls):
        return {u: fetch(u) for u in urls}

    done = 0
    with ThreadPoolExecutor(max_workers=10) as pool:
        for fut in as_completed([pool.submit(run_host, us) for us in by_host.values()]):
            results.update(fut.result())
            done += 1
            if done % 100 == 0:
                print(f"brand pages: {done} of {len(by_host)} hosts", flush=True)
    rows = []
    for eid, urls in jobs.items():
        for u in urls:
            r = results.get(u, {})
            rows.append({"Exhibitor ID": eid, "URL": u, "Status": r.get("status", ""),
                         "Alts": " | ".join(r.get("alts", []))[:1200],
                         "Headings": " | ".join(r.get("heads", []))[:800],
                         "Links": " | ".join(r.get("links", []))[:1500],
                         "Text": r.get("text", "")[:1200], "Error": r.get("error", "")})
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()

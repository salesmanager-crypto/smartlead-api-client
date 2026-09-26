"""Phase 2 prep: fetch each exhibitor's homepage and About page, cache them, and extract
signals for classification and parent-company research.

Cache: cache/sites/<host>.json.gz (one per website host; reruns skip cached hosts).
Output: pipeline/work/site_signals.csv keyed by Exhibitor ID.

One request at a time per host; several hosts in parallel (these are the exhibitors' own
sites, not the show or Amazon).
"""
import gzip, json, os, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CACHE, NON_COMPANY_DOMAINS, ROOT, UA, domain_of

SITE_CACHE = os.path.join(CACHE, "sites")
OUT = os.path.join(ROOT, "pipeline", "work", "site_signals.csv")
os.makedirs(SITE_CACHE, exist_ok=True)

PARENT_RE = re.compile(
    r"[^.]{0,160}\b(subsidiary of|a division of|division of|part of the|part of|member of the|"
    r"a brand of|brand of|owned by|acquired by|wholly[- ]owned|a unit of|an affiliate of|"
    r"parent company|sister company|family of brands|portfolio of brands|our brands|"
    r"a [A-Z][\w&.-]*(?: [A-Z][\w&.-]*){0,3} company)\b[^.]{0,160}\.", re.I)
ABOUT_WORDS = ("about", "company", "who-we-are", "who we are", "our-story", "our story", "history")
BRAND_WORDS = ("brand",)

session = requests.Session()
session.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
lock = threading.Lock()


def host_of(url):
    d = domain_of(url)
    if not d:
        return ""
    for bad in NON_COMPANY_DOMAINS:
        if d == bad or d.endswith("." + bad):
            return ""
    return d


def get(url):
    err = "retries exhausted"
    for attempt in range(3):
        try:
            r = session.get(url, timeout=20, allow_redirects=True)
            ctype = r.headers.get("content-type", "")
            if r.status_code == 429:
                time.sleep(30 * (attempt + 1))
                continue
            return r.status_code, r.url, (r.text if "html" in ctype or not ctype else "")
        except requests.RequestException as e:
            err = repr(e)[:200]
            time.sleep(2 ** (attempt + 1))
    return 0, url, "ERROR " + err


def page_text(html):
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "noscript", "svg", "iframe"]):
        t.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    md = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    desc = md.get("content", "").strip() if md else ""
    links = []
    for a in soup.find_all("a", href=True):
        txt = a.get_text(" ", strip=True)[:60]
        links.append((txt, a["href"]))
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    return title, desc, text, links


def fetch_site(host, website):
    path = os.path.join(SITE_CACHE, host + ".json.gz")
    if os.path.exists(path):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    start = website if website.lower().startswith("http") else "http://" + website
    status, final, html = get(start)
    rec = {"host": host, "start_url": start, "status": status, "final_url": final,
           "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    if html and not html.startswith("ERROR"):
        title, desc, text, links = page_text(html)
        rec.update(title=title, desc=desc, home_text=text[:6000])
        base_host = urlparse(final).netloc.lower().replace("www.", "")
        about_url, brand_links = "", []
        for txt, href in links:
            full = urljoin(final, href)
            u = urlparse(full)
            if u.scheme not in ("http", "https") or u.netloc.lower().replace("www.", "") != base_host:
                continue
            low = (txt + " " + u.path).lower()
            if not about_url and any(w in low for w in ABOUT_WORDS) and "career" not in low:
                about_url = full
            if any(w in low for w in BRAND_WORDS):
                brand_links.append([txt, full])
        rec["brand_links"] = brand_links[:30]
        rec["about_url"] = about_url
        if about_url:
            time.sleep(1)
            s2, f2, h2 = get(about_url)
            rec["about_status"] = s2
            if h2 and not h2.startswith("ERROR"):
                rec["about_text"] = page_text(h2)[2][:8000]
    else:
        rec["error"] = html[:300]
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(rec, f)
    return rec


def signals(rec):
    text = " ".join([rec.get("about_text", ""), rec.get("home_text", "")])
    hits = []
    for m in PARENT_RE.finditer(text):
        s = m.group(0).strip()
        if s not in hits:
            hits.append(s)
    snippet = rec.get("about_text") or rec.get("home_text") or ""
    return {
        "Site Status": rec.get("status", ""), "Site Final URL": rec.get("final_url", ""),
        "Site Title": rec.get("title", ""), "Site Description": rec.get("desc", ""),
        "About URL": rec.get("about_url", ""), "Site Snippet": snippet[:700],
        "Parent Hints": " || ".join(hits[:6])[:1500],
        "Brand Links": " || ".join(f"{t} -> {u}" for t, u in rec.get("brand_links", [])[:10])[:1200],
        "Site Error": rec.get("error", ""),
    }


def main():
    ex = pd.read_excel(os.path.join(ROOT, "phase1_exhibitors.xlsx"), sheet_name="Exhibitors",
                       dtype=str).fillna("")
    jobs = {}
    for eid, web in zip(ex["Exhibitor ID"], ex["Website"]):
        h = host_of(web)
        if h:
            jobs.setdefault(h, (web, []))[1].append(eid)
    print(f"{len(jobs)} hosts to fetch for {len(ex)} exhibitors", flush=True)
    rows, done = [], 0
    with ThreadPoolExecutor(max_workers=10) as pool:
        futs = {pool.submit(fetch_site, h, w): (h, ids) for h, (w, ids) in jobs.items()}
        for fut in as_completed(futs):
            h, ids = futs[fut]
            try:
                rec = fut.result()
            except Exception as e:
                rec = {"host": h, "error": repr(e)[:300]}
            sig = signals(rec)
            for eid in ids:
                rows.append({"Exhibitor ID": eid, "Host": h, **sig})
            done += 1
            if done % 100 == 0:
                print(f"sites: {done} of {len(jobs)} fetched", flush=True)
    pd.DataFrame(rows).sort_values("Exhibitor ID").to_csv(OUT, index=False)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()

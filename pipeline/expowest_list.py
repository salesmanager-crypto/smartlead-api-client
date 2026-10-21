"""Natural Products Expo West exhibitor directories (Small World Labs / A2Z) for several years.

  python3 pipeline/expowest_list.py list            every exhibitor row per year -> pipeline/work/ew_list_<year>.jsonl
  python3 pipeline/expowest_list.py details [N]     detail page per unique exhibitor (website, address), N workers
  python3 pipeline/expowest_list.py build           merge years, dedupe -> expowest_master.csv

The directory paginates through a POST to index.php (module organizations_organization_list). We load the
page once in Chromium, click page 2 to capture that request, then replay it with a larger limit using the
same session. Detail pages (/co/<slug>) are cached under cache/expowest/<year>/.
2025 is not on Small World Labs: its directory sits in the event app behind an image captcha, so it is
left out rather than worked around.
"""
import csv, html, json, os, re, sys, time, random
from urllib.parse import parse_qsl, urlencode

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NON_COMPANY_DOMAINS, ROOT, UA, domain_of, norm_name, registrable_domain

PLACEHOLDER = NON_COMPANY_DOMAINS | {"nocompanywebsite.com", "none.com", "na.com", "example.com", "gmail.com",
                                     "yahoo.com", "hotmail.com", "outlook.com", "wix.com", "squarespace.com"}

SHOWS = {
    2024: "https://expowest24.smallworldlabs.com",
    2026: "https://expowest26.smallworldlabs.com",
    2027: "https://expowest27.smallworldlabs.com",
}
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
WORK = os.path.join(ROOT, "pipeline", "work")
CACHE = os.path.join(ROOT, "cache", "expowest")
OUT = os.path.join(ROOT, "expowest_master.csv")
os.makedirs(WORK, exist_ok=True)

ROW = re.compile(r'href="(/co/[^"]+)"[^>]*>([^<]+)</a>(.*?)</tr>', re.S)
BOOTH = re.compile(r'Booth #\s*([A-Za-z0-9-]+)')


def parse_rows(fragment):
    out = []
    for slug, name, rest in ROW.findall(fragment):
        out.append({"slug": slug, "name": html.unescape(name).strip(), "booths": BOOTH.findall(rest)})
    return out


def list_year(year, base):
    from playwright.sync_api import sync_playwright
    path = os.path.join(WORK, f"ew_list_{year}.jsonl")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        ctx = b.new_context(user_agent=UA, viewport={"width": 1600, "height": 1200})
        pg = ctx.new_page()
        cap = []
        def on_request(r):
            try:
                if b"paginationHandler" in (r.post_data_buffer or b""):
                    cap.append(r)
            except Exception:
                pass
        pg.on("request", on_request)
        pg.goto(base + "/exhibitors", wait_until="networkidle", timeout=120000)
        pg.evaluate("""() => { const a=[...document.querySelectorAll('a.pager-item')]
            .find(e=>/Next Page$/.test(e.getAttribute('aria-label')||'')); if (a) a.click(); }""")
        for _ in range(30):
            if cap:
                break
            pg.wait_for_timeout(500)
        if not cap:
            raise SystemExit(f"{year}: no pagination request captured")
        form = dict(parse_qsl(cap[0].post_data_buffer.decode("utf-8", "ignore")))
        rows, seen, offset, limit = [], {}, 0, 50
        while True:
            form.update(limit=str(limit), offset=str(offset))
            r = ctx.request.post(base + "/index.php", data=urlencode(form),
                                 headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                          "X-Requested-With": "XMLHttpRequest"})
            raw = r.body()
            for enc in ("utf-8-sig", "utf-16", "latin-1"):
                try:
                    j = json.loads(raw.decode(enc))
                    break
                except (UnicodeDecodeError, ValueError):
                    j = None
            if j is None:
                print(f"{year}: offset {offset} unreadable response ({r.status}), retrying", flush=True)
                time.sleep(10)
                continue
            from urllib.parse import unquote
            body = unquote(j.get("data") or "")
            if j.get("formToken"):
                form.update(tk=j["formToken"], tm=j["formTime"])
            page = parse_rows(body)
            if not page:
                break
            got = []
            for x in page:
                if x["slug"] in seen:
                    seen[x["slug"]]["booths"] = sorted(set(seen[x["slug"]]["booths"]) | set(x["booths"]))
                else:
                    got.append(x)
            for x in got:
                seen[x["slug"]] = x
                rows.append(x)
            print(f"{year}: offset {offset} +{len(got)} = {len(rows)}", flush=True)
            offset += len(j.get("objects") or page)
            if offset >= int(j.get("total") or 0):
                break
            time.sleep(random.uniform(1, 2))
        b.close()
    with open(path, "w") as f:
        for x in rows:
            f.write(json.dumps({"year": year, **x}) + "\n")
    print(f"{year}: {len(rows)} exhibitors -> {path}")


def load_lists():
    out = []
    for year in SHOWS:
        p = os.path.join(WORK, f"ew_list_{year}.jsonl")
        if os.path.exists(p):
            out += [json.loads(l) for l in open(p)]
    return out


def group(rows):
    """One group per company: same normalized name, newest year first."""
    g = {}
    for r in sorted(rows, key=lambda r: -r["year"]):
        g.setdefault(norm_name(r["name"]), []).append(r)
    return g


def detail_targets():
    # fetch the newest year's page for each company (it carries the current website and address)
    return [v[0] for v in group(load_lists()).values()]


def parse_detail(h):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
    txt = re.sub(r"<[^>]+>", "\n", t)
    txt = html.unescape(re.sub(r"[ \t]+", " ", txt))
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    d = {"website": "", "address": "", "about": ""}

    def after(label, n=1):
        for i, l in enumerate(lines):
            if l == label and i + 1 < len(lines):
                return lines[i + 1:i + 1 + n]
        return []

    w = after("Website")
    if w and re.match(r"^(https?://|www\.)", w[0], re.I):
        d["website"] = w[0]
    a = after("Address", 4)
    addr = []
    for l in a:
        if l in ("[Cancel]", "Share:", "Contact", "Phone", "Email", "Social"):
            break
        addr.append(l)
    d["address"] = ", ".join(addr)
    m = re.search(r'<div[^>]*class="[^"]*(?:description|about)[^"]*"[^>]*>(.*?)</div>', t, re.S | re.I)
    if m:
        d["about"] = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).strip()[:1500]
    socials = re.findall(r'href="(https?://(?:www\.)?(?:linkedin|facebook|instagram|twitter|x|tiktok|youtube)\.com/[^"]+)"', t)
    d["socials"] = sorted(set(s for s in socials if "smallworldlabs" not in s and "expowest" not in s.lower()
                              and "naturalproductsexpo" not in s.lower() and "newhope" not in s.lower()))
    return d


def details(worker=0, nworkers=1):
    import urllib.request
    import ssl
    targets = detail_targets()
    ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt")
    out = os.path.join(WORK, f"ew_details_{worker}.jsonl")
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["key"] for l in open(out)}
    f = open(out, "a")
    for i, t in enumerate(targets):
        if i % nworkers != worker:
            continue
        key = f'{t["year"]}{t["slug"]}'
        if key in done:
            continue
        cdir = os.path.join(CACHE, str(t["year"]))
        os.makedirs(cdir, exist_ok=True)
        cpath = os.path.join(cdir, t["slug"].strip("/").replace("/", "_") + ".html")
        if os.path.exists(cpath):
            h = open(cpath, errors="ignore").read()
        else:
            h = ""
            for attempt in range(4):
                try:
                    req = urllib.request.Request(SHOWS[t["year"]] + t["slug"], headers={"User-Agent": UA})
                    h = urllib.request.urlopen(req, timeout=45, context=ctx).read().decode("utf-8", "ignore")
                    break
                except Exception as e:  # back off and retry
                    time.sleep(5 * (attempt + 1))
            if h:
                open(cpath, "w").write(h)
            time.sleep(random.uniform(0.6, 1.4))
        d = parse_detail(h) if h else {"website": "", "address": "", "about": "", "socials": [], "error": "fetch failed"}
        f.write(json.dumps({"key": key, **d}) + "\n")
        f.flush()
    f.close()


def company_domain(url):
    d = domain_of(url)
    d = registrable_domain(d) if d else ""
    return "" if d in PLACEHOLDER else d


def build():
    det = {}
    for fn in os.listdir(WORK):
        if fn.startswith("ew_details_"):
            for l in open(os.path.join(WORK, fn)):
                x = json.loads(l)
                det[x["key"]] = x
    groups = group(load_lists())
    recs = []
    for k, v in groups.items():
        top = v[0]
        d = det.get(f'{top["year"]}{top["slug"]}', {})
        # fall back to an older year's page when the newest one has no website
        for r in v[1:]:
            if d.get("website"):
                break
            d2 = det.get(f'{r["year"]}{r["slug"]}', {})
            if d2.get("website"):
                d = {**d, "website": d2["website"], "address": d.get("address") or d2.get("address", "")}
        years = sorted({r["year"] for r in v})
        booths = {}
        for r in v:
            booths.setdefault(r["year"], set()).update(r["booths"])
        recs.append({
            "name": top["name"], "norm": k, "years": years,
            "booths": "; ".join(f'{y}: {", ".join(sorted(booths[y]))}' for y in sorted(booths, reverse=True) if booths[y]),
            "website": d.get("website", ""), "domain": company_domain(d.get("website", "")),
            "address": d.get("address", ""), "socials": " ".join(d.get("socials", [])),
            "urls": " ".join(SHOWS[r["year"]] + r["slug"] for r in v),
        })
    # stable IDs from list data only, so later website data never renumbers anyone
    recs.sort(key=lambda r: (-max(r["years"]), -len(r["years"]), r["norm"]))
    for i, r in enumerate(recs, 1):
        r["eid"] = f"E{i:04d}"
    # second pass: merge different names that share a company domain
    by_dom = {}
    for r in recs:
        if r["domain"]:
            by_dom.setdefault(r["domain"], []).append(r)
    drop = set()
    for dom, rs in by_dom.items():
        if len(rs) < 2:
            continue
        rs.sort(key=lambda r: r["eid"])
        keep = rs[0]
        for r in rs[1:]:
            keep["years"] = sorted(set(keep["years"]) | set(r["years"]))
            keep["booths"] = "; ".join(x for x in [keep["booths"], r["booths"]] if x)
            keep["urls"] += " " + r["urls"]
            keep.setdefault("aka", []).append(r["name"])
            drop.add(id(r))
    recs = [r for r in recs if id(r) not in drop]
    recs.sort(key=lambda r: (-max(r["years"]), -len(r["years"]), r["norm"]))
    fields = ["Exhibitor ID", "Exhibitor", "Also Listed As", "Years", "In 2027", "Years Count", "Booths",
              "Website", "Domain", "Address", "Social Links", "Show URLs"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, r in enumerate(recs, 1):
            w.writerow({"Exhibitor ID": r["eid"], "Exhibitor": r["name"], "Also Listed As": "; ".join(r.get("aka", [])),
                        "Years": ", ".join(map(str, r["years"])), "In 2027": "Yes" if 2027 in r["years"] else "No",
                        "Years Count": len(r["years"]), "Booths": r["booths"], "Website": r["website"],
                        "Domain": r["domain"], "Address": r["address"], "Social Links": r["socials"],
                        "Show URLs": r["urls"]})
    raw = load_lists()
    print(f"rows per year: " + ", ".join(f"{y}: {sum(1 for r in raw if r['year']==y)}" for y in SHOWS))
    print(f"raw rows {len(raw)} -> unique by name {len(groups)} -> after domain merge {len(recs)}")
    print(f"with website: {sum(1 for r in recs if r['website'])}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "list":
        years = [int(a) for a in sys.argv[2:]] or list(SHOWS)
        for y in years:
            list_year(y, SHOWS[y])
    elif cmd == "details":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        if len(sys.argv) > 3:
            details(int(sys.argv[3]), n)
        else:
            import subprocess
            procs = [subprocess.Popen([sys.executable, __file__, "details", str(n), str(w)]) for w in range(n)]
            for p in procs:
                p.wait()
    elif cmd == "build":
        build()
    else:
        print(__doc__)

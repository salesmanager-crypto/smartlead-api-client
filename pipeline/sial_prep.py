"""SIAL Paris 2026 front end: turns the "SIAL Paris 2026 Exhibitors - Amazon US Presence" Google Sheet into the
files the shared pipeline scripts read (phase1_exhibitors.xlsx, phase2_domains.xlsx, phase4_smartscout.xlsx).

  python sial_prep.py base          pipeline/work/src_exhibitors.json + src_brands.json (raw get_values dumps of
                                    the Exhibitors and Brands tabs) -> pipeline/work/sial_base.csv and
                                    phase1_exhibitors.xlsx for the exhibitors marked On Amazon US = ✓
  python sial_prep.py profiles      fetch each exhibitor's SIAL profile page (cached) -> description, activity
                                    fields, own social links, complementary entities, brands, address
                                    -> pipeline/work/sial_profiles.csv and pipeline/work/social_links.csv
  python sial_prep.py export N      classification work units (type, parent, brands owned) -> p2_in_XX.jsonl
  python sial_prep.py collect       p2_out_XX.jsonl -> phase2_domains.xlsx and phase4_smartscout.xlsx (Brands)
  python sial_prep.py amz           Amazon store work list -> pipeline/work/amz_in.jsonl, brands the sheet
                                    already matched on Amazon first (tier 0), other owned brands after (tier 1)
  python sial_prep.py status

Exhibitor IDs (E0001...) follow the sheet's estimated Amazon revenue, highest first, and are fixed once
sial_base.csv exists (rerunning base keeps them).
"""
import glob, gzip, html as html_lib, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CACHE, NON_COMPANY_DOMAINS, ROOT, UA, domain_of, norm_name

WORK = os.path.join(ROOT, "pipeline", "work")
BASE = os.path.join(WORK, "sial_base.csv")
PROFILES = os.path.join(WORK, "sial_profiles.csv")
SOCIAL = os.path.join(WORK, "social_links.csv")
PROFILE_CACHE = os.path.join(CACHE, "sial")
PROFILE_URL = "https://www.sialparis.com/en/exhibitors-2026/exhibitor/"
SHOW = "SIAL Paris 2026"
TYPES = {"Brand / Manufacturer", "Distributor / Wholesaler", "Service / Software / Media / Association",
         "Equipment / Packaging / B2B Supplier", "Unclear"}
OWNERSHIP = {"Owned", "Licensed", "Third-party", "Not a brand"}


def money(s):
    try:
        return float(re.sub(r"[$,]", "", s or ""))
    except ValueError:
        return 0.0


def host(url):
    d = domain_of(url)
    if not d or any(d == b or d.endswith("." + b) for b in NON_COMPANY_DOMAINS):
        return ""
    return d


def rows(path):
    v = json.load(open(path))["values"]
    h = v[0]
    return [dict(zip(h, r + [""] * (len(h) - len(r)))) for r in v[1:]]


def base():
    ex = [r for r in rows(os.path.join(WORK, "src_exhibitors.json")) if r["On Amazon US"] == "✓"]
    ids = {}
    if os.path.exists(BASE):
        old = pd.read_csv(BASE, dtype=str, keep_default_na=False)
        ids = dict(zip(old["SIAL Profile ID"], old["Exhibitor ID"]))
    merged = {}
    for r in ex:  # the catalog lists a few exhibitors once per stand; keep one row with every stand
        m = merged.setdefault(r["SIAL profile ID"], dict(r))
        if m is not r and r["Stand(s)"] and r["Stand(s)"] not in m["Stand(s)"]:
            m["Stand(s)"] = ", ".join(x for x in (m["Stand(s)"], r["Stand(s)"]) if x)
    ex = sorted(merged.values(), key=lambda r: -money(r["Est. monthly Amazon revenue (USD)"]))
    n = max([int(i[1:]) for i in ids.values()] or [0])
    out = []
    for r in ex:
        pid = r["SIAL profile ID"]
        if pid not in ids:
            n += 1
            ids[pid] = f"E{n:04d}"
        out.append({"Exhibitor ID": ids[pid], "Exhibitor Name": r["Exhibitor"], "Country": r["Country"],
                    "Sector": r["Sector"], "Stand": r["Stand(s)"], "Website": r["Website"],
                    "Domain": host(r["Website"]), "SIAL Brands": r["Brands listed on SIAL"],
                    "Brands On Amazon (sheet)": r["Brands on Amazon US"],
                    "Sheet Monthly Revenue": money(r["Est. monthly Amazon revenue (USD)"]),
                    "Sheet Flag": r["Flag"], "SIAL Profile ID": pid, "SIAL Profile URL": PROFILE_URL + pid})
    d = pd.DataFrame(out).sort_values("Exhibitor ID")
    d.to_csv(BASE, index=False)
    # the shared site fetcher (phase2_fetch_sites.py) reads this
    d.rename(columns={"Stand": "SIAL Stand"}).assign(Shows=SHOW).to_excel(
        os.path.join(ROOT, "phase1_exhibitors.xlsx"), sheet_name="Exhibitors", index=False)
    print(f"{len(d)} exhibitors marked ✓; with a website domain: {(d['Domain'] != '').sum()}; "
          f"flagged likely distributor: {(d['Sheet Flag'] != '-').sum() - (d['Sheet Flag'] == '').sum()}")


def brand_rows():
    """Exhibitor ID -> list of the sheet's Brands-tab rows (brand, Amazon name, match, revenue, sellers)."""
    b = pd.read_csv(BASE, dtype=str, keep_default_na=False)
    pid2id = dict(zip(b["SIAL Profile ID"], b["Exhibitor ID"]))
    out = {}
    for r in rows(os.path.join(WORK, "src_brands.json")):
        eid = pid2id.get(r["SIAL profile ID"])
        if eid:
            out.setdefault(eid, []).append(r)
    return out


# ---- SIAL profile pages ----

def text_of(fragment):
    t = re.sub(r"^[^<>]*>", "", fragment)  # sections start and end mid-tag
    t = re.sub(r"<[^>]*$", "", t)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html_lib.unescape(t)).strip()


def section(h, start_pat, end_pats):
    m = re.search(start_pat, h)
    if not m:
        return ""
    rest = h[m.end():]
    end = min([e.start() for p in end_pats for e in [re.search(p, rest)] if e] or [len(rest)])
    return rest[:end]


def parse_profile(h):
    strip = section(h, r'class="CatalogExhibitorStrip-sociallist-left"', [r'CatalogExhibitorStrip-sociallist-right'])
    social = dict.fromkeys(["LinkedIn", "Facebook", "X", "Instagram", "YouTube", "TikTok"], "")
    for u in re.findall(r'href="(https?://[^"]+)"', strip):
        d = domain_of(u)
        for k, dom in (("LinkedIn", "linkedin.com"), ("Facebook", "facebook.com"), ("X", "x.com"),
                       ("X", "twitter.com"), ("Instagram", "instagram.com"), ("YouTube", "youtube.com"),
                       ("TikTok", "tiktok.com")):
            if (d == dom or d.endswith("." + dom)) and not social[k]:
                social[k] = html_lib.unescape(u)
    desc = text_of(section(h, r'class="CatalogItemDescription"', [r'Activity fields', r'id="certifications"',
                                                                   r'<!-- Additional Entities -->']))
    desc = re.sub(r"^Description :\s*", "", desc)
    activity = text_of(section(h, r'Activity fields\s*:', [r'</div></div></div>', r'id="certifications"']))
    entities = text_of(section(h, r'<!-- Additional Entities -->', [r'id="partners"', r'<!-- Partners', r'>Partners<',
                                                                    r'id="products"', r'id="brands"']))
    entities = re.sub(r"^Complementary entities\s*\(\d+\)\s*", "", entities)
    brands = text_of(section(h, r'id="brands"', [r'More exhibitors', r'<footer']))
    brands = re.sub(r"^Brands\s*", "", brands).replace("-->", "").strip()
    addr = text_of(section(h, r'>Address<', [r'Thematic tours', r'Certifications:', r'Download PDF']))
    return {**social, "SIAL Description": desc[:3000], "SIAL Activity Fields": activity[:600],
            "SIAL Complementary Entities": entities[:800], "SIAL Brands Section": re.sub(r"\s+", " ", brands)[:600],
            "SIAL Address": addr[:300]}


def fetch_profile(pid):
    os.makedirs(PROFILE_CACHE, exist_ok=True)
    path = os.path.join(PROFILE_CACHE, re.sub(r"[^\w.-]", "_", pid) + ".html.gz")
    if os.path.exists(path):
        return gzip.open(path, "rt", encoding="utf-8").read()
    for attempt in range(3):
        try:
            r = requests.get(PROFILE_URL + pid, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"},
                             timeout=30)
            if r.status_code == 200:
                with gzip.open(path, "wt", encoding="utf-8") as f:
                    f.write(r.text)
                time.sleep(1.0)
                return r.text
            if r.status_code == 404:
                return ""
        except requests.RequestException:
            pass
        time.sleep(5 * (attempt + 1))
    return ""


def profiles():
    b = pd.read_csv(BASE, dtype=str, keep_default_na=False)
    with ThreadPoolExecutor(max_workers=3) as pool:
        pages = list(pool.map(fetch_profile, b["SIAL Profile ID"]))
    out = []
    for (_, r), h in zip(b.iterrows(), pages):
        p = parse_profile(h) if h else {}
        out.append({"Exhibitor ID": r["Exhibitor ID"], "Profile Loaded": "Yes" if h else "No", **p})
    d = pd.DataFrame(out)
    d.to_csv(PROFILES, index=False)
    d[["Exhibitor ID", "LinkedIn", "Facebook", "X", "Instagram", "YouTube", "TikTok"]].to_csv(SOCIAL, index=False)
    print(f"profiles loaded {(d['Profile Loaded'] == 'Yes').sum()} of {len(d)}; LinkedIn {(d['LinkedIn'] != '').sum()}, "
          f"description {(d['SIAL Description'] != '').sum()}, complementary entities "
          f"{(d['SIAL Complementary Entities'] != '').sum()}")


# ---- classification work units ----

def signals_for(website):
    from phase2_fetch_sites import SITE_CACHE, signals
    h = host(website)
    p = os.path.join(SITE_CACHE, h + ".json.gz") if h else ""
    if not p or not os.path.exists(p):
        return {}
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        return signals(json.load(fh))


def export(chunk):
    b = pd.read_csv(BASE, dtype=str, keep_default_na=False)
    prof = pd.read_csv(PROFILES, dtype=str, keep_default_na=False).set_index("Exhibitor ID").to_dict("index")
    br = brand_rows()
    pending = set()
    for f in glob.glob(os.path.join(WORK, "p2_in_*.jsonl")):
        pending |= {json.loads(l)["id"] for l in open(f)}
    items = []
    for r in b.to_dict("records"):
        if r["Exhibitor ID"] in pending:
            continue
        p, s = prof.get(r["Exhibitor ID"], {}), signals_for(r["Website"])
        items.append({
            "id": r["Exhibitor ID"], "name": r["Exhibitor Name"], "country": r["Country"], "sector": r["Sector"],
            "website": r["Website"], "domain": r["Domain"], "sheet_flag": r["Sheet Flag"],
            "sial_description": p.get("SIAL Description", "")[:900],
            "sial_activity_fields": p.get("SIAL Activity Fields", ""),
            "sial_complementary_entities": p.get("SIAL Complementary Entities", ""),
            "sial_brands": r["SIAL Brands"][:900],
            "site": " | ".join(x for x in [s.get("Site Title", ""), s.get("Site Description", "")] if x)[:300]
                    + (" || " + s.get("Site Snippet", "")[:400] if s else ""),
            "site_status": str(s.get("Site Status", "")), "site_about_url": s.get("About URL", ""),
            "parent_hints": s.get("Parent Hints", "")[:700],
            "brands": [{"brand": x["Brand"], "brand_source": x["Brand source"],
                        "amazon_name": x["Exact brand name on Amazon"], "on_amazon": x["On Amazon US"],
                        "match": x["Match status"], "monthly_revenue": x["Est. monthly revenue (USD)"],
                        "seller_type": x["Seller type"], "amazon_category": x["SmartScout category"]}
                       for x in br.get(r["Exhibitor ID"], [])][:40],
        })
    existing = glob.glob(os.path.join(WORK, "p2_in_*.jsonl"))
    n = max([int(os.path.basename(f)[6:8]) for f in existing] or [-1]) + 1
    made = []
    for i in range(0, len(items), chunk):
        with open(os.path.join(WORK, f"p2_in_{n:02d}.jsonl"), "w") as fh:
            for it in items[i:i + chunk]:
                fh.write(json.dumps(it, ensure_ascii=False) + "\n")
        made.append(f"{n:02d}")
        n += 1
    print(f"exported {len(items)} exhibitors into chunks: {' '.join(made)}")


def load_out():
    out = {}
    for f in sorted(glob.glob(os.path.join(WORK, "p2_out_*.jsonl"))):
        for l in open(f):
            l = l.strip()
            if l:
                try:
                    r = json.loads(l)
                except json.JSONDecodeError:
                    continue
                if r.get("type") in TYPES:
                    out[r["id"]] = r  # a later line for the same id replaces an earlier one
    return out


def clean(s):
    return str(s or "").replace("—", ", ").replace("–", "-").strip()


def collect():
    b = pd.read_csv(BASE, dtype=str, keep_default_na=False)
    prof = pd.read_csv(PROFILES, dtype=str, keep_default_na=False).set_index("Exhibitor ID").to_dict("index")
    br = brand_rows()
    got = load_out()
    ex_rows, brand_out = [], []
    for r in b.to_dict("records"):
        eid = r["Exhibitor ID"]
        c = got.get(eid, {})
        p = prof.get(eid, {})
        ex_rows.append({
            "Exhibitor ID": eid, "Exhibitor Name": r["Exhibitor Name"], "Shows": SHOW, "SIAL Stand": r["Stand"],
            "Country": r["Country"], "Sector": r["Sector"], "Website": r["Website"],
            "Domain": r["Domain"] or domain_of(c.get("domain_found", "")),
            "Domain Confidence": "from SIAL" if r["Domain"] else ("found by search" if c.get("domain_found") else "not found"),
            "Domain Source": clean(c.get("domain_source")),
            "People Domains": "; ".join(dict.fromkeys(d for d in (domain_of(x) for x in c.get("people_domains") or []) if d)),
            "Parent Company": clean(c.get("parent")), "Parent Domain": domain_of(c.get("parent_domain", "")),
            "Parent Source": clean(c.get("parent_source")), "Exhibitor Type": c.get("type", ""),
            "Type Reason": clean(c.get("type_reason")), "LinkedIn": p.get("LinkedIn", ""),
            "About Summary": p.get("SIAL Description", "")[:600], "SIAL Brands": r["SIAL Brands"],
            "SIAL Profile URL": r["SIAL Profile URL"], "Sheet Monthly Revenue": r["Sheet Monthly Revenue"],
            "Notes": clean(c.get("notes")) if c else "Classification not done yet"})
        sheet = {norm_name(x["Brand"]): x for x in br.get(eid, [])}
        for x in c.get("brands", []):
            s = sheet.get(norm_name(x.get("brand", "")), {})
            brand_out.append({"Exhibitor ID": eid, "Brand": clean(x.get("brand")),
                              "Ownership": x.get("ownership", ""), "Brand Source": clean(x.get("source")),
                              "Sheet Amazon Name": s.get("Exact brand name on Amazon", ""),
                              "Sheet On Amazon": s.get("On Amazon US", ""),
                              "Monthly Revenue": money(s.get("Est. monthly revenue (USD)", "")),
                              "Sheet Seller Type": s.get("Seller type", "")})
    ex = pd.DataFrame(ex_rows)
    with pd.ExcelWriter(os.path.join(ROOT, "phase2_domains.xlsx"), engine="openpyxl") as xw:
        ex.to_excel(xw, sheet_name="Exhibitors", index=False)
    bd = pd.DataFrame(brand_out, columns=["Exhibitor ID", "Brand", "Ownership", "Brand Source", "Sheet Amazon Name",
                                          "Sheet On Amazon", "Monthly Revenue", "Sheet Seller Type"])
    with pd.ExcelWriter(os.path.join(ROOT, "phase4_smartscout.xlsx"), engine="openpyxl") as xw:
        bd.to_excel(xw, sheet_name="Brands", index=False)
    done = ex[ex["Exhibitor Type"] != ""]
    print(f"classified {len(done)} of {len(ex)}")
    print(done["Exhibitor Type"].value_counts().to_string())
    print(f"with parent: {(done['Parent Company'] != '').sum()}; brand rows: {len(bd)}; "
          f"ownership: {bd['Ownership'].value_counts().to_dict()}")


def amz():
    p2 = pd.read_excel(os.path.join(ROOT, "phase2_domains.xlsx"), sheet_name="Exhibitors", dtype=str).fillna("")
    keep = p2[p2["Exhibitor Type"] == "Brand / Manufacturer"].set_index("Exhibitor ID")
    bd = pd.read_excel(os.path.join(ROOT, "phase4_smartscout.xlsx"), sheet_name="Brands", dtype=str).fillna("")
    bd = bd[bd["Exhibitor ID"].isin(keep.index) & bd["Ownership"].isin(["Owned", "Licensed"]) & (bd["Brand"] != "")]
    from amazon_store import squash
    items, seen = [], set()
    for r in bd.to_dict("records"):
        key = f'{r["Exhibitor ID"]}|{squash(r["Brand"])}'
        if key in seen or not squash(r["Brand"]):
            continue
        seen.add(key)
        items.append({"key": key, "id": r["Exhibitor ID"], "exhibitor": keep.at[r["Exhibitor ID"], "Exhibitor Name"],
                      "brand": r["Brand"], "ownership": r["Ownership"], "source": "brand",
                      "domain": keep.at[r["Exhibitor ID"], "Domain"],
                      "tier": 0 if r["Sheet On Amazon"] in ("✓", "?") else 1,
                      "rev": float(keep.at[r["Exhibitor ID"], "Sheet Monthly Revenue"] or 0)})
    have = {i["id"] for i in items}
    for eid, r in keep.iterrows():
        if eid not in have:
            name = re.sub(r"\s*\(.*?\)", "", r["Exhibitor Name"]).strip()
            items.append({"key": f"{eid}|{squash(name)}", "id": eid, "exhibitor": r["Exhibitor Name"], "brand": name,
                          "ownership": "Owned", "source": "exhibitor name", "domain": r["Domain"], "tier": 1,
                          "rev": float(r["Sheet Monthly Revenue"] or 0)})
    items.sort(key=lambda i: (i["tier"], -i["rev"]))
    with open(os.path.join(WORK, "amz_in.jsonl"), "w") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"{len(items)} brands for {len(keep)} brand / manufacturer exhibitors; tier 0 (already matched on Amazon "
          f"in the sheet): {sum(i['tier'] == 0 for i in items)}")


def status():
    b = pd.read_csv(BASE, dtype=str)
    got = load_out()
    print(f"base {len(b)}; classified {len(got)}")
    for f in sorted(glob.glob(os.path.join(WORK, "p2_in_*.jsonl"))):
        k = os.path.basename(f)[6:8]
        ids = [json.loads(l)["id"] for l in open(f)]
        print(f"  chunk {k}: {len(ids)} in, {sum(i in got for i in ids)} out")


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"base": base, "profiles": profiles, "export": lambda: export(int(sys.argv[2])), "collect": collect,
     "amz": amz, "status": status}[cmd]()

"""Decision makers, emails and custom copy for Expo West exhibitors that sell on Amazon.

  python3 pipeline/expowest_people.py targets            exhibitors in scope, in priority order (printed summary)
  python3 pipeline/expowest_people.py sf-export N        next chunk of N in-scope exhibitors with no Surfe search yet
                                                          -> pipeline/work/sf_in_NN.jsonl
  python3 pipeline/expowest_people.py sd-export N        second Surfe pass (D) for in-scope brands with fewer than 5
                                                          people: other domains and company names -> sd_in_NN.jsonl
  python3 pipeline/expowest_people.py select             up to 5 people per exhibitor -> surfe_people.csv
  python3 pipeline/expowest_people.py se-export N BUDGET  selected people with no email lookup yet, chunks of N,
                                                          at most BUDGET people -> pipeline/work/se_in_NN.jsonl
  python3 pipeline/expowest_people.py ce-export N        people with an email and no custom email yet
                                                          -> pipeline/work/ce_in_NN.jsonl
  python3 pipeline/expowest_people.py status

In scope: an exhibitor whose Amazon status is verified or possible (amazon_http.py), with a website domain.
Priority: verified before possible, exhibiting in 2027 first, then the number of years exhibited.
Title filter and ranking are the shared rules in surfe_people.py.
"""
import csv, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT
from surfe_people import EXCLUDE, KEEP, PRESIDENT, norm_li, rank
from amazon_store import squash
from amazon_http import domain_core
from difflib import SequenceMatcher

WORK = os.path.join(ROOT, "pipeline", "work")
MASTER = os.path.join(ROOT, "expowest_master.csv")
PEOPLE = os.path.join(ROOT, "surfe_people.csv")
ORDER = {"verified": 0, "possible": 1, "different brand": 2, "not found": 3, "skipped service": 4, "error": 5}


def load(pattern):
    out = []
    for f in sorted(glob.glob(os.path.join(WORK, pattern))):
        for l in open(f):
            l = l.strip()
            if l:
                try:
                    out.append(json.loads(l))
                except json.JSONDecodeError:
                    pass
    return out


def amazon_best():
    """Best Amazon result per exhibitor ID."""
    best = {}
    for r in load("amz_out_http*.jsonl"):
        cur = best.get(r["id"])
        if cur is None or ORDER[r["status"]] < ORDER[cur["status"]]:
            best[r["id"]] = r
    return best


def master():
    return {r["Exhibitor ID"]: r for r in csv.DictReader(open(MASTER, encoding="utf-8"))}


# suppliers to other manufacturers (ingredients, packaging, commodities) rarely buy Amazon agency services
B2B = re.compile(r"\b(plastics?|packag\w*|chemicals?|ingredients?|flavou?rs?|fragrances?|mills?|commodit\w*|"
                 r"co-?pack\w*|contract manufactur\w*|private label|bulk|wholesale|distribut\w*|import\w*|"
                 r"export\w*|trading|sourcing|processing|containers?|bottl(es|ing)|closures?|films?|"
                 r"polymers?|enzymes?|cultures|starches?|sweeteners?|proteins? (inc|corp|llc)|biotech\w*)\b", re.I)
B2B_NAMES = {"adm", "amcor", "cargill", "ingredion", "givaudan", "dsm", "kerry", "tate and lyle", "bunge"}


_OLD = None


def old_db():
    """Exhibitor ID -> match in the old Expo West database (old_db_dedup.py)."""
    global _OLD
    if _OLD is None:
        p = os.path.join(WORK, "old_db_match.json")
        _OLD = json.load(open(p)) if os.path.exists(p) else {}
    return _OLD


def tier(eid, in2027):
    """Campaign priority: brands new to us first, brands already in the old database after (kept, not dropped).
    1 new + 2027 list, 2 new, 3 in old database, 4 in old database with contacts already sent."""
    o = old_db().get(eid, {})
    if o.get("old_sent"):
        return 4
    if o.get("old_company"):
        return 3
    return 1 if in2027 else 2


def strict_sim(a, b):
    """Name match without the loose substring shortcut: a contained name must cover most of the other."""
    a, b = squash(a), squash(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    short, long_ = sorted((a, b), key=len)
    if len(short) >= 4 and short in long_ and len(short) / len(long_) >= 0.6:
        return 0.9
    return SequenceMatcher(None, a, b).ratio()


def targets():
    m, amz = master(), amazon_best()
    skip = {r["id"] for r in load("excluded.jsonl")}  # reviewed by hand: on Amazon but not a fit
    out = []
    for eid, a in amz.items():
        if a["status"] not in ("verified", "possible") or eid not in m or eid in skip:
            continue
        r = m[eid]
        if not r["Domain"] and not r["Exhibitor"]:
            continue
        if B2B.search(r["Exhibitor"]) or squash(r["Exhibitor"]) in {squash(x) for x in B2B_NAMES}:
            continue
        b = a.get("best") or {}
        names = [x for x in (b.get("store_name", ""), b.get("brand_row", "")) if x]
        dcore = domain_core(r["Domain"])
        match = max([strict_sim(n, t) for n in names for t in (a["brand"], r["Exhibitor"], dcore) if t] or [0])
        if match < 0.8:
            continue
        # the show's website field is sometimes another company's; search Surfe by name when it doesn't fit
        dfit = max([strict_sim(dcore, t) for t in [a["brand"], r["Exhibitor"]] + names if t] or [0])
        if dfit < 0.6 and not any(squash(t) and (squash(t) in dcore or dcore in squash(t)
                                                 or os.path.commonprefix([squash(t), dcore]).__len__() >= 4)
                                  for t in [a["brand"], r["Exhibitor"]] + names):
            domain = ""
        else:
            domain = r["Domain"]
        out.append({"id": eid, "name": r["Exhibitor"], "domain": domain, "brand": a["brand"],
                    "store": b.get("store_name", ""), "status": a["status"],
                    "in2027": r["In 2027"] == "Yes", "years": int(r["Years Count"] or 0)})
    for t in out:
        t["tier"] = tier(t["id"], t["in2027"])
    out += old_targets(amz, skip)
    out.sort(key=lambda t: (t["tier"], ORDER[t["status"]], -t["years"], t["id"]))
    return out


def domain_fits(domain, names):
    """False when the website domain looks like another company's (search Surfe by name instead)."""
    dcore = domain_core(domain)
    if not dcore:
        return False
    if max([strict_sim(dcore, t) for t in names if t] or [0]) >= 0.6:
        return True
    return any(squash(t) and (squash(t) in dcore or dcore in squash(t)
                              or len(os.path.commonprefix([squash(t), dcore])) >= 4) for t in names)


def old_targets(amz, skip):
    """Brands only in the old Expo West database that sell on Amazon and were typed Brand / Manufacturer
    (expowest_phase2.py). Tier 3, or 4 when the old campaign already sent to them."""
    old_path, cp_path = os.path.join(ROOT, "old_only_companies.csv"), os.path.join(ROOT, "phase2_checkpoint.csv")
    if not (os.path.exists(old_path) and os.path.exists(cp_path)):
        return []
    p2 = {r["Exhibitor ID"]: r for r in csv.DictReader(open(cp_path, encoding="utf-8"))}
    out = []
    for r in csv.DictReader(open(old_path, encoding="utf-8")):
        oid, a = r["Old ID"], amz.get(r["Old ID"])
        if not a or a["status"] != "verified" or oid in skip:
            continue
        if p2.get(oid, {}).get("Exhibitor Type") != "Brand / Manufacturer":
            continue
        b = a.get("best") or {}
        names = [r["Company"], a["brand"], b.get("store_name", ""), b.get("brand_row", "")]
        domain = r["Domain"] or p2[oid]["Domain Found"]
        out.append({"id": oid, "name": r["Company"], "domain": domain if domain_fits(domain, names) else "",
                    "brand": a["brand"], "store": b.get("store_name", ""), "status": a["status"],
                    "in2027": False, "years": 0, "tier": 4 if r["Already Sent (old)"] == "Yes" else 3})
    return out


def next_nn(prefix):
    nums = [int(re.search(r"_(\d+)\.jsonl$", f).group(1)) for f in glob.glob(os.path.join(WORK, f"{prefix}_in_*.jsonl"))]
    return max(nums, default=0) + 1


def sf_export(n):
    done = {json.loads(l)["id"] for f in glob.glob(os.path.join(WORK, "sf_in_*.jsonl")) for l in open(f)}
    todo = [t for t in targets() if t["id"] not in done][:n]
    if not todo:
        print("nothing to export")
        return
    nn = next_nn("sf")
    path = os.path.join(WORK, f"sf_in_{nn:02d}.jsonl")
    with open(path, "w") as f:
        for t in todo:
            f.write(json.dumps({"id": t["id"], "name": t["name"], "domain": t["domain"], "brands": t["brand"],
                                "amazon_store": t["store"]}, ensure_ascii=False) + "\n")
    print(f"wrote {len(todo)} exhibitors to {path}")


SUFFIX = re.compile(r"[,.]?\s*\b(inc|llc|ltd|co|corp|corporation|company|limited|gmbh|s\.?a|pbc|l\.?l\.?c)\b\.?$", re.I)


def plain(name):
    """Company name as Surfe would hold it: no legal suffix, symbols or bracketed extras."""
    n = re.sub(r"\(.*?\)|[®™]", "", name or "")
    for _ in range(2):
        n = SUFFIX.sub("", n.strip())
    return re.sub(r"\s+", " ", n).strip(" ,.-")


def sd_export(n):
    """Pass D: brands still under 5 people after passes A to C. Lists domains not searched yet (phase 2 research,
    parent-free) and the company names to search by (Surfe's company name, the Amazon store, the exhibitor)."""
    done = {json.loads(l)["id"] for f in glob.glob(os.path.join(WORK, "sd_in_*.jsonl")) for l in open(f)}
    skip = {r["id"] for r in load("bad_match.jsonl")} | {r["id"] for r in load("excluded.jsonl")}
    have = {}
    for p in people():
        have[p["Exhibitor ID"]] = have.get(p["Exhibitor ID"], 0) + 1
    co = {r["id"]: r for r in load("sf_co_*.jsonl")}
    p2f = os.path.join(ROOT, "phase2_checkpoint.csv")
    p2 = {r["Exhibitor ID"]: r for r in csv.DictReader(open(p2f, encoding="utf-8"))} if os.path.exists(p2f) else {}
    todo = []
    for t in targets():
        if t["id"] in done or t["id"] in skip or have.get(t["id"], 0) >= 5:
            continue
        if p2.get(t["id"], {}).get("Exhibitor Type", "Brand / Manufacturer") != "Brand / Manufacturer":
            continue
        cand = [t["name"], t["brand"], t["store"]]
        found = p2.get(t["id"], {}).get("Domain Found", "").strip().lower()
        domains = [found] if found and found != (t["domain"] or "").lower() and domain_fits(found, cand) else []
        names = []
        for x in (co.get(t["id"], {}).get("name", ""), t["store"], t["name"], t["brand"]):
            x = plain(x)
            if x and squash(x) not in {squash(y) for y in names}:
                names.append(x)
        todo.append({"id": t["id"], "name": t["name"], "store": t["store"], "brands": t["brand"],
                     "searched_domain": t["domain"], "new_domains": domains, "names": names[:3],
                     "have": have.get(t["id"], 0), "tier": t["tier"]})
    todo = todo[:n]
    if not todo:
        print("nothing to export")
        return
    nn = next_nn("sd")
    path = os.path.join(WORK, f"sd_in_{nn:02d}.jsonl")
    with open(path, "w") as f:
        for t in todo:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    print(f"wrote {len(todo)} brands to {path} ({sum(1 for t in todo if t['new_domains'])} with a new domain)")


COUNTRY = {"United States": "us", "Canada": "ca", "United Kingdom": "gb", "Australia": "au", "Mexico": "mx",
           "Italy": "it", "France": "fr", "Germany": "de", "Spain": "es", "Japan": "jp", "Korea, Republic of": "kr",
           "South Korea": "kr", "Netherlands": "nl", "Israel": "il", "Ireland": "ie", "New Zealand": "nz",
           "India": "in", "China": "cn", "Taiwan": "tw", "Peru": "pe", "Colombia": "co", "Brazil": "br"}


def select():
    m = master()
    bad_match = {r["id"] for r in load("bad_match.jsonl")}  # reviewed: Surfe matched another company
    bad_match |= {r["id"] for r in load("excluded.jsonl")}  # reviewed: not a fit, or an existing client
    raw = [p for p in load("sf_raw_*.jsonl") if p.get("id") not in bad_match]
    names = {t["id"]: t for f in glob.glob(os.path.join(WORK, "sf_in_*.jsonl")) for t in map(json.loads, open(f))}
    sdin = {t["id"]: t for f in glob.glob(os.path.join(WORK, "sd_in_*.jsonl")) for t in map(json.loads, open(f))}
    for p in load("sd_raw_*.jsonl"):  # pass D: name searches cover several brands per call, so match by name
        if p.get("pass") == "error" or not p.get("firstName"):
            continue
        if str(p.get("pass", "")).startswith("DN"):
            cands = [c for c in (p.get("cands") or [p.get("id")]) if c in sdin]
            score, best = max(((max([strict_sim(p.get("companyName", ""), x) for x in sdin[c]["names"] if x] or [0]), c)
                               for c in cands), default=(0, None))
            if score < 0.8:
                continue
            p = {**p, "id": best, "byname": True}
        if p.get("id") not in bad_match:
            raw.append(p)
    by = {}
    for p in raw:
        p = {k: (p.get(k) or "") for k in ("id", "firstName", "lastName", "jobTitle", "linkedInUrl", "country",
                                            "seniorities", "companyName", "companyDomain", "pass", "byname")}
        p["sen"] = " ".join(p["seniorities"]).lower() if isinstance(p["seniorities"], list) else str(p["seniorities"]).lower()
        p["country"] = str(p["country"]).lower()
        t = p["jobTitle"]
        if p["pass"] == "error" or not p["firstName"] or not t:
            continue
        if EXCLUDE.search(t) or PRESIDENT.search(t) or not KEEP.search(t):
            continue
        if len(p["lastName"].rstrip(".")) <= 1:
            continue
        src = names.get(p["id"], {})
        home_cc = COUNTRY.get(m.get(p["id"], {}).get("Address", "").rsplit(",", 1)[-1].strip(), "")
        if home_cc and p["country"] and p["country"] not in (home_cc, "us"):
            continue  # offshore contractors and other regions are not the brand's decision makers
        if not src.get("domain") or p["byname"]:  # searched by name: the person's company must be this exhibitor
            if not p["byname"] and max(strict_sim(p["companyName"], t) for t in (
                    src.get("name", ""), src.get("brands", ""), src.get("amazon_store", "")) if t) < 0.8:
                continue
            home = COUNTRY.get(m.get(p["id"], {}).get("Address", "").rsplit(",", 1)[-1].strip(), "")
            if home and p["country"] and p["country"] != home:
                continue  # same name, different country: likely another company
            if not home and p["country"] not in ("us", ""):
                continue  # no address on file (old-database brands): a same-name match abroad is likely another company
            tld = p["companyDomain"].rsplit(".", 1)[-1].lower() if "." in p["companyDomain"] else ""
            if home and len(tld) == 2 and tld not in (home, "us", "co", "io", "ai", "me", "tv"):
                continue  # company site in another country
        key = norm_li(p["linkedInUrl"]) or f'{p["firstName"]} {p["lastName"]}'.lower()
        by.setdefault(p["id"], {}).setdefault(key, p)
    fields = ["Key", "Exhibitor ID", "Exhibitor Name", "First Name", "Last Name", "Title", "LinkedIn URL",
              "Country", "Seniority", "Surfe Company", "Company Domain", "Priority"]
    rows = []
    for eid, d in by.items():
        if eid.startswith("O") and any(p["country"] == "us" for p in d.values()):
            # old-database brands have no address on file: when Surfe finds US people, drop other regions
            d = {k: p for k, p in d.items() if p["country"] in ("us", "")}
        seen, uniq = set(), []
        for p in sorted(d.values(), key=rank):  # same person with two LinkedIn profiles: keep the better-ranked one
            nk = f'{p["firstName"]} {p["lastName"]}'.lower().strip()
            if nk not in seen:
                seen.add(nk)
                uniq.append(p)
        for i, p in enumerate(uniq[:5], 1):
            fix = lambda s: s.strip().title() if s.islower() or s.isupper() else s.strip()
            pid = norm_li(p["linkedInUrl"]) or f'{p["firstName"]} {p["lastName"]}'.lower().strip()
            rows.append({"Key": f'{eid}|{pid}', "Exhibitor ID": eid,
                         "Exhibitor Name": names.get(eid, {}).get("name", p["companyName"]),
                         "First Name": fix(p["firstName"]), "Last Name": fix(p["lastName"]),
                         "Title": p["jobTitle"].strip(), "LinkedIn URL": p["linkedInUrl"],
                         "Country": p["country"].upper(), "Seniority": p["sen"], "Surfe Company": p["companyName"],
                         "Company Domain": p["companyDomain"] or names.get(eid, {}).get("domain", ""), "Priority": i})
    with open(PEOPLE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    searched = {i for i in names}
    print(f"{len(rows)} people for {len(by)} of {len(searched)} searched exhibitors; "
          f"5 people: {sum(1 for d in by.values() if len(d) >= 5)}")


def people():
    return list(csv.DictReader(open(PEOPLE, encoding="utf-8"))) if os.path.exists(PEOPLE) else []


def se_export(n, budget):
    done = {json.loads(l)["key"] for f in glob.glob(os.path.join(WORK, "se_in_*.jsonl")) for l in open(f)}
    order = {t["id"]: i for i, t in enumerate(targets())}
    todo = sorted([p for p in people() if p["Key"] not in done],
                  key=lambda p: (order.get(p["Exhibitor ID"], 10**6), int(p["Priority"])))[:budget]
    nn = next_nn("se")
    for i in range(0, len(todo), n):
        path = os.path.join(WORK, f"se_in_{nn:02d}.jsonl")
        with open(path, "w") as f:
            for p in todo[i:i + n]:
                f.write(json.dumps({"key": p["Key"], "id": p["Exhibitor ID"], "firstName": p["First Name"],
                                    "lastName": p["Last Name"], "linkedinUrl": p["LinkedIn URL"],
                                    "companyDomain": p["Company Domain"], "companyName": p["Exhibitor Name"]},
                                   ensure_ascii=False) + "\n")
        print(f"wrote {len(todo[i:i + n])} people to {path}")
        nn += 1


def emails():
    out = {}
    for r in load("se_out_*.jsonl"):
        out[r["key"]] = r
    return out


def ce_export(n):
    m, amz, em = master(), amazon_best(), emails()
    done = {json.loads(l)["key"] for f in glob.glob(os.path.join(WORK, "ce_in_*.jsonl")) for l in open(f)}
    todo = [p for p in people() if em.get(p["Key"], {}).get("email") and p["Key"] not in done]
    todo.sort(key=lambda p: (p["Exhibitor ID"], int(p["Priority"])))
    nn = next_nn("ce")
    chunk = []

    def flush():
        nonlocal nn, chunk
        if chunk:
            path = os.path.join(WORK, f"ce_in_{nn:02d}.jsonl")
            with open(path, "w") as f:
                for x in chunk:
                    f.write(json.dumps(x, ensure_ascii=False) + "\n")
            print(f"wrote {len(chunk)} people to {path}")
            nn += 1
            chunk = []

    last = None
    for p in todo:
        if len(chunk) >= n and p["Exhibitor ID"] != last:  # keep a company's people in one chunk
            flush()
        e, a = m[p["Exhibitor ID"]], amz.get(p["Exhibitor ID"], {})
        b = a.get("best") or {}
        booth27 = re.search(r"2027: ([^;]+)", e["Booths"])
        chunk.append({"key": p["Key"], "id": p["Exhibitor ID"], "first_name": p["First Name"],
                      "last_name": p["Last Name"], "title": p["Title"], "company": e["Exhibitor"],
                      "years_exhibited": e["Years"], "booth_2027": booth27.group(1) if booth27 else "",
                      "brand": a.get("brand", ""), "amazon_store_name": b.get("store_name", ""),
                      "has_amazon_store": bool(b.get("has_store")), "amazon_status": a.get("status", ""),
                      "sample_product": b.get("title", "")[:120], "sold_by": b.get("sold_by", ""),
                      "monthly_revenue": ""})
        last = p["Exhibitor ID"]
    flush()


def status():
    from collections import Counter
    amz = amazon_best()
    t = targets()
    print("amazon (exhibitors checked):", dict(Counter(a["status"] for a in amz.values())))
    print(f"in scope: {len(t)} (2027 exhibitors: {sum(1 for x in t if x['in2027'])})")
    searched = {json.loads(l)["id"] for f in glob.glob(os.path.join(WORK, "sf_in_*.jsonl")) for l in open(f)}
    print(f"surfe searched: {len(searched)}; people selected: {len(people())}")
    em = emails()
    print(f"email lookups: {len(em)}, with email: {sum(1 for r in em.values() if r.get('email'))}")


if __name__ == "__main__":
    a = sys.argv[1:] or [""]
    if a[0] == "targets":
        for x in targets()[:20]:
            print(x)
        print(len(targets()))
    elif a[0] == "sf-export":
        sf_export(int(a[1]))
    elif a[0] == "sd-export":
        sd_export(int(a[1]))
    elif a[0] == "select":
        select()
    elif a[0] == "se-export":
        se_export(int(a[1]), int(a[2]))
    elif a[0] == "ce-export":
        ce_export(int(a[1]))
    elif a[0] == "status":
        status()
    else:
        print(__doc__)

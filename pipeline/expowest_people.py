"""Decision makers, emails and custom copy for Expo West exhibitors that sell on Amazon.

  python3 pipeline/expowest_people.py targets            exhibitors in scope, in priority order (printed summary)
  python3 pipeline/expowest_people.py sf-export N        next chunk of N in-scope exhibitors with no Surfe search yet
                                                          -> pipeline/work/sf_in_NN.jsonl
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


def targets():
    m, amz = master(), amazon_best()
    out = []
    for eid, a in amz.items():
        if a["status"] not in ("verified", "possible") or eid not in m:
            continue
        r = m[eid]
        if not r["Domain"]:
            continue
        b = a.get("best") or {}
        out.append({"id": eid, "name": r["Exhibitor"], "domain": r["Domain"], "brand": a["brand"],
                    "store": b.get("store_name", ""), "status": a["status"],
                    "in2027": r["In 2027"] == "Yes", "years": int(r["Years Count"] or 0)})
    out.sort(key=lambda t: (ORDER[t["status"]], not t["in2027"], -t["years"], t["id"]))
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


def select():
    raw = load("sf_raw_*.jsonl")
    names = {t["id"]: t for f in glob.glob(os.path.join(WORK, "sf_in_*.jsonl")) for t in map(json.loads, open(f))}
    by = {}
    for p in raw:
        p = {k: (p.get(k) or "") for k in ("id", "firstName", "lastName", "jobTitle", "linkedInUrl", "country",
                                            "seniorities", "companyName", "companyDomain", "pass")}
        p["sen"] = " ".join(p["seniorities"]).lower() if isinstance(p["seniorities"], list) else str(p["seniorities"]).lower()
        p["country"] = str(p["country"]).lower()
        t = p["jobTitle"]
        if p["pass"] == "error" or not p["firstName"] or not t:
            continue
        if EXCLUDE.search(t) or PRESIDENT.search(t) or not KEEP.search(t):
            continue
        if len(p["lastName"].rstrip(".")) <= 1:
            continue
        key = norm_li(p["linkedInUrl"]) or f'{p["firstName"]} {p["lastName"]}'.lower()
        by.setdefault(p["id"], {}).setdefault(key, p)
    fields = ["Key", "Exhibitor ID", "Exhibitor Name", "First Name", "Last Name", "Title", "LinkedIn URL",
              "Country", "Seniority", "Surfe Company", "Company Domain", "Priority"]
    rows = []
    for eid, d in by.items():
        for i, p in enumerate(sorted(d.values(), key=rank)[:5], 1):
            fix = lambda s: s.strip().title() if s.islower() or s.isupper() else s.strip()
            rows.append({"Key": f'{eid}|{norm_li(p["linkedInUrl"])}', "Exhibitor ID": eid,
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

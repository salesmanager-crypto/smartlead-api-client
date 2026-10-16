"""Sales, marketing and e-commerce decision makers per exhibitor from Surfe (no CEOs or founders).

  python surfe_people.py export N [IDS_FILE]   write pipeline/work/sf_in_XX.jsonl chunks of N exhibitors in scope
                                               (Brand / Manufacturer exhibitors, highest revenue first) that have
                                               no Surfe results yet
  python surfe_people.py select                pick up to 5 people per exhibitor from the raw Surfe candidates
                                               -> surfe_people.csv and surfe_companies.csv
  python surfe_people.py status

Agents (prompt pipeline/sf_agent_prompt.txt) call Surfe company enrichment (company LinkedIn page, size, HQ) and
Surfe people search filtered to sales / marketing / e-commerce titles, and append every candidate they get to
sf_raw_XX.jsonl and every company to sf_co_XX.jsonl. Selection is done here, in code, so the rules are the same
for every exhibitor.
"""
import glob, json, os, re, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
PEOPLE = os.path.join(ROOT, "surfe_people.csv")
COMPANIES = os.path.join(ROOT, "surfe_companies.csv")

# titles never kept: owners and the executive suite outside sales / marketing, plus junior and support roles
EXCLUDE = re.compile(
    r"\b(ceo|chief executive|founder|co-?founder|owner|chairman|chairwoman|board|cfo|coo|cto|cio|chief "
    r"(operating|financial|technology|information|people|legal|administrative|strategy|product)|"
    r"intern|assistant|coordinator|specialist|representative|rep\b|associate(?! director)|analyst|clerk|"
    r"admin|administrator|customer (service|care|support|success)|support|receptionist|driver|warehouse|"
    r"technician|engineer|designer|photographer|videographer|copywriter|writer|editor|recruit|human resources|"
    r"\bhr\b|account(ant|ing)|payable|receivable|purchasing|procurement|buyer|supply chain|logistics|quality|"
    r"inside sales|sales support|territory|student|retired|former|ex-)\b", re.I)
# "president" alone is an owner role; "vice president" is kept
PRESIDENT = re.compile(r"(?<!vice )(?<!vice-)\bpresident\b", re.I)
KEEP = re.compile(r"sales|marketing|e-?commerce|digital|amazon|marketplace|brand|national account|key account|"
                  r"business development|channel|revenue|commercial|growth|retail|merchandis|partnership|"
                  r"\bcmo\b|\bcro\b|\bcco\b|online|omni", re.I)


def rank(p):
    """Lower is better: e-commerce / Amazon first, then marketing leaders, then sales leaders."""
    t = p["jobTitle"].lower()
    func = 0 if re.search(r"e-?commerce|amazon|marketplace|digital|online|omni", t) else (
        1 if re.search(r"marketing|brand|growth|\bcmo\b", t) else 2)
    if re.search(r"\bchief\b|\bcmo\b|\bcro\b|\bcco\b", t):
        level = 0
    elif re.search(r"\b(svp|evp|vice president|vp)\b", t):
        level = 1
    elif re.search(r"\bhead\b|director", t):
        level = 2
    elif re.search(r"manager|lead\b", t):
        level = 3
    else:
        level = 4
    us = 0 if p["country"] in ("us", "") else 1
    return (us, level, func)


def targets():
    p2 = pd.read_excel(os.path.join(ROOT, "phase2_domains.xlsx"), sheet_name="Exhibitors", dtype=str).fillna("")
    p2 = p2[p2["Exhibitor Type"] == "Brand / Manufacturer"].set_index("Exhibitor ID")
    b = pd.read_excel(os.path.join(ROOT, "phase4_smartscout.xlsx"), sheet_name="Brands", dtype=str).fillna("")
    b = b[b["Exhibitor ID"].isin(p2.index) & b["Ownership"].isin(["Owned", "Licensed"])]
    b["rev"] = pd.to_numeric(b["Monthly Revenue"].str.replace(r"[$,]", "", regex=True), errors="coerce").fillna(0)
    g = b.groupby("Exhibitor ID").agg(rev=("rev", "sum"), brands=("Brand", lambda s: "; ".join(s)))
    g = g.join(p2[["Exhibitor Name", "Domain", "Parent Domain"]], how="left").sort_values("rev", ascending=False)
    return g


def export(n, ids_file=None):
    g = targets()
    if ids_file:
        want = [l.strip() for l in open(ids_file) if l.strip()]
        g = g.loc[[i for i in want if i in g.index]]
    done = set()
    for f in glob.glob(os.path.join(WORK, "sf_in_*.jsonl")):
        done |= {json.loads(l)["id"] for l in open(f)}
    rows = [{"id": i, "name": r["Exhibitor Name"], "domain": r["Domain"], "parent_domain": r["Parent Domain"],
             "brands": r["brands"], "monthly_revenue": int(r["rev"])}
            for i, r in g.iterrows() if i not in done]
    existing = glob.glob(os.path.join(WORK, "sf_in_*.jsonl"))
    k = max([int(os.path.basename(f)[6:8]) for f in existing] or [-1]) + 1
    made = []
    for s in range(0, len(rows), n):
        with open(os.path.join(WORK, f"sf_in_{k:02d}.jsonl"), "w") as fh:
            for r in rows[s:s + n]:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k += 1
    print(f"exported {len(rows)} exhibitors into chunks {' '.join(made)}")


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


def select():
    raw = load("sf_raw_*.jsonl")
    cos = load("sf_co_*.jsonl")
    ids = {json.loads(l)["id"]: json.loads(l) for f in glob.glob(os.path.join(WORK, "sf_in_*.jsonl")) for l in open(f)}
    by = {}
    for p in raw:
        p = {k: (p.get(k) or "") for k in ("id", "firstName", "lastName", "jobTitle", "linkedInUrl", "country",
                                            "seniorities", "departments", "companyName", "companyDomain", "pass")}
        p["sen"] = " ".join(p["seniorities"]).lower() if isinstance(p["seniorities"], list) else str(p["seniorities"]).lower()
        p["country"] = str(p["country"]).lower()
        t = p["jobTitle"]
        if not p["firstName"] or not t:
            continue
        if EXCLUDE.search(t) or PRESIDENT.search(t) or not KEEP.search(t):
            continue
        if len(p["lastName"].rstrip(".")) <= 1:
            continue  # surname shown as an initial only
        key = (p["id"], p["linkedInUrl"] or f'{p["firstName"]} {p["lastName"]}'.lower())
        by.setdefault(p["id"], {})[key] = p
    rows = []
    for eid, d in by.items():
        picks = sorted(d.values(), key=rank)[:5]
        for i, p in enumerate(picks, 1):
            rows.append({"Exhibitor ID": eid, "Exhibitor Name": ids.get(eid, {}).get("name", ""),
                         "First Name": p["firstName"].strip().title() if p["firstName"].islower() else p["firstName"].strip(),
                         "Last Name": p["lastName"].strip().title() if p["lastName"].islower() else p["lastName"].strip(),
                         "Title": p["jobTitle"].strip(), "LinkedIn URL": p["linkedInUrl"], "Country": p["country"].upper(),
                         "Seniority": p["sen"], "Surfe Company": p["companyName"], "Company Domain": p["companyDomain"],
                         "Priority": i, "Source": "Surfe people search"})
    pd.DataFrame(rows).to_csv(PEOPLE, index=False)
    c = pd.DataFrame(cos).drop_duplicates("id", keep="last") if cos else pd.DataFrame()
    c.to_csv(COMPANIES, index=False)
    n_ex = len(ids)
    got = pd.DataFrame(rows).groupby("Exhibitor ID").size() if rows else pd.Series(dtype=int)
    print(f"{len(rows)} people for {len(got)} of {n_ex} exhibitors; 5 people: {(got >= 5).sum()}; "
          f"companies enriched: {len(c)}")


def status():
    ins = glob.glob(os.path.join(WORK, "sf_in_*.jsonl"))
    for f in sorted(ins):
        k = os.path.basename(f)[6:8]
        n = sum(1 for _ in open(f))
        raw = os.path.join(WORK, f"sf_raw_{k}.jsonl")
        co = os.path.join(WORK, f"sf_co_{k}.jsonl")
        done = os.path.join(WORK, f"sf_done_{k}.txt")
        print(k, n, "raw", sum(1 for _ in open(raw)) if os.path.exists(raw) else 0,
              "co", sum(1 for _ in open(co)) if os.path.exists(co) else 0, "DONE" if os.path.exists(done) else "")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "select":
        select()
    else:
        status()

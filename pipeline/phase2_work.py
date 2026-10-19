"""Phase 2 research work units.

  export N   write pipeline/work/p2_in_XX.jsonl chunks of N exhibitors not yet in
             phase2_checkpoint.csv and not already in a pending chunk
  collect    append rows from pipeline/work/p2_out_XX.csv to phase2_checkpoint.csv
             (validated, one row per Exhibitor ID, first answer wins)
  status     counts

Agents (called by the orchestrating session) read p2_in files, run the web searches,
and write p2_out files. The checkpoint is the resume point for new sessions.
"""
import csv, glob, json, os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NON_COMPANY_DOMAINS, ROOT, domain_of

WORK = os.path.join(ROOT, "pipeline", "work")
CP = os.path.join(ROOT, "phase2_checkpoint.csv")
OUT_FIELDS = ["Exhibitor ID", "Domain Found", "Domain Source", "Exhibitor Type", "Type Reason",
              "Parent Company", "Parent Domain", "Parent Source", "Parent Query", "Notes"]
TYPES = {"Brand / Manufacturer", "Distributor / Wholesaler", "Service / Software / Media / Association",
         "Tool & Equipment / Shop Supplier", "Unclear"}


def company_host(url):
    d = domain_of(url)
    if not d:
        return ""
    for bad in NON_COMPANY_DOMAINS:
        if d == bad or d.endswith("." + bad):
            return ""
    return d


def done_ids():
    if not os.path.exists(CP):
        return set()
    return set(pd.read_csv(CP, dtype=str, keep_default_na=False)["Exhibitor ID"])


def pending_ids():
    ids = set()
    for f in glob.glob(os.path.join(WORK, "p2_in_*.jsonl")):
        with open(f) as fh:
            for line in fh:
                ids.add(json.loads(line)["id"])
    return ids


def export(chunk):
    ex = pd.read_excel(os.path.join(ROOT, "phase1_exhibitors.xlsx"), sheet_name="Exhibitors",
                       dtype=str).fillna("")
    import gzip
    from phase2_fetch_sites import SITE_CACHE, signals
    skip = done_ids() | pending_ids()
    items = []
    for r in ex.to_dict("records"):
        eid = r["Exhibitor ID"]
        if eid in skip:
            continue
        host = company_host(r["Website"])
        s = {}
        if host:
            cpath = os.path.join(SITE_CACHE, host + ".json.gz")
            if not os.path.exists(cpath):
                continue  # site not fetched yet; export it in a later round
            with gzip.open(cpath, "rt", encoding="utf-8") as fh:
                s = signals(json.load(fh))
        site_bits = " | ".join(x for x in [s.get("Site Title", ""), s.get("Site Description", "")] if x)
        items.append({
            "id": eid, "name": r["Exhibitor Name"], "website": r["Website"], "domain": host,
            "needs_domain": not host,
            "shows": r["Shows"], "summary": r["About Summary"] or r["About"][:400],
            "categories": r["Categories"][:400], "show_brands": r["Show Brands"][:300],
            "linkedin": r["LinkedIn"],
            "site": (site_bits + " || " + s.get("Site Snippet", "")[:350])[:600] if s else "",
            "site_about_url": s.get("About URL", ""),
            "site_status": s.get("Site Status", ""), "site_error": s.get("Site Error", "")[:120],
            "parent_hints": s.get("Parent Hints", "")[:900],
        })
    existing = glob.glob(os.path.join(WORK, "p2_in_*.jsonl"))
    n = max([int(os.path.basename(f)[6:8]) for f in existing] or [-1]) + 1
    made = []
    for i in range(0, len(items), chunk):
        path = os.path.join(WORK, f"p2_in_{n:02d}.jsonl")
        with open(path, "w") as fh:
            for it in items[i:i + chunk]:
                fh.write(json.dumps(it, ensure_ascii=False) + "\n")
        made.append(f"{n:02d}")
        n += 1
    print(f"exported {len(items)} exhibitors into chunks: {' '.join(made)}")


def collect():
    have = done_ids()
    new = not os.path.exists(CP)
    added, bad = 0, []
    with open(CP, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS + ["Chunk"], extrasaction="ignore")
        if new:
            w.writeheader()
        for path in sorted(glob.glob(os.path.join(WORK, "p2_out_*.csv"))):
            chunk = os.path.basename(path)[7:9]
            with open(path, newline="", encoding="utf-8") as fh:
                for r in csv.DictReader(fh):
                    eid = (r.get("Exhibitor ID") or "").strip()
                    if not eid or eid in have:
                        continue
                    if r.get("Exhibitor Type", "").strip() not in TYPES:
                        bad.append((chunk, eid, r.get("Exhibitor Type")))
                        continue
                    r = {k: (r.get(k) or "").strip().replace("—", ", ").replace("–", "-")
                         for k in OUT_FIELDS}
                    r["Chunk"] = chunk
                    w.writerow(r)
                    have.add(eid)
                    added += 1
        f.flush()
    print(f"collected {added} new rows; checkpoint now {len(have)}; rejected {len(bad)} {bad[:5]}")


def status():
    ex = pd.read_excel(os.path.join(ROOT, "phase1_exhibitors.xlsx"), sheet_name="Exhibitors", dtype=str)
    d = done_ids()
    print(f"phase 2: {len(d)} of {len(ex)} done")
    for f in sorted(glob.glob(os.path.join(WORK, "p2_in_*.jsonl"))):
        n = os.path.basename(f)[6:8]
        ids = [json.loads(l)["id"] for l in open(f)]
        out = os.path.join(WORK, f"p2_out_{n}.csv")
        got = len(pd.read_csv(out, dtype=str)) if os.path.exists(out) else 0
        print(f"  chunk {n}: {len(ids)} in, {got} out, {sum(i in d for i in ids)} collected")


if __name__ == "__main__":
    {"export": lambda: export(int(sys.argv[2])), "collect": collect, "status": status}[sys.argv[1]]()

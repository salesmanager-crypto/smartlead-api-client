"""Phase 5 work units: decision makers from public LinkedIn search results (web search, unverified).

  export N [M]  write pipeline/work/p5_in_XX.jsonl chunks of N exhibitors (the next M by revenue
                that are not yet in phase5_checkpoint.csv or a pending chunk)
  collect       append rows from pipeline/work/p5_out_XX.csv to phase5_checkpoint.csv
  status
"""
import csv, glob, json, os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
CP = os.path.join(ROOT, "phase5_checkpoint.csv")
FIELDS = ["Exhibitor ID", "Company LinkedIn", "Name", "Title (as shown)", "LinkedIn URL", "Priority",
          "Match Reason", "Search Query", "Confidence", "Notes"]


def targets():
    """Exhibitors with any Amazon brand (Yes or Possible), largest combined revenue first."""
    r3 = pd.read_excel(os.path.join(ROOT, "phase3_brands_amazon.xlsx"), sheet_name="Exhibitor Rollup",
                       dtype=str).fillna("")
    r3 = r3[r3["Any Brand On Amazon"].isin(["Yes", "Possible"])]
    r4 = pd.read_excel(os.path.join(ROOT, "phase4_smartscout.xlsx"), sheet_name="Exhibitor Rollup")
    rev = dict(zip(r4["Exhibitor ID"], r4["Total Monthly Revenue"]))
    p1 = pd.read_excel(os.path.join(ROOT, "phase1_exhibitors.xlsx"), sheet_name="Exhibitors",
                       dtype=str).fillna("").set_index("Exhibitor ID")
    out = []
    for r in r3.to_dict("records"):
        eid = r["Exhibitor ID"]
        m = rev.get(eid) or 0.0
        size = "small" if m < 200_000 else "mid/large"
        out.append({"id": eid, "name": r["Exhibitor Name"], "domain": r["Domain"], "parent": r["Parent Company"],
                    "brands": r["Amazon Brand List"], "monthly_revenue": round(float(m)),
                    "size": size, "company_linkedin": p1.at[eid, "LinkedIn"] if eid in p1.index else "",
                    "about": (p1.at[eid, "About Summary"] if eid in p1.index else "")[:250]})
    out.sort(key=lambda x: -x["monthly_revenue"])
    return out


def done_ids():
    if not os.path.exists(CP):
        return set()
    df = pd.read_csv(CP, dtype=str, keep_default_na=False)
    # exhibitors whose only rows say "Not searched" are not done: a later session can search them
    real = df[~df["Notes"].str.startswith("Not searched")]
    return set(real["Exhibitor ID"])


def pending_ids(include_all=False):
    """Exhibitors in an input chunk that has no output yet (still being worked)."""
    s = set()
    for f in glob.glob(os.path.join(WORK, "p5_in_*.jsonl")):
        n = os.path.basename(f)[6:8]
        if include_all or not os.path.exists(os.path.join(WORK, f"p5_out_{n}.csv")):
            s |= {json.loads(l)["id"] for l in open(f)}
    return s


def export(chunk, limit):
    skip = done_ids() | pending_ids()
    items = [t for t in targets() if t["id"] not in skip][:limit]
    existing = glob.glob(os.path.join(WORK, "p5_in_*.jsonl"))
    n = max([int(os.path.basename(f)[6:8]) for f in existing] or [-1]) + 1
    made = []
    for i in range(0, len(items), chunk):
        with open(os.path.join(WORK, f"p5_in_{n:02d}.jsonl"), "w") as fh:
            for it in items[i:i + chunk]:
                fh.write(json.dumps(it, ensure_ascii=False) + "\n")
        made.append(f"{n:02d}")
        n += 1
    print(f"exported {len(items)} exhibitors into chunks {' '.join(made)}")


def collect():
    have = set(pd.read_csv(CP, dtype=str, keep_default_na=False)["Exhibitor ID"]) if os.path.exists(CP) else set()
    new = not os.path.exists(CP)
    added = 0
    with open(CP, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS + ["Chunk"], extrasaction="ignore")
        if new:
            w.writeheader()
        for path in sorted(glob.glob(os.path.join(WORK, "p5_out_*.csv"))):
            chunk = os.path.basename(path)[7:9]
            df = pd.read_csv(path, dtype=str, keep_default_na=False)
            in_path = os.path.join(WORK, f"p5_in_{chunk}.jsonl")
            order = [json.loads(l)["id"] for l in open(in_path)]
            present = [i for i in order if i in set(df["Exhibitor ID"])]
            finished = set(present[:-1]) if len(present) < len(order) else set(present)
            for eid, g in df.groupby("Exhibitor ID", sort=False):
                if eid in have or eid not in finished:
                    continue
                for r in g.to_dict("records"):
                    r = {k: (r.get(k) or "").strip().replace("—", ", ").replace("–", "-") for k in FIELDS}
                    r["Chunk"] = chunk
                    w.writerow(r)
                have.add(eid)
                added += 1
    print(f"collected {added} exhibitors; checkpoint {len(have)}")


def status():
    d = done_ids()
    print(f"phase 5: {len(d)} exhibitors with rows; {len(targets())} targets")
    for f in sorted(glob.glob(os.path.join(WORK, "p5_in_*.jsonl"))):
        ids = [json.loads(l)["id"] for l in open(f)]
        print(f"  {os.path.basename(f)}: {len(ids)} in, {sum(i in d for i in ids)} collected")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 10**9)
    else:
        {"collect": collect, "status": status}[cmd]()

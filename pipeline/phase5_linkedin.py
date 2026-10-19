"""Phase 5 company LinkedIn URLs: one linkedin.com/company URL per exhibitor with an Amazon brand.

  export N M   write pipeline/work/p5l_in_XX.jsonl chunks of N exhibitors: the next M target exhibitors
               (Amazon brand in SmartScout, largest revenue first) with no Company LinkedIn on file
  collect      merge p5l_out_XX.csv into phase5_company_linkedin.csv
  status
"""
import csv, glob, json, os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT
from phase5_work import CP, WORK, targets

OUT = os.path.join(ROOT, "phase5_company_linkedin.csv")
FIELDS = ["Exhibitor ID", "Company LinkedIn", "LinkedIn Company Name", "Match Reason", "Search Query", "Notes"]


def read(path, cols):
    return pd.read_csv(path, dtype=str, keep_default_na=False) if os.path.exists(path) else pd.DataFrame(columns=cols)


def known():
    """Exhibitor ID -> company LinkedIn URL from the show page, the people search, or this step."""
    urls = {}
    cp = read(CP, ["Exhibitor ID", "Company LinkedIn"])
    for r in cp.to_dict("records"):
        if r["Company LinkedIn"]:
            urls.setdefault(r["Exhibitor ID"], r["Company LinkedIn"])
    for r in read(OUT, FIELDS).to_dict("records"):
        if r["Company LinkedIn"]:
            urls[r["Exhibitor ID"]] = r["Company LinkedIn"]
    return urls


def export(chunk, limit):
    urls = known()
    done = set(read(OUT, FIELDS)["Exhibitor ID"])
    pending = set()
    for f in glob.glob(os.path.join(WORK, "p5l_in_*.jsonl")):
        n = os.path.basename(f)[7:9]
        if not os.path.exists(os.path.join(WORK, f"p5l_out_{n}.csv")):
            pending |= {json.loads(l)["id"] for l in open(f)}
    items = []
    for t in targets():
        if not t["brands"] or t["company_linkedin"] or t["id"] in urls or t["id"] in done or t["id"] in pending:
            continue
        items.append({k: t[k] for k in ("id", "name", "domain", "parent", "brands", "monthly_revenue", "about")})
        if len(items) >= limit:
            break
    existing = glob.glob(os.path.join(WORK, "p5l_in_*.jsonl"))
    n = max([int(os.path.basename(f)[7:9]) for f in existing] or [-1]) + 1
    made = []
    for i in range(0, len(items), chunk):
        with open(os.path.join(WORK, f"p5l_in_{n:02d}.jsonl"), "w") as fh:
            for it in items[i:i + chunk]:
                fh.write(json.dumps(it, ensure_ascii=False) + "\n")
        made.append(f"{n:02d}")
        n += 1
    print(f"exported {len(items)} exhibitors into chunks {' '.join(made)}")


def collect():
    have = set(read(OUT, FIELDS)["Exhibitor ID"])
    new = not os.path.exists(OUT)
    added = found = 0
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS + ["Chunk"], extrasaction="ignore")
        if new:
            w.writeheader()
        for path in sorted(glob.glob(os.path.join(WORK, "p5l_out_*.csv"))):
            chunk = os.path.basename(path)[8:10]
            for r in pd.read_csv(path, dtype=str, keep_default_na=False).to_dict("records"):
                if r["Exhibitor ID"] in have:
                    continue
                r = {k: (r.get(k) or "").strip().replace("—", ", ").replace("–", "-") for k in FIELDS}
                r["Chunk"] = chunk
                w.writerow(r)
                have.add(r["Exhibitor ID"])
                added += 1
                found += bool(r["Company LinkedIn"])
    print(f"collected {added} exhibitors ({found} with a URL); file {len(have)}")


def status():
    urls = known()
    t = [x for x in targets() if x["brands"]]
    print(f"exhibitors with Amazon brands: {len(t)}; with company LinkedIn: {sum(x['id'] in urls or bool(x['company_linkedin']) for x in t)}")
    for f in sorted(glob.glob(os.path.join(WORK, "p5l_in_*.jsonl"))):
        n = os.path.basename(f)[7:9]
        ids = [json.loads(l)["id"] for l in open(f)]
        out = os.path.join(WORK, f"p5l_out_{n}.csv")
        got = len(read(out, FIELDS)) if os.path.exists(out) else 0
        print(f"  chunk {n}: {len(ids)} in, {got} out")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(int(sys.argv[2]), int(sys.argv[3]))
    else:
        {"collect": collect, "status": status}[cmd]()

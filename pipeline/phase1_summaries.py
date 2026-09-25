"""About Summary helper for phase 1.

  export N   write unique, not-yet-summarized About texts from phase1_checkpoint.csv into
             pipeline/work/summ_in_XX.jsonl chunks of N items
  collect    fold pipeline/work/summ_out_XX.csv files into pipeline/work/summaries.csv

Summaries are keyed by a hash of the About text, so identical text in both shows is
summarized once and a rerun never redoes finished items.
"""
import csv, glob, json, os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT
from phase1_build import about_key

WORK = os.path.join(ROOT, "pipeline", "work")
SUMMARIES = os.path.join(WORK, "summaries.csv")
CP_PATH = os.path.join(ROOT, "phase1_checkpoint.csv")


def done_keys():
    if not os.path.exists(SUMMARIES):
        return set()
    return set(pd.read_csv(SUMMARIES, dtype=str, keep_default_na=False)["about_key"])


def export(chunk):
    os.makedirs(WORK, exist_ok=True)
    df = pd.read_csv(CP_PATH, dtype=str, keep_default_na=False)
    done = done_keys()
    pending = set()
    for f in glob.glob(os.path.join(WORK, "summ_in_*.jsonl")):
        with open(f) as fh:
            pending |= {json.loads(l)["about_key"] for l in fh}
    items, seen = [], set()
    for r in df.to_dict("records"):
        if not r["About"].strip():
            continue
        k = about_key(r["About"])
        if k in done or k in pending or k in seen:
            continue
        seen.add(k)
        items.append({"about_key": k, "name": r["Exhibitor Name"], "categories": r["Categories"],
                      "about": r["About"][:2500]})
    existing = glob.glob(os.path.join(WORK, "summ_in_*.jsonl"))
    n = max([int(os.path.basename(f)[8:10]) for f in existing] or [-1]) + 1
    files = []
    for i in range(0, len(items), chunk):
        path = os.path.join(WORK, f"summ_in_{n:02d}.jsonl")
        with open(path, "w") as fh:
            for it in items[i:i + chunk]:
                fh.write(json.dumps(it, ensure_ascii=False) + "\n")
        files.append((path, len(items[i:i + chunk])))
        n += 1
    for p, c in files:
        print(p, c)
    print(f"exported {len(items)} items in {len(files)} chunks")


def collect():
    rows = {}
    if os.path.exists(SUMMARIES):
        for r in pd.read_csv(SUMMARIES, dtype=str, keep_default_na=False).to_dict("records"):
            rows[r["about_key"]] = r["summary"]
    for f in sorted(glob.glob(os.path.join(WORK, "summ_out_*.csv"))):
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                s = (r.get("summary") or "").replace("—", ", ").replace("–", "-").strip()
                if r.get("about_key") and s:
                    rows[r["about_key"]] = s
    pd.DataFrame({"about_key": list(rows), "summary": list(rows.values())}).to_csv(SUMMARIES, index=False)
    print(f"summaries on file: {len(rows)}")


if __name__ == "__main__":
    if sys.argv[1] == "export":
        export(int(sys.argv[2]))
    else:
        collect()

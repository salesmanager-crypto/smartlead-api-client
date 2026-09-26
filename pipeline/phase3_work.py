"""Phase 3 work units: brands owned + SmartScout presence.

  export N   write pipeline/work/p3_in_XX.jsonl chunks of N Research-scope exhibitors not yet in
             phase3_checkpoint.csv and not in a pending chunk
  collect    move finished exhibitors from pipeline/work/p3_out_XX.csv into phase3_checkpoint.csv
             (all brand rows of an exhibitor together) and merge ss_raw_XX.jsonl into
             smartscout_cache.json (keyed by brand)
  status     counts
"""
import csv, glob, json, os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
CP = os.path.join(ROOT, "phase3_checkpoint.csv")
SS_CACHE = os.path.join(ROOT, "smartscout_cache.json")
FIELDS = ["Exhibitor ID", "Brand", "Brand Source", "Amazon Check Method", "SmartScout Brand",
          "SmartScout Match", "SS Primary Category", "SS Primary Subcategory", "SS Monthly Revenue",
          "Amazon URL", "Amazon Sold By", "Amazon Confidence", "On Amazon", "Notes"]
MATCHES = {"exact", "close", "wrong match", "not found", ""}


def done_ids():
    if not os.path.exists(CP):
        return set()
    return set(pd.read_csv(CP, dtype=str, keep_default_na=False)["Exhibitor ID"])


def pending_ids():
    ids = set()
    for f in glob.glob(os.path.join(WORK, "p3_in_*.jsonl")):
        with open(f) as fh:
            ids |= {json.loads(l)["id"] for l in fh}
    return ids


def export(chunk):
    p2 = pd.read_excel(os.path.join(ROOT, "phase2_domains.xlsx"), sheet_name="Exhibitors",
                       dtype=str).fillna("")
    p2 = p2[p2["Phase 3 Scope"] == "Research"]
    bp_path = os.path.join(WORK, "brand_pages.csv")
    bp = pd.read_csv(bp_path, dtype=str, keep_default_na=False) if os.path.exists(bp_path) else pd.DataFrame(
        columns=["Exhibitor ID"])
    bp_by = {k: g.to_dict("records") for k, g in bp.groupby("Exhibitor ID")}
    skip = done_ids() | pending_ids()
    items = []
    for r in p2.to_dict("records"):
        if r["Exhibitor ID"] in skip:
            continue
        pages = []
        for b in bp_by.get(r["Exhibitor ID"], []):
            pages.append({"url": b["URL"], "image_alts": b["Alts"][:500], "headings": b["Headings"][:300],
                          "links": b["Links"][:600], "text": b["Text"][:400]})
        items.append({
            "id": r["Exhibitor ID"], "name": r["Exhibitor Name"], "domain": r["Domain"],
            "website": r["Website"], "type": r["Exhibitor Type"], "type_reason": r["Type Reason"],
            "summary": r["About Summary"], "about": r["About"][:700], "categories": r["Categories"][:300],
            "show_brands": r["Show Brands"], "parent": r["Parent Company"],
            "brand_links": " || ".join(p.split(" -> ")[0] for p in r["Site Brand Links"].split(" || ") if p)[:300],
            "brand_pages": pages,
        })
    existing = glob.glob(os.path.join(WORK, "p3_in_*.jsonl"))
    n = max([int(os.path.basename(f)[6:8]) for f in existing] or [-1]) + 1
    made = []
    for i in range(0, len(items), chunk):
        path = os.path.join(WORK, f"p3_in_{n:02d}.jsonl")
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
        w = csv.DictWriter(f, fieldnames=FIELDS + ["Chunk"], extrasaction="ignore")
        if new:
            w.writeheader()
        for path in sorted(glob.glob(os.path.join(WORK, "p3_out_*.csv"))):
            chunk = os.path.basename(path)[7:9]
            in_path = os.path.join(WORK, f"p3_in_{chunk}.jsonl")
            order = [json.loads(l)["id"] for l in open(in_path)] if os.path.exists(in_path) else []
            df = pd.read_csv(path, dtype=str, keep_default_na=False)
            # an exhibitor is finished once a later exhibitor in the chunk has rows (or the chunk is done)
            present = [i for i in order if i in set(df["Exhibitor ID"])]
            finished = set(present[:-1]) if len(present) < len(order) else set(present)
            for eid, g in df.groupby("Exhibitor ID", sort=False):
                if eid in have or eid not in finished:
                    continue
                if not set(g["SmartScout Match"].str.strip()) <= MATCHES:
                    bad.append((chunk, eid))
                    continue
                for r in g.to_dict("records"):
                    r = {k: (r.get(k) or "").strip().replace("—", ", ").replace("–", "-") for k in FIELDS}
                    r["Chunk"] = chunk
                    w.writerow(r)
                have.add(eid)
                added += 1
    cache = json.load(open(SS_CACHE)) if os.path.exists(SS_CACHE) else {}
    for path in glob.glob(os.path.join(WORK, "ss_raw_*.jsonl")):
        with open(path) as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                name = row.get("Brand Name")
                if name:
                    cache.setdefault(name, {})["profile"] = row
    with open(SS_CACHE, "w") as fh:
        json.dump(cache, fh)
    print(f"collected {added} exhibitors; checkpoint {len(have)} exhibitors; rejected {bad[:5]}; "
          f"smartscout_cache brands {len(cache)}")


def status():
    d = done_ids()
    print(f"phase 3: {len(d)} exhibitors done")
    for f in sorted(glob.glob(os.path.join(WORK, "p3_in_*.jsonl"))):
        n = os.path.basename(f)[6:8]
        ids = [json.loads(l)["id"] for l in open(f)]
        out = os.path.join(WORK, f"p3_out_{n}.csv")
        got = pd.read_csv(out, dtype=str)["Exhibitor ID"].nunique() if os.path.exists(out) else 0
        print(f"  chunk {n}: {len(ids)} in, {got} out, {sum(i in d for i in ids)} collected")


if __name__ == "__main__":
    {"export": lambda: export(int(sys.argv[2])), "collect": collect, "status": status}[sys.argv[1]]()

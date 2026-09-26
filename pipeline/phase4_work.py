"""Phase 4 work units: SmartScout sellers + top subcategories (+ rank) per Amazon brand.

  export N   write pipeline/work/p4_in_XX.jsonl chunks of N SmartScout brands (On Amazon = Yes,
             SmartScout Match exact/close, current products > 0) not yet in phase4_checkpoint.jsonl
  collect    merge pipeline/work/p4_raw_XX.jsonl into phase4_checkpoint.jsonl (one JSON per brand)
             and into smartscout_cache.json; merge subcategory rank lists into
             pipeline/work/subcat_rank_cache.json
  status
"""
import glob, json, os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
CP = os.path.join(ROOT, "phase4_checkpoint.jsonl")
SS_CACHE = os.path.join(ROOT, "smartscout_cache.json")
RANK_CACHE = os.path.join(WORK, "subcat_rank_cache.json")


def done():
    if not os.path.exists(CP):
        return {}
    out = {}
    with open(CP) as f:
        for line in f:
            r = json.loads(line)
            out[r["brand"].lower()] = r
    return out


def pending():
    s = set()
    for f in glob.glob(os.path.join(WORK, "p4_in_*.jsonl")):
        s |= {json.loads(l)["brand"].lower() for l in open(f)}
    return s


def target_brands():
    b = pd.read_excel(os.path.join(ROOT, "phase3_brands_amazon.xlsx"), sheet_name="Brands", dtype=str).fillna("")
    b = b[(b["On Amazon"] == "Yes") & b["SmartScout Match"].isin(["exact", "close"]) & (b["SmartScout Brand"] != "")]
    groups = {}
    for r in b.to_dict("records"):
        g = groups.setdefault(r["SmartScout Brand"], {"brand": r["SmartScout Brand"], "exhibitors": [], "brand_names": set()})
        g["exhibitors"].append(f"{r['Exhibitor ID']} {r['Exhibitor Name']}")
        g["brand_names"].add(r["Brand"])
    return groups


def export(chunk):
    cache = json.load(open(SS_CACHE)) if os.path.exists(SS_CACHE) else {}
    skip = set(done()) | pending()
    items = []
    for name, g in sorted(target_brands().items()):
        if name.lower() in skip:
            continue
        prof = cache.get(name, {}).get("profile", {})
        items.append({"brand": name, "exhibitors": g["exhibitors"][:5], "brand_names": sorted(g["brand_names"]),
                      "has_profile": bool(prof), "single_seller": prof.get("Single Seller Name", "")})
    existing = glob.glob(os.path.join(WORK, "p4_in_*.jsonl"))
    n = max([int(os.path.basename(f)[6:8]) for f in existing] or [-1]) + 1
    made = []
    for i in range(0, len(items), chunk):
        with open(os.path.join(WORK, f"p4_in_{n:02d}.jsonl"), "w") as fh:
            for it in items[i:i + chunk]:
                fh.write(json.dumps(it, ensure_ascii=False) + "\n")
        made.append(f"{n:02d}")
        n += 1
    print(f"exported {len(items)} brands into chunks: {' '.join(made)}")


def collect():
    """Rebuild phase4_checkpoint.jsonl from all raw files; per brand prefer the record with data."""
    cache = json.load(open(SS_CACHE)) if os.path.exists(SS_CACHE) else {}
    ranks = json.load(open(RANK_CACHE)) if os.path.exists(RANK_CACHE) else {}
    best = {}
    for path in sorted(glob.glob(os.path.join(WORK, "p4_raw_*.jsonl"))):
        for line in open(path):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = (r.get("brand") or "").lower()
            if not key:
                continue
            for sub, lst in (r.get("subcat_lists") or {}).items():
                ranks.setdefault(sub, lst)
            score = bool(r.get("sellers")) + bool(r.get("subcats"))
            if key not in best or score >= best[key][0]:
                best[key] = (score, {k: v for k, v in r.items() if k != "subcat_lists"})
    with open(CP + ".tmp", "w") as out:
        for key, (score, r) in best.items():
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
            c = cache.setdefault(r["brand"], {})
            if r.get("profile"):
                c["profile"] = r["profile"]
            c["sellers"] = r.get("sellers", [])
            c["subcats"] = r.get("subcats", [])
    os.replace(CP + ".tmp", CP)
    json.dump(cache, open(SS_CACHE, "w"))
    json.dump(ranks, open(RANK_CACHE, "w"))
    print(f"checkpoint {len(best)} brands; subcategory rank lists {len(ranks)}")


def status():
    d = done()
    print(f"phase 4: {len(d)} of {len(target_brands())} brands done")
    for f in sorted(glob.glob(os.path.join(WORK, "p4_in_*.jsonl"))):
        n = os.path.basename(f)[6:8]
        names = [json.loads(l)["brand"].lower() for l in open(f)]
        print(f"  chunk {n}: {len(names)} in, {sum(x in d for x in names)} collected")


if __name__ == "__main__":
    {"export": lambda: export(int(sys.argv[2])), "collect": collect, "status": status}[sys.argv[1]]()

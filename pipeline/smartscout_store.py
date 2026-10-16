"""SmartScout data keyed on the exact Amazon store name verified by amazon_store.py.

  python smartscout_store.py plan N   for every verified / possible brand, look up its Amazon store name (then
                                      the Amazon brand field) in smartscout_cache.json; names not cached go to
                                      pipeline/work/ssx_in_XX.jsonl chunks of N names for a SmartScout pull
  python smartscout_store.py build    merge cache + ssx_raw_XX.jsonl -> smartscout_store.csv (one row per brand key)
  python smartscout_store.py status

Agents (prompt pipeline/ssx_agent_prompt.txt) run the saved "Full profile of the brand <X>" query with the store
names as filterValues and append every returned row to ssx_raw_XX.jsonl. A name SmartScout does not return is
"not in SmartScout"; the brand still counts as on Amazon because the store was seen on amazon.com.
"""
import glob, json, os, re, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
OUT = os.path.join(ROOT, "smartscout_store.csv")
CACHE = os.path.join(ROOT, "smartscout_cache.json")


def key(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def cache_index():
    c = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    for r in raw_rows():
        c.setdefault(r["Brand Name"], {})["profile"] = r
    return c, {key(k): k for k in c}


def raw_rows():
    out = []
    for f in sorted(glob.glob(os.path.join(WORK, "ssx_raw_*.jsonl"))):
        for l in open(f):
            l = l.strip()
            if l:
                try:
                    r = json.loads(l)
                except json.JSONDecodeError:
                    continue
                if r.get("Brand Name"):
                    out.append(r)
    return out


def queried():
    q = set()
    for f in glob.glob(os.path.join(WORK, "ssx_in_*.jsonl")):
        q |= {key(json.loads(l)["name"]) for l in open(f)}
    return q


def stores():
    a = pd.read_csv(os.path.join(ROOT, "amazon_stores.csv"), dtype=str).fillna("")
    return a[a["Amazon Status"].isin(["verified", "possible"])]


def plan(n):
    c, idx = cache_index()
    done = queried()
    want = []
    for _, r in stores().iterrows():
        names = [x for x in (r["Amazon Store Name"], r["Amazon Brand Field"]) if x]
        if any(key(x) in idx for x in names):
            continue
        for x in names:
            if key(x) not in done and key(x) not in {key(w) for w in want}:
                want.append(x)
    existing = glob.glob(os.path.join(WORK, "ssx_in_*.jsonl"))
    k = max([int(os.path.basename(f)[7:9]) for f in existing] or [-1]) + 1
    made = []
    for s in range(0, len(want), n):
        with open(os.path.join(WORK, f"ssx_in_{k:02d}.jsonl"), "w") as fh:
            for x in want[s:s + n]:
                fh.write(json.dumps({"name": x}, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k += 1
    print(f"{len(want)} store names to pull into chunks {' '.join(made) or '(none)'}")


def build():
    c, idx = cache_index()
    done = queried()
    rows = []
    for _, r in stores().iterrows():
        hit, basis = None, ""
        for label, x in (("store name", r["Amazon Store Name"]), ("Amazon brand field", r["Amazon Brand Field"])):
            if x and key(x) in idx:
                hit, basis = c[idx[key(x)]], label
                break
        out = {"Key": r["Key"], "Exhibitor ID": r["Exhibitor ID"], "Brand": r["Brand"],
               "Amazon Store Name": r["Amazon Store Name"]}
        if not hit:
            names = [x for x in (r["Amazon Store Name"], r["Amazon Brand Field"]) if x]
            out["SmartScout Match"] = ("not in SmartScout" if names and all(key(x) in done for x in names)
                                       else "pending pull")
            rows.append(out)
            continue
        p, sellers, subs = hit.get("profile") or {}, hit.get("sellers") or [], hit.get("subcats") or []
        out.update({"SmartScout Brand": p.get("Brand Name", ""), "SmartScout Match": f"exact on {basis}",
                    "Monthly Revenue": p.get("Total Monthly Revenue", ""),
                    "Annual Revenue (TTM)": p.get("Trailing 12-Month Revenue", ""),
                    "Primary Category": p.get("Primary Category", ""),
                    "Primary Subcategory": p.get("Primary Subcategory", ""),
                    "Total Products": p.get("Total Products", ""), "Average Rating": p.get("Average Rating", ""),
                    "Average Sellers": p.get("Average Sellers", ""), "Has Storefront": p.get("Has Storefront", ""),
                    "Single Seller Name": p.get("Single Seller Name", "")})
        if sellers:
            top = max(sellers, key=lambda s: s.get("Estimated Brand Share") or 0)
            out.update({"Dominant Seller": top.get("Seller Name", ""),
                        "Dominant Seller Sales %": top.get("Estimated Brand Share", ""),
                        "Dominant Seller Type": top.get("Type", ""),
                        "Reseller Share %": round(sum(s.get("Estimated Brand Share") or 0 for s in sellers
                                                      if s.get("Type") == "Third-party reseller"), 1)})
        for i, s in enumerate(subs[:3], 1):
            out.update({f"Top Subcategory {i}": s.get("Subcategory", ""), f"Sub {i} Market Share": s.get("Market Share", ""),
                        f"Sub {i} Brand Rank": s.get("Rank", "")})
        rows.append(out)
    d = pd.DataFrame(rows)
    d.to_csv(OUT, index=False)
    print(d["SmartScout Match"].value_counts().to_string())


def status():
    for f in sorted(glob.glob(os.path.join(WORK, "ssx_in_*.jsonl"))):
        k = os.path.basename(f)[7:9]
        o = os.path.join(WORK, f"ssx_raw_{k}.jsonl")
        print(k, sum(1 for _ in open(f)), "raw", sum(1 for _ in open(o)) if os.path.exists(o) else 0,
              "DONE" if os.path.exists(os.path.join(WORK, f"ssx_done_{k}.txt")) else "")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "plan":
        plan(int(sys.argv[2]))
    elif cmd == "build":
        build()
    else:
        status()

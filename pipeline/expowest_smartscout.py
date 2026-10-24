"""SmartScout brand profiles for the Expo West Amazon brands, keyed on the exact Amazon store name.

  python3 pipeline/expowest_smartscout.py plan N   store names (then Amazon brand fields) of every campaign brand not yet
                                                   queried -> pipeline/work/ssx_in_NN.jsonl chunks of N names
  python3 pipeline/expowest_smartscout.py build    ssx_raw_NN.jsonl -> smartscout_brands.csv (one row per exhibitor ID)
  python3 pipeline/expowest_smartscout.py status

Agents (pipeline/ssx_agent_prompt.txt) run the saved "Full profile of the brand <X>" query with the names as
filterValues and append every returned row. A name SmartScout does not return is "not in SmartScout": the brand is
still on Amazon, because the store was seen on amazon.com.
"""
import csv, glob, html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
MASTER = os.path.join(ROOT, "expowest_amazon_master.csv")
OUT = os.path.join(ROOT, "smartscout_brands.csv")
FIELDS = ["Exhibitor ID", "Exhibitor", "Amazon Store Name", "SmartScout Brand", "SmartScout Match",
          "Monthly Revenue", "TTM Revenue", "Monthly Units", "Primary Category", "Primary Subcategory",
          "Total Products", "Total Reviews", "Average Rating", "Average Price", "Brand Score", "Average Sellers",
          "Average FBA Sellers", "MoM Growth", "12-Month MoM Growth", "Amazon ISR", "Amazon Revenue %",
          "Ranking Products", "Ranking Search Terms", "Single Seller Name", "Has Storefront"]
SRC = {"Monthly Revenue": "Total Monthly Revenue", "TTM Revenue": "Trailing 12-Month Revenue",
       "Monthly Units": "Total Monthly Units Sold", "Brand Score": "Average Brand Score",
       "MoM Growth": "Average MoM Growth", "12-Month MoM Growth": "Average 12-Month MoM Growth",
       "Amazon ISR": "Average Amazon ISR", "Amazon Revenue %": "Average Amazon Revenue %"}


def key(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def brands():
    """One row per campaign brand with its Amazon store name and Amazon brand field."""
    import expowest_people as P
    amz, out, seen = P.amazon_best(), [], set()
    for r in csv.DictReader(open(MASTER, encoding="utf-8")):
        eid = r["Exhibitor ID"]
        if eid in seen:
            continue
        seen.add(eid)
        b = (amz.get(eid) or {}).get("best") or {}
        names = [html.unescape(x) for x in (r["Amazon Store Name"], b.get("brand_row", "")) if x.strip()]
        out.append({"id": eid, "name": r["Exhibitor"], "names": list(dict.fromkeys(names)), "tier": r["Priority Tier"]})
    out.sort(key=lambda x: (x["tier"], x["id"]))
    return out


def raw_rows():
    out = {}
    for f in sorted(glob.glob(os.path.join(WORK, "ssx_raw_*.jsonl"))):
        for l in open(f, encoding="utf-8"):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("Brand Name"):
                out.setdefault(key(r["Brand Name"]), r)
    return out


def queried():
    q = set()
    for f in glob.glob(os.path.join(WORK, "ssx_in_*.jsonl")):
        if os.path.exists(f.replace("ssx_in_", "ssx_done_").replace(".jsonl", ".txt")):
            q |= {key(json.loads(l)["name"]) for l in open(f, encoding="utf-8")}
    return q


def pending():
    return {key(json.loads(l)["name"]) for f in glob.glob(os.path.join(WORK, "ssx_in_*.jsonl"))
            for l in open(f, encoding="utf-8")}


def plan(n):
    have, skip, want = raw_rows(), pending(), []
    for b in brands():
        if any(key(x) in have for x in b["names"]):
            continue
        for x in b["names"]:
            if key(x) not in skip and key(x) not in {key(w) for w in want}:
                want.append(x)
    nums = [int(re.search(r"_(\d+)\.jsonl$", f).group(1)) for f in glob.glob(os.path.join(WORK, "ssx_in_*.jsonl"))]
    k, made = max(nums, default=0) + 1, []
    for s in range(0, len(want), n):
        with open(os.path.join(WORK, f"ssx_in_{k:02d}.jsonl"), "w", encoding="utf-8") as fh:
            for x in want[s:s + n]:
                fh.write(json.dumps({"name": x}, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k += 1
    print(f"{len(want)} store names to pull into chunks {' '.join(made) or '(none)'}")


def build():
    have, done = raw_rows(), queried()
    mp = os.path.join(WORK, "ssx_mismatch.json")  # reviewed: same name in SmartScout, different company
    mismatch = json.load(open(mp)) if os.path.exists(mp) else {}
    rows = []
    for b in brands():
        out = {"Exhibitor ID": b["id"], "Exhibitor": b["name"], "Amazon Store Name": b["names"][0] if b["names"] else ""}
        hit = next((have[key(x)] for x in b["names"] if key(x) in have), None)
        if hit and b["id"] in mismatch:
            out["SmartScout Brand"] = hit["Brand Name"]
            out["SmartScout Match"] = f"different company in SmartScout ({mismatch[b['id']]})"
            hit = None
        elif not hit:
            out["SmartScout Match"] = ("not in SmartScout" if b["names"] and all(key(x) in done for x in b["names"])
                                       else "pending pull" if b["names"] else "no store name")
        if hit:
            out["SmartScout Brand"] = hit["Brand Name"]
            out["SmartScout Match"] = "exact" if hit["Brand Name"] == out["Amazon Store Name"] else "same name, different case or spacing"
            for f in FIELDS[5:]:
                out[f] = hit.get(SRC.get(f, f), "")
        rows.append(out)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(f"{len(rows)} brands -> {OUT}")
    print(dict(Counter(r["SmartScout Match"] for r in rows)))


def status():
    for f in sorted(glob.glob(os.path.join(WORK, "ssx_in_*.jsonl"))):
        k = re.search(r"_(\d+)\.jsonl$", f).group(1)
        o = os.path.join(WORK, f"ssx_raw_{k}.jsonl")
        print(k, sum(1 for _ in open(f)), "raw", sum(1 for _ in open(o)) if os.path.exists(o) else 0,
              "DONE" if os.path.exists(os.path.join(WORK, f"ssx_done_{k}.txt")) else "")


# ---- detail pull: sellers and top subcategories, for brands we will email ----

def detail_targets():
    """SmartScout brand names (as SmartScout writes them) for matched brands that have decision makers."""
    ppl = {r["Exhibitor ID"] for r in csv.DictReader(open(MASTER, encoding="utf-8")) if r["First Name"]}
    ss = {r["Exhibitor ID"]: r for r in csv.DictReader(open(OUT, encoding="utf-8"))}
    out = []
    for b in brands():
        r = ss.get(b["id"], {})
        if b["id"] in ppl and r.get("Monthly Revenue", "") != "" and r.get("SmartScout Brand"):
            if r["SmartScout Brand"] not in out:
                out.append(r["SmartScout Brand"])
    return out


def detail_plan(n):
    done = {key(json.loads(l)["brand"]) for f in glob.glob(os.path.join(WORK, "ssd_in_*.jsonl"))
            for l in open(f, encoding="utf-8")}
    want = [b for b in detail_targets() if key(b) not in done]
    nums = [int(re.search(r"_(\d+)\.jsonl$", f).group(1)) for f in glob.glob(os.path.join(WORK, "ssd_in_*.jsonl"))]
    k, made = max(nums, default=0) + 1, []
    for s in range(0, len(want), n):
        with open(os.path.join(WORK, f"ssd_in_{k:02d}.jsonl"), "w", encoding="utf-8") as fh:
            for x in want[s:s + n]:
                fh.write(json.dumps({"brand": x}, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k += 1
    print(f"{len(want)} brands for the sellers / subcategory pull into chunks {' '.join(made) or '(none)'}")


def detail_rows(kind):
    """Brand key -> rows. Prefers ssd_tx/ (rebuilt from the raw tool results by ssd_from_transcripts.py)."""
    out = {}
    tx = os.path.join(WORK, "ssd_tx", f"ssd_{kind}_tx.jsonl")
    for f in [tx] if os.path.exists(tx) else sorted(glob.glob(os.path.join(WORK, f"ssd_{kind}_*.jsonl"))):
        for l in open(f, encoding="utf-8"):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("Brand Name"):
                out.setdefault(key(r["Brand Name"]), []).append(r)
    return out


if __name__ == "__main__":
    a = sys.argv[1:] or [""]
    {"plan": lambda: plan(int(a[1])), "build": build, "status": status,
     "detail-plan": lambda: detail_plan(int(a[1]))}.get(a[0], lambda: print(__doc__))()



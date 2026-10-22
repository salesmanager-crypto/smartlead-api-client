"""Company type, parent company and missing domains for Expo West brands that sell on Amazon.

  python3 pipeline/expowest_phase2.py export N     next chunks of N brands with no answer yet -> pipeline/work/p2_in_NN.jsonl
  python3 pipeline/expowest_phase2.py collect      validate p2_out_NN.csv files -> phase2_checkpoint.csv
  python3 pipeline/expowest_phase2.py status

In scope: the campaign brands (expowest_people.targets, priority tier order) and old-database-only companies
whose Amazon store check came back verified. Agents follow pipeline/npe_p2_agent_prompt.txt (one parent
search per company, plus a domain search when the domain is missing).
"""
import csv, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
CP = os.path.join(ROOT, "phase2_checkpoint.csv")
OLD_ONLY = os.path.join(ROOT, "old_only_companies.csv")
FIELDS = ["Exhibitor ID", "Domain Found", "Domain Source", "Exhibitor Type", "Type Reason",
          "Parent Company", "Parent Domain", "Parent Source", "Parent Query", "Notes"]
TYPES = {"Brand / Manufacturer", "Distributor / Wholesaler", "Service / Software / Media / Association",
         "Ingredient / Packaging / Private-Label Supplier", "Unclear"}
DASH = re.compile("[–—]")


def queue():
    """Brands to research, highest priority first."""
    import expowest_people as P
    m, amz = P.master(), P.amazon_best()
    out = []
    for t in P.targets():
        e, b = m[t["id"]], (amz.get(t["id"], {}).get("best") or {})
        out.append({"id": t["id"], "name": e["Exhibitor"], "other_names": e["Also Listed As"], "website": e["Website"],
                    "domain": e["Domain"], "needs_domain": not e["Domain"], "amazon_store": b.get("store_name", ""),
                    "sample_product": b.get("title", "")[:150]})
    if os.path.exists(OLD_ONLY):
        for r in csv.DictReader(open(OLD_ONLY, encoding="utf-8")):
            a = amz.get(r["Old ID"])
            if not a or a["status"] != "verified":
                continue
            b = a.get("best") or {}
            out.append({"id": r["Old ID"], "name": r["Company"], "other_names": r["Other Names"], "website": "",
                        "domain": r["Domain"], "needs_domain": not r["Domain"], "amazon_store": b.get("store_name", ""),
                        "sample_product": b.get("title", "")[:150]})
    return out


def done_ids():
    return {r["Exhibitor ID"] for r in csv.DictReader(open(CP, encoding="utf-8"))} if os.path.exists(CP) else set()


def pending_ids():
    return {json.loads(l)["id"] for f in glob.glob(os.path.join(WORK, "p2_in_*.jsonl")) for l in open(f)}


def export(n):
    skip = done_ids() | pending_ids()
    todo = [q for q in queue() if q["id"] not in skip]
    nums = [int(re.search(r"_(\d+)\.jsonl$", f).group(1)) for f in glob.glob(os.path.join(WORK, "p2_in_*.jsonl"))]
    nn = max(nums, default=0) + 1
    made = []
    for i in range(0, len(todo), n):
        with open(os.path.join(WORK, f"p2_in_{nn:02d}.jsonl"), "w") as f:
            for q in todo[i:i + n]:
                f.write(json.dumps(q, ensure_ascii=False) + "\n")
        made.append(f"{nn:02d}")
        nn += 1
    print(f"exported {len(todo)} brands into chunks {' '.join(made) or '(none)'}")


def collect():
    have = {}
    if os.path.exists(CP):
        for r in csv.DictReader(open(CP, encoding="utf-8")):
            have[r["Exhibitor ID"]] = r
    bad = 0
    for f in sorted(glob.glob(os.path.join(WORK, "p2_out_*.csv"))):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            r = {k: DASH.sub(", ", (r.get(k) or "").strip()) for k in FIELDS}
            if r["Exhibitor Type"] not in TYPES:
                bad += 1
                continue
            have.setdefault(r["Exhibitor ID"], r)
    with open(CP, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(have.values())
    print(f"{len(have)} brands in {CP} ({bad} rows skipped for an invalid type)")


def status():
    from collections import Counter
    rows = list(csv.DictReader(open(CP, encoding="utf-8"))) if os.path.exists(CP) else []
    q = queue()
    print(f"researched {len(rows)} of {len(q)} in queue; pending chunks: {len(glob.glob(os.path.join(WORK, 'p2_in_*.jsonl')))}")
    print(dict(Counter(r["Exhibitor Type"] for r in rows)))
    print(f"parents found: {sum(1 for r in rows if r['Parent Company'])}; domains found: {sum(1 for r in rows if r['Domain Found'])}")


if __name__ == "__main__":
    a = sys.argv[1:] or [""]
    {"export": lambda: export(int(a[1])), "collect": collect, "status": status}.get(a[0], lambda: print(__doc__))()

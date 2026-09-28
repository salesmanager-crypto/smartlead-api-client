"""Phase 5 recheck: top up decision makers toward 5 per exhibitor and explain every shortfall.

  export N M   write pipeline/work/p5r_in_XX.jsonl chunks of N exhibitors: the next M target exhibitors
               by revenue with fewer than 5 people that are not already rechecked or pending
  collect      merge p5r_out_XX.csv (new people) into phase5_recheck_people.csv and
               p5r_sum_XX.csv (one row per exhibitor) into phase5_recheck_summary.csv
  status
"""
import csv, glob, json, os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT
from phase5_work import CP, FIELDS, WORK, targets

PEOPLE = os.path.join(ROOT, "phase5_recheck_people.csv")
SUMMARY = os.path.join(ROOT, "phase5_recheck_summary.csv")
SUM_FIELDS = ["Exhibitor ID", "Searches Used", "Pages Fetched", "People Before", "New People", "People After",
              "Rejected Candidates", "Reason Code", "Reason Under 5"]
REASONS = {
    "R1": "Small company: fewer than 5 leaders are public",
    "R2": "Only junior or out-of-scope titles surfaced",
    "R3": "Name collision: results dominated by other companies or people with the same name",
    "R4": "Conglomerate: results mostly other divisions or non-US roles",
    "R5": "Overseas seller: little or no US LinkedIn presence",
    "R6": "Profiles found but the result did not show a current title at this company",
    "R7": "Per-exhibitor search cap reached; more people likely exist",
    "R8": "Session web search limit reached before the recheck",
    "OK": "5 or more people found",
}


def read(path, cols):
    return pd.read_csv(path, dtype=str, keep_default_na=False) if os.path.exists(path) else pd.DataFrame(columns=cols)


def current_people():
    """Named people per exhibitor from the first pass plus any recheck rows."""
    cp = read(CP, FIELDS)
    rp = read(PEOPLE, FIELDS)
    allp = pd.concat([cp, rp], ignore_index=True)
    return allp[allp["Name"] != ""]


def export(chunk, limit):
    people = current_people()
    cp = read(CP, FIELDS)
    done = set(read(SUMMARY, SUM_FIELDS)["Exhibitor ID"])
    pending = set()
    for f in glob.glob(os.path.join(WORK, "p5r_in_*.jsonl")):
        n = os.path.basename(f)[7:9]
        if not os.path.exists(os.path.join(WORK, f"p5r_sum_{n}.csv")):
            pending |= {json.loads(l)["id"] for l in open(f)}
    items = []
    for t in targets():
        g = people[people["Exhibitor ID"] == t["id"]]
        if len(g) >= 5 or t["id"] in done or t["id"] in pending:
            continue
        c = cp[cp["Exhibitor ID"] == t["id"]]
        t["existing"] = [{"name": r["Name"], "title": r["Title (as shown)"], "url": r["LinkedIn URL"]}
                         for r in g.to_dict("records")]
        t["prior_queries"] = sorted(set(q for q in c["Search Query"] if q))
        t["prior_notes"] = "; ".join(sorted(set(n for n in c["Notes"] if n)))
        t["company_linkedin"] = next((x for x in c["Company LinkedIn"] if x), t["company_linkedin"])
        items.append(t)
        if len(items) >= limit:
            break
    existing = glob.glob(os.path.join(WORK, "p5r_in_*.jsonl"))
    n = max([int(os.path.basename(f)[7:9]) for f in existing] or [-1]) + 1
    made = []
    for i in range(0, len(items), chunk):
        with open(os.path.join(WORK, f"p5r_in_{n:02d}.jsonl"), "w") as fh:
            for it in items[i:i + chunk]:
                fh.write(json.dumps(it, ensure_ascii=False) + "\n")
        made.append(f"{n:02d}")
        n += 1
    print(f"exported {len(items)} exhibitors into chunks {' '.join(made)}")


def clean(v):
    return (v or "").strip().replace("—", ", ").replace("–", "-")


def collect():
    have = set(read(SUMMARY, SUM_FIELDS)["Exhibitor ID"])
    seen = {(r["Exhibitor ID"], r["LinkedIn URL"] or r["Name"].lower()) for r in current_people().to_dict("records")}
    new_p, new_s = not os.path.exists(PEOPLE), not os.path.exists(SUMMARY)
    added = people = 0
    with open(PEOPLE, "a", newline="", encoding="utf-8") as fp, open(SUMMARY, "a", newline="", encoding="utf-8") as fs:
        wp = csv.DictWriter(fp, fieldnames=FIELDS + ["Chunk"], extrasaction="ignore")
        ws = csv.DictWriter(fs, fieldnames=SUM_FIELDS + ["Chunk"], extrasaction="ignore")
        if new_p:
            wp.writeheader()
        if new_s:
            ws.writeheader()
        for path in sorted(glob.glob(os.path.join(WORK, "p5r_sum_*.csv"))):
            chunk = os.path.basename(path)[8:10]
            s = pd.read_csv(path, dtype=str, keep_default_na=False)
            out = os.path.join(WORK, f"p5r_out_{chunk}.csv")
            o = read(out, FIELDS)
            for r in s.to_dict("records"):
                eid = r["Exhibitor ID"]
                if eid in have:
                    continue
                for p in o[o["Exhibitor ID"] == eid].to_dict("records"):
                    p = {k: clean(p.get(k)) for k in FIELDS}
                    key = (eid, p["LinkedIn URL"] or p["Name"].lower())
                    if not p["Name"] or key in seen:
                        continue
                    seen.add(key)
                    p["Chunk"] = chunk
                    wp.writerow(p)
                    people += 1
                r = {k: clean(r.get(k)) for k in SUM_FIELDS}
                r["Chunk"] = chunk
                ws.writerow(r)
                have.add(eid)
                added += 1
    print(f"collected {added} exhibitors, {people} new people; rechecked total {len(have)}")


def status():
    s = read(SUMMARY, SUM_FIELDS)
    print(f"rechecked: {len(s)}")
    for f in sorted(glob.glob(os.path.join(WORK, "p5r_in_*.jsonl"))):
        n = os.path.basename(f)[7:9]
        ids = [json.loads(l)["id"] for l in open(f)]
        sp = os.path.join(WORK, f"p5r_sum_{n}.csv")
        got = len(read(sp, SUM_FIELDS))
        print(f"  chunk {n}: {len(ids)} in, {got} summarized")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(int(sys.argv[2]), int(sys.argv[3]))
    else:
        {"collect": collect, "status": status}[cmd]()

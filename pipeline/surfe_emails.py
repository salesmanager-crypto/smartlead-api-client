"""Work emails from Surfe for the selected decision makers, spent on exhibitors that are on Amazon first.

  python surfe_emails.py export N BUDGET   write pipeline/work/se_in_XX.jsonl chunks of N people, at most BUDGET
                                           people in total (Surfe email credits), people of exhibitors with an
                                           Amazon-verified brand first, then "possible", each group by revenue
  python surfe_emails.py collect           merge se_out_XX.jsonl -> surfe_emails.csv
  python surfe_emails.py status

Agents (prompt pipeline/se_agent_prompt.txt) call surfe_enrich_people (email only, no mobile) and append one line
per person to se_out_XX.jsonl. Nothing is guessed: a person Surfe has no email for stays blank.
"""
import glob, json, os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
OUT = os.path.join(ROOT, "surfe_emails.csv")


def person_key(r):
    return f'{r["Exhibitor ID"]}|{r["LinkedIn URL"] or (r["First Name"] + " " + r["Last Name"]).lower()}'


def amazon_rank():
    """Exhibitor ID -> 0 (verified store or brand on Amazon), 1 (possible), 2 (neither)."""
    a = pd.read_csv(os.path.join(ROOT, "amazon_stores.csv"), dtype=str).fillna("")
    best = {}
    for _, r in a.iterrows():
        k = 0 if r["Amazon Status"] == "verified" else (1 if r["Amazon Status"] == "possible" else 2)
        best[r["Exhibitor ID"]] = min(best.get(r["Exhibitor ID"], 2), k)
    return best


def load_out():
    out = {}
    for f in sorted(glob.glob(os.path.join(WORK, "se_out_*.jsonl"))):
        for l in open(f):
            l = l.strip()
            if l:
                try:
                    r = json.loads(l)
                except json.JSONDecodeError:
                    continue
                if r.get("status") != "error" or r.get("key") not in out:
                    out[r.get("key")] = r
    return out


def export(n, budget):
    p = pd.read_csv(os.path.join(ROOT, "surfe_people.csv"), dtype=str).fillna("")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from surfe_people import targets
    rev = targets()["rev"].to_dict()
    rank = amazon_rank()
    p["key"] = p.apply(person_key, axis=1)
    p["arank"] = p["Exhibitor ID"].map(lambda e: rank.get(e, 2))
    p["rev"] = p["Exhibitor ID"].map(lambda e: rev.get(e, 0))
    p = p[p["arank"] < 2].sort_values(["arank", "rev", "Exhibitor ID", "Priority"], ascending=[True, False, True, True])
    queued = set()
    for f in glob.glob(os.path.join(WORK, "se_in_*.jsonl")):
        queued |= {json.loads(l)["key"] for l in open(f)}
    p = p[~p["key"].isin(queued)].head(max(0, budget))
    domains = pd.read_excel(os.path.join(ROOT, "phase2_domains.xlsx"), sheet_name="Exhibitors", dtype=str).fillna("")
    dom = dict(zip(domains["Exhibitor ID"], domains["Domain"]))
    rows = [{"key": r["key"], "id": r["Exhibitor ID"], "firstName": r["First Name"], "lastName": r["Last Name"],
             "linkedinUrl": r["LinkedIn URL"], "companyDomain": r["Company Domain"] or dom.get(r["Exhibitor ID"], ""),
             "companyName": r["Surfe Company"] or r["Exhibitor Name"]} for _, r in p.iterrows()]
    existing = glob.glob(os.path.join(WORK, "se_in_*.jsonl"))
    k = max([int(os.path.basename(f)[6:8]) for f in existing] or [-1]) + 1
    made = []
    for s in range(0, len(rows), n):
        with open(os.path.join(WORK, f"se_in_{k:02d}.jsonl"), "w") as fh:
            for r in rows[s:s + n]:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k += 1
    print(f"exported {len(rows)} people into chunks {' '.join(made)}")


def collect():
    out = load_out()
    rows = [{"Key": k, "Exhibitor ID": r.get("id", ""), "Email": r.get("email") or "",
             "Email Status": r.get("email_status") or "", "Other Emails": "; ".join(r.get("other_emails") or []),
             "Surfe Status": r.get("status", ""), "Note": r.get("note") or ""} for k, r in out.items() if k]
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"{len(rows)} people enriched, {sum(1 for r in rows if r['Email'])} with an email")


def status():
    for f in sorted(glob.glob(os.path.join(WORK, "se_in_*.jsonl"))):
        k = os.path.basename(f)[6:8]
        o = os.path.join(WORK, f"se_out_{k}.jsonl")
        print(k, sum(1 for _ in open(f)), "out", sum(1 for _ in open(o)) if os.path.exists(o) else 0,
              "DONE" if os.path.exists(os.path.join(WORK, f"se_done_{k}.txt")) else "")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == "collect":
        collect()
    else:
        status()

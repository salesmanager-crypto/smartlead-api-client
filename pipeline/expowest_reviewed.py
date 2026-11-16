"""Reviewed Expo West emails -> one Smartlead lead per contact, rendered with that contact's own first name.

  python3 pipeline/expowest_reviewed.py <reviewed.xlsx>

The reviewed workbook holds one email per brand in its "New Email" column, greeted to the brand's first contact.
Brands whose cell starts "RESEARCH NEEDED" have no email and are left out. For every other brand the copy after the
greeting is shared by all its contacts; each contact gets "Hi <their name>," in front (the name the person goes by,
or "Hi <Brand> team," where the record holds no person's name), then the Phase 10 gate (presend_qa.py) checks the
rendered copy against that brand's SmartScout numbers and writes the upload file only when nothing fails.

Outputs (pipeline/work/reviewed/): emails_reviewed.csv, gate_master.csv, qa_report.csv, smartlead_upload.csv
and, in the repository root (gitignored), expowest_smartlead_tiers1to3.csv and expowest_smartlead_tier4.csv.
Follow-ups live in the Smartlead sequence itself (see FOLLOW_UPS) and use {{first_name}} and {{company_name}}.
"""
import csv, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl
from common import ROOT
import expowest_presend as P

OUT = os.path.join(ROOT, "pipeline", "work", "reviewed")
SIGNATURE = "Albert Scott|Full Service Amazon Agency"
# brands held out of the send although the reviewer wrote an email: the figures cannot be traced to our data
EXTRA_HOLDS = {
    "O1800": "figures belong to another brand (SunButter), not in our SmartScout rows for Red River Commodities",
}


def reviewed(path):
    ws = openpyxl.load_workbook(path).active
    rows = list(ws.iter_rows(values_only=True))
    H = rows[0]
    return [dict(zip(H, r)) for r in rows[1:]]


def split_greeting(text):
    first, _, rest = text.partition("\n\n")
    m = re.fullmatch(r"Hi (.+),", first.strip())
    return (m.group(1) if m else None), rest


def build(path):
    os.makedirs(OUT, exist_ok=True)
    R = reviewed(path)
    emails, team, research = [], {}, []
    for r in R:
        t = (r["New Email"] or "").strip()
        if not t.startswith("Hi "):
            research.append((r["Exhibitor ID"], r["Exhibitor"], t.split("\n")[0]))
            continue
        name, rest = split_greeting(t)
        if name and name != r["First Name"]:
            team[(r["Exhibitor ID"], r["First Name"])] = name  # the reviewer greeted the brand, not the person
        emails.append({"Exhibitor ID": r["Exhibitor ID"], "Brand": r["Exhibitor"],
                       "Email Body": "Hi {{first_name}},\n\n" + rest.strip()})
    with open(os.path.join(OUT, "emails_reviewed.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["Exhibitor ID", "Brand", "Email Body"])
        w.writeheader()
        w.writerows(emails)
    print(f"{len(emails)} reviewed emails, {len(research)} brands marked RESEARCH NEEDED, "
          f"{len(team)} contacts greeted as a team")
    with open(os.path.join(OUT, "research_needed.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Exhibitor ID", "Exhibitor", "Reviewer note"])
        w.writerows(research)
    return team


def main(path):
    """Run the gate; a brand whose reviewed copy fails it is held out (reason kept) and the gate runs again, so the
    reviewer's text is never edited here. Stops when a run has no FAIL rows."""
    import pandas as pd
    team = build(path)
    holds = dict(EXTRA_HOLDS)
    for _ in range(4):
        rc = P.run(out=OUT, signature=SIGNATURE, min_words="60", max_words="115",
                   emails_path=os.path.join(OUT, "emails_reviewed.csv"), team_greeting=team, hold_ids=holds, no_show=True)
        if rc == 0:
            break
        rep = pd.read_csv(os.path.join(OUT, "qa_report.csv"), dtype=str).fillna("")
        for _, f in rep[rep.Result == "FAIL"].iterrows():
            holds.setdefault(f["Exhibitor ID"], "reviewed copy fails the send rules: " + f["Issues"].split(" | ")[0])
    with open(os.path.join(OUT, "held_by_gate.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Exhibitor ID", "Reason"])
        w.writerows(holds.items())
    print(f"{len(holds)} brands held out by the gate: {', '.join(holds)}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

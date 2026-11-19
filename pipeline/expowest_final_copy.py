"""Yoni's corrected Expo West sequence (Nov 19 workbook) -> each contact's email, rendered and checked.

  python3 pipeline/expowest_final_copy.py <workbook.xlsx> [initial-email column, default "New New Email"]

The workbook has one row per brand. The initial email column is greeted to the brand's first contact; its text after
the greeting is shared by every contact at the brand, and each contact gets "Hi <their name>," in front (the name they
go by, or "Hi <Brand> team," where the record holds no person's name). Follow-ups 2 and 3 are per brand too.

The copy is Yoni's, so nothing is edited or dropped here. The Phase 10 gate runs on it and every contact gets a check
string: PASS, WARN: <why>, or REVIEW: <what could not be traced to our data or breaks a send rule>.

Outputs (pipeline/work/final_copy/): emails_final.csv, gate_master.csv, qa_report.csv, by_email.json
(email -> {"body": the email with <br> breaks, "check": ...}).
"""
import csv, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import ROOT
import expowest_presend as P
from expowest_reviewed import reviewed, split_greeting, SIGNATURE

OUT = os.path.join(ROOT, "pipeline", "work", "final_copy")


def html(text):
    return text.replace("\n\n", "<br><br>").replace("\n", "<br>")


def main(path, column="New New Email"):
    os.makedirs(OUT, exist_ok=True)
    emails, team, research = [], {}, []
    for r in reviewed(path):
        t = (r[column] or "").strip()
        if not t.startswith("Hi "):
            research.append(r["Exhibitor ID"])
            continue
        name, rest = split_greeting(t)
        if name and name != r["First Name"]:
            team[(r["Exhibitor ID"], r["First Name"])] = name
        emails.append({"Exhibitor ID": r["Exhibitor ID"], "Brand": r["Exhibitor"],
                       "Email Body": "Hi {{first_name}},\n\n" + rest.strip()})
    with open(os.path.join(OUT, "emails_final.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["Exhibitor ID", "Brand", "Email Body"])
        w.writeheader()
        w.writerows(emails)
    print(f"{len(emails)} brand emails, {len(research)} brands without one (research needed), {len(team)} team greetings")
    P.run(out=OUT, signature=SIGNATURE, min_words="40", max_words="400",
          emails_path=os.path.join(OUT, "emails_final.csv"), team_greeting=team, no_show=True)
    rep = pd.read_csv(os.path.join(OUT, "qa_report.csv"), dtype=str).fillna("")
    gm = list(csv.DictReader(open(os.path.join(OUT, "gate_master.csv"), encoding="utf-8")))
    by = {}
    for _, q in rep.iterrows():
        g = gm[int(q["Row"]) - 2]
        body = g["Email Body"].replace("{{first_name}}", g["First Name"])
        iss = q["Issues"].split(" | ") if q["Issues"] else []
        check = {"PASS": "PASS", "WARN": "WARN: " + "; ".join(iss[:2])}.get(q["Result"], "REVIEW: " + "; ".join(iss[:2]))
        by[g["Card Email"].strip().lower()] = {"body": html(body), "check": check, "id": g["Exhibitor ID"]}
    json.dump(by, open(os.path.join(OUT, "by_email.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(by)} contacts rendered:", dict(pd.Series([v["check"].split(":")[0] for v in by.values()]).value_counts()))


if __name__ == "__main__":
    main(sys.argv[1], *(sys.argv[2:3]))

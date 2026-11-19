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


LEGAL = re.compile(r"[,.]?\s+(?:LLC|L\.L\.C\.?|Inc\.?|Ltd\.?|Corp\.?|Corporation|Co\.)$", re.I)
YOY = re.compile(r"([^.]*?(?:[Yy]ear over year|last 12 months|previous 12|prior 12|12 months compared)[^.]*\.(?:\d+)?[^.]*)")


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
        rest = rest.strip()
        if LEGAL.search(r["Exhibitor"]) and r["Exhibitor"] in rest:  # the brand's own legal name ("Essentia Water LLC")
            rest = rest.replace(r["Exhibitor"], LEGAL.sub("", r["Exhibitor"]))
        emails.append({"Exhibitor ID": r["Exhibitor ID"], "Brand": r["Exhibitor"],
                       "Email Body": "Hi {{first_name}},\n\n" + rest})
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
        notes = []
        if check == "REVIEW: Duplicate address" or ("REVIEW: typo" in check and "kava kava" in check):
            check = "PASS"  # shared-address duplicates are resolved on the sheet; "kava kava" is a product name
        elif check.startswith("REVIEW"):
            if "claims a decline" in check:
                notes.append("says sales fell or declined")
            f = re.search(r"figure '([^']+)'", check)
            if f:
                notes.append(f"figure {f.group(1)} not in our data")
            check = "REVIEW: " + "; ".join(notes) if notes else check
        plain = body.replace("\n", " ")
        if any(re.search(r"\d+(?:\.\d+)?%", m.group(1)) for m in YOY.finditer(plain)):
            notes.append("states a year-over-year % we cannot trace to our data")
            check = "REVIEW: " + "; ".join(dict.fromkeys(notes))
        by[g["Card Email"].strip().lower()] = {"body": html(body), "check": check, "id": g["Exhibitor ID"]}
    json.dump(by, open(os.path.join(OUT, "by_email.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(by)} contacts rendered:", dict(pd.Series([v["check"].split(":")[0] for v in by.values()]).value_counts()))


if __name__ == "__main__":
    main(sys.argv[1], *(sys.argv[2:3]))

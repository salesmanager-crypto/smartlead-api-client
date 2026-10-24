"""Master sheet and Smartlead import for the Expo West Amazon campaign.

  python3 pipeline/expowest_campaign.py master      -> expowest_amazon_master.csv (one row per person; in-scope
                                                      exhibitors with no people get one row saying why)
  python3 pipeline/expowest_campaign.py smartlead   -> expowest_smartlead_import.csv (people with an email and a
                                                      passing custom email only)

Text columns are cleaned of em and en dashes before writing.
"""
import csv, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT
from expowest_people import ORDER, amazon_best, emails, master, people, targets, tier

MASTER_OUT = os.path.join(ROOT, "expowest_amazon_master.csv")
SL_OUT = os.path.join(ROOT, "expowest_smartlead_import.csv")


def clean(v):
    return re.sub(r"\s*[–—]\s*", ", ", v) if isinstance(v, str) else v


def custom_emails():
    """Brand-level emails from expowest_emails.py collect, keyed by Exhibitor ID (every contact at a brand gets the
    same body; only {{first_name}} changes)."""
    from expowest_emails import OUT
    if not os.path.exists(OUT):
        return {}
    return {r["Exhibitor ID"]: r for r in csv.DictReader(open(OUT, encoding="utf-8"))}


def build_master():
    m, amz, em = master(), amazon_best(), emails()
    ce = custom_emails()
    ppl = {}
    for p in people():
        ppl.setdefault(p["Exhibitor ID"], []).append(p)
    searched = set()
    import glob, json
    for f in glob.glob(os.path.join(ROOT, "pipeline", "work", "sf_in_*.jsonl")):
        searched |= {json.loads(l)["id"] for l in open(f)}
    oldm = {}
    op = os.path.join(ROOT, "pipeline", "work", "old_db_match.json")
    if os.path.exists(op):
        oldm = json.load(open(op))
    tiers = {1: "1: New to us, 2027 exhibitor", 2: "2: New to us", 3: "3: In old database",
             4: "4: In old database, already sent"}
    fields = ["Priority Tier", "Row Status", "In Old Database", "Old DB Already Sent", "Old DB Company", "Exhibitor ID", "Exhibitor",
              "Also Listed As", "Years Exhibited", "In 2027 List",
              "Booths", "Website", "Domain", "Domain Found", "Domain Source", "Exhibitor Type", "Type Reason",
              "Parent Company", "Parent Domain", "Parent Source", "Research Notes", "Address", "Amazon Status", "Amazon Store Name", "Has Amazon Store",
              "Amazon Store URL", "Amazon Brand Field", "Sample ASIN", "Sample Product", "Sold By",
              "Priority", "First Name", "Last Name", "Title", "LinkedIn URL", "Country", "Email", "Email Status",
              "Email Body", "Email Angle", "Email QA Flags", "Show URLs"]
    fields.remove("Amazon Store URL")  # not captured reliably; the store name is exact
    p2 = {}
    p2f = os.path.join(ROOT, "phase2_checkpoint.csv")
    if os.path.exists(p2f):
        p2 = {r["Exhibitor ID"]: r for r in csv.DictReader(open(p2f, encoding="utf-8"))}
    BRAND = "Brand / Manufacturer"

    def research(eid):
        r = p2.get(eid, {})
        return {"Domain Found": r.get("Domain Found", ""), "Domain Source": r.get("Domain Source", ""),
                "Exhibitor Type": r.get("Exhibitor Type", ""), "Type Reason": r.get("Type Reason", ""),
                "Parent Company": r.get("Parent Company", ""), "Parent Domain": r.get("Parent Domain", ""),
                "Parent Source": r.get("Parent Source", ""), "Research Notes": r.get("Notes", "")}

    def add(base, eid):
        """One row per selected person, or one row saying why there are none."""
        if not ppl.get(eid):
            why = "No people found in Surfe" if eid in searched else "People search pending"
            rows.append({**base, "Row Status": why})
            return
        for p in sorted(ppl[eid], key=lambda p: int(p["Priority"])):
            r = em.get(p["Key"], {})
            c = ce.get(eid, {})
            if not r:
                why = "Email pending"
            elif not r.get("email"):
                why = "No email from Surfe"
            elif not c:
                why = "Custom email pending"
            else:
                why = "Ready"
            rows.append({**base, "Row Status": why, "Priority": p["Priority"], "First Name": p["First Name"],
                         "Last Name": p["Last Name"], "Title": p["Title"], "LinkedIn URL": p["LinkedIn URL"],
                         "Country": p["Country"], "Email": r.get("email", ""), "Email Status": r.get("email_status", ""),
                         "Email Body": c.get("Email Body", ""), "Email Angle": c.get("Angle", ""),
                         "Email QA Flags": c.get("QA Flags", "")})

    rows = []
    scope = {t["id"] for t in targets()}  # Amazon sellers after the supplier, false-match and client exclusions
    for eid, e in m.items():
        a = amz.get(eid)
        st = a["status"] if a else ""
        if eid not in scope or p2.get(eid, {}).get("Exhibitor Type", BRAND) != BRAND:
            continue
        b = a.get("best") or {}
        o = oldm.get(eid, {})
        base = {"Priority Tier": tiers[tier(eid, e["In 2027"] == "Yes")], "In Old Database": "Yes" if o.get("old_company") else "No",
                "Old DB Already Sent": "Yes" if o.get("old_sent") else "No",
                "Old DB Company": o.get("old_company", ""), "Exhibitor ID": eid, "Exhibitor": e["Exhibitor"], "Also Listed As": e["Also Listed As"],
                "Years Exhibited": e["Years"], "In 2027 List": e["In 2027"], "Booths": e["Booths"],
                "Website": e["Website"], "Domain": e["Domain"], "Address": e["Address"], "Amazon Status": st,
                "Amazon Store Name": b.get("store_name", ""), "Has Amazon Store": "Yes" if b.get("has_store") else "No",
                "Amazon Store URL": b.get("store_url", ""), "Amazon Brand Field": b.get("brand_row", ""),
                "Sample ASIN": b.get("asin", ""), "Sample Product": b.get("title", ""), "Sold By": b.get("sold_by", ""),
                "Show URLs": e["Show URLs"], **research(eid)}
        add(base, eid)
    import expowest_phase2 as P2
    old = {r["Old ID"]: r for r in csv.DictReader(open(P2.OLD_ONLY, encoding="utf-8"))} if os.path.exists(P2.OLD_ONLY) else {}
    for q in P2.queue():
        oid = q["id"]
        if oid not in old or p2.get(oid, {}).get("Exhibitor Type", BRAND) != BRAND:
            continue
        o, b = old[oid], (amz[oid].get("best") or {})
        sent = o["Already Sent (old)"] == "Yes"
        base = {"Priority Tier": tiers[4 if sent else 3],
                     "In Old Database": "Yes", "Old DB Already Sent": "Yes" if sent else "No", "Old DB Company": o["Company"],
                     "Exhibitor ID": oid, "Exhibitor": o["Company"], "Also Listed As": o["Other Names"],
                     "Years Exhibited": "", "In 2027 List": "No", "Domain": o["Domain"],
                     "Amazon Status": amz[oid]["status"], "Amazon Store Name": b.get("store_name", ""),
                     "Has Amazon Store": "Yes" if b.get("has_store") else "No", "Amazon Brand Field": b.get("brand_row", ""),
                     "Sample ASIN": b.get("asin", ""), "Sample Product": b.get("title", ""), "Sold By": b.get("sold_by", ""),
                     **research(oid)}
        add(base, oid)
    rows.sort(key=lambda r: (r["Priority Tier"], r["In 2027 List"] != "Yes", ORDER[r["Amazon Status"]], r["Exhibitor ID"],
                             int(r.get("Priority") or 9)))
    with open(MASTER_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: clean(r.get(k, "")) for k in fields})
    from collections import Counter
    print(f"{len(rows)} rows for {len({r['Exhibitor ID'] for r in rows})} Amazon exhibitors ->", MASTER_OUT)
    print(dict(Counter(r["Row Status"] for r in rows)))


def build_smartlead():
    rows = [r for r in csv.DictReader(open(MASTER_OUT, encoding="utf-8")) if r["Row Status"] == "Ready"]
    fields = ["email", "first_name", "last_name", "company_name", "website", "linkedin_profile", "title",
              "brand_store", "booth_2027", "email1_body"]  # subject lines are set in Smartlead
    with open(SL_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            booth = re.search(r"2027: ([^;]+)", r["Booths"])
            body = r["Email Body"]
            w.writerow({"email": r["Email"], "first_name": r["First Name"], "last_name": r["Last Name"],
                        "company_name": r["Exhibitor"], "website": r["Website"], "linkedin_profile": r["LinkedIn URL"],
                        "title": r["Title"], "brand_store": r["Amazon Store Name"],
                        "booth_2027": booth.group(1) if booth else "",
                        "email1_body": body.replace("\n", "<br>")})
    print(f"{len(rows)} leads -> {SL_OUT}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "master":
        build_master()
    elif cmd == "smartlead":
        build_smartlead()
    else:
        print(__doc__)

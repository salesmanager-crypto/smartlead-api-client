"""One master sheet: one row per decision maker, with everything about their exhibitor on the same row.

  python master_build.py      -> master_sheet.csv

Rows: every Brand / Manufacturer exhibitor (distributors, service companies, shop suppliers and unclear exhibitors
are out of scope). An exhibitor with people gets one row per person (up to 5, in priority order); an exhibitor with
no people gets one row whose Row Status says why. Sources, in column order: phase 1 show data and social links,
phase 2 domain / parent / type, the verified Amazon store (amazon_stores.csv), SmartScout keyed on that store name
(smartscout_store.csv), Surfe company and people (surfe_companies.csv, surfe_people.csv), Surfe emails
(surfe_emails.csv) and the custom emails (cold_emails.csv). Missing files are treated as empty, so the sheet can be
built at any stage.
"""
import os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

OUT = os.path.join(ROOT, "master_sheet.csv")
STATUS_ORDER = {"verified": 0, "possible": 1, "different brand": 2, "not found": 3, "error": 4}

COLUMNS = [
    "Exhibitor ID", "Exhibitor Name", "Shows", "AAPEX Booth", "SEMA Booth", "Website", "Domain", "Facebook", "X",
    "Company LinkedIn", "Parent Company", "Brands Owned", "Amazon Brand", "Amazon Store Name", "Has Amazon Store",
    "Amazon Store URL", "Amazon Status", "Amazon Sold By (sample)", "SmartScout Match", "Monthly Revenue",
    "Annual Revenue (TTM)", "Primary Category", "Primary Subcategory", "Dominant Seller", "Dominant Seller Type",
    "Reseller Share %", "Top Subcategory 1", "Sub 1 Market Share", "Sub 1 Brand Rank", "Employees", "HQ Country",
    "Priority", "First Name", "Last Name", "Title", "Person LinkedIn", "Person Country", "Email", "Email Status",
    "Email Subject", "Email Body", "Row Status",
]


def csv(name):
    p = os.path.join(ROOT, name)
    return pd.read_csv(p, dtype=str).fillna("") if os.path.exists(p) else pd.DataFrame()


def main():
    p2 = pd.read_excel(os.path.join(ROOT, "phase2_domains.xlsx"), sheet_name="Exhibitors", dtype=str).fillna("")
    p2 = p2[p2["Exhibitor Type"] == "Brand / Manufacturer"]
    social = csv(os.path.join("pipeline", "work", "social_links.csv"))
    social = social.set_index("Exhibitor ID").to_dict("index") if len(social) else {}
    brands = pd.read_excel(os.path.join(ROOT, "phase4_smartscout.xlsx"), sheet_name="Brands", dtype=str).fillna("")
    owned = (brands[brands["Ownership"].isin(["Owned", "Licensed"]) & (brands["Brand"] != "")]
             .groupby("Exhibitor ID")["Brand"].apply(lambda s: "; ".join(dict.fromkeys(s))).to_dict())
    li = csv("phase5_company_linkedin.csv")
    li = dict(zip(li["Exhibitor ID"], li["Company LinkedIn"])) if len(li) else {}
    co = csv("surfe_companies.csv")
    co = co.drop_duplicates("id", keep="last").set_index("id").to_dict("index") if len(co) else {}
    ss = csv("smartscout_store.csv")
    ss = ss.set_index("Key").to_dict("index") if len(ss) else {}

    amz = csv("amazon_stores.csv")
    best = {}
    if len(amz):
        amz["o"] = amz["Amazon Status"].map(lambda s: STATUS_ORDER.get(s, 9))
        amz["rev"] = amz["Key"].map(lambda k: pd.to_numeric(ss.get(k, {}).get("Monthly Revenue", ""), errors="coerce"))
        amz["rev"] = amz["rev"].fillna(0)
        for eid, g in amz.sort_values(["o", "rev"], ascending=[True, False]).groupby("Exhibitor ID", sort=False):
            best[eid] = g.iloc[0].to_dict()

    people = csv("surfe_people.csv")
    if len(people):
        from surfe_emails import person_key
        people["key"] = people.apply(person_key, axis=1)
    em = csv("surfe_emails.csv")
    em = em.set_index("Key").to_dict("index") if len(em) else {}
    ce = csv("cold_emails.csv")
    ce = ce.set_index("Key").to_dict("index") if len(ce) else {}
    by_ex = {eid: g.sort_values("Priority") for eid, g in people.groupby("Exhibitor ID")} if len(people) else {}

    rows = []
    for _, x in p2.iterrows():
        eid = x["Exhibitor ID"]
        a = best.get(eid, {})
        s = ss.get(a.get("Key", ""), {})
        c = co.get(eid, {})
        base = {"Exhibitor ID": eid, "Exhibitor Name": x["Exhibitor Name"], "Shows": x["Shows"],
                "AAPEX Booth": x["AAPEX Booth"], "SEMA Booth": x["SEMA Booth"], "Website": x["Website"],
                "Domain": x["Domain"], "Facebook": social.get(eid, {}).get("Facebook", ""),
                "X": social.get(eid, {}).get("X", ""),
                "Company LinkedIn": c.get("linkedInURL") or li.get(eid) or x["LinkedIn"],
                "Parent Company": x["Parent Company"], "Brands Owned": owned.get(eid, ""),
                "Amazon Brand": a.get("Brand", ""), "Amazon Store Name": a.get("Amazon Store Name", ""),
                "Has Amazon Store": {"True": "Yes", "False": "No"}.get(a.get("Has Amazon Store", ""), ""),
                "Amazon Store URL": a.get("Amazon Store URL", ""), "Amazon Status": a.get("Amazon Status", ""),
                "Amazon Sold By (sample)": a.get("Sold By", ""), "Employees": c.get("employeeCount", ""),
                "HQ Country": c.get("hqCountry", "")}
        for col in ("SmartScout Match", "Monthly Revenue", "Annual Revenue (TTM)", "Primary Category",
                    "Primary Subcategory", "Dominant Seller", "Dominant Seller Type", "Reseller Share %",
                    "Top Subcategory 1", "Sub 1 Market Share", "Sub 1 Brand Rank"):
            base[col] = s.get(col, "")
        for col in ("Monthly Revenue", "Annual Revenue (TTM)"):
            v = pd.to_numeric(base[col], errors="coerce")
            base[col] = "" if pd.isna(v) else str(int(round(v)))
        g = by_ex.get(eid)
        if g is None or not len(g):
            if not a:
                why = "Amazon check not run yet"
            elif a.get("Amazon Status") in ("not found", "different brand"):
                why = f"Not on Amazon ({a['Amazon Status']}); no people searched"
            else:
                why = "No sales, marketing or e-commerce people found in Surfe" if eid in co else "People search pending"
            rows.append({**base, "Row Status": why})
            continue
        for _, r in g.iterrows():
            e, m = em.get(r["key"], {}), ce.get(r["key"], {})
            status = "Ready" if e.get("Email") and m.get("Email Body") else (
                "No email from Surfe" if e and not e.get("Email") else
                ("Email pending" if not e else "Custom email pending"))
            rows.append({**base, "Priority": r["Priority"], "First Name": r["First Name"], "Last Name": r["Last Name"],
                         "Title": r["Title"], "Person LinkedIn": r["LinkedIn URL"], "Person Country": r["Country"],
                         "Email": e.get("Email", ""), "Email Status": e.get("Email Status", ""),
                         "Email Subject": m.get("Email Subject", ""), "Email Body": m.get("Email Body", ""),
                         "Row Status": status})
    d = pd.DataFrame(rows, columns=COLUMNS).fillna("")
    d["_o"] = d["Amazon Status"].map(lambda s: STATUS_ORDER.get(s, 9))
    d["_r"] = pd.to_numeric(d["Monthly Revenue"], errors="coerce").fillna(-1)
    d["_p"] = pd.to_numeric(d["Priority"], errors="coerce").fillna(99)
    d = d.sort_values(["_o", "_r", "Exhibitor ID", "_p"], ascending=[True, False, True, True]).drop(columns=["_o", "_r", "_p"])
    for col in COLUMNS:
        d[col] = d[col].astype(str).str.replace("—", ", ").str.replace("–", "-")
    d.to_csv(OUT, index=False)
    print(f"{len(d)} rows, {d['Exhibitor ID'].nunique()} exhibitors, {(d['First Name'] != '').sum()} people, "
          f"{(d['Email'] != '').sum()} emails, {(d['Email Body'] != '').sum()} custom emails")
    print(d["Row Status"].value_counts().to_string())


if __name__ == "__main__":
    main()

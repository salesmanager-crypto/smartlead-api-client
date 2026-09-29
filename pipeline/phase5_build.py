"""Phase 5 build -> phase5_decision_makers.xlsx (People, Coverage, Read Me) and AAPEX_SEMA_MASTER.xlsx."""
import os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, load_state, save_state
from phase1_build import excel_safe, format_workbook
from phase5_work import CP, FIELDS, targets
from phase5_recheck import PEOPLE as RP, REASONS, SUM_FIELDS, SUMMARY
from phase5_linkedin import known as company_pages

OUT = os.path.join(ROOT, "phase5_decision_makers.xlsx")
MASTER = os.path.join(ROOT, "AAPEX_SEMA_MASTER.xlsx")
NOT_SEARCHED = "Not searched (session web search limit reached); try Sales Navigator / Surfe"


def main():
    t = pd.DataFrame(targets())
    cp = pd.read_csv(CP, dtype=str, keep_default_na=False) if os.path.exists(CP) else pd.DataFrame(columns=FIELDS)
    real = cp[~cp["Notes"].str.startswith("Not searched")]
    searched = set(real["Exhibitor ID"])
    # drop "Not searched" placeholder rows (re-added below for every unsearched target)
    first_queries = real[real["Search Query"] != ""].groupby("Exhibitor ID")["Search Query"].nunique()
    cp = real
    if os.path.exists(RP):
        rp = pd.read_csv(RP, dtype=str, keep_default_na=False)
        drops = QA[QA["Action"] == "drop"]
        rp = rp[~(rp["Exhibitor ID"] + "|" + rp["Name"]).isin(drops["Exhibitor ID"] + "|" + drops["Name"])]
        rp["Notes"] = rp["Notes"].map(lambda n: "; ".join(filter(None, ["Found in recheck", n])))
        cp = pd.concat([cp, rp], ignore_index=True)
        searched |= set(rp["Exhibitor ID"])
    # an exhibitor's "no profiles found" placeholder goes once the recheck found someone
    has_named = set(cp[cp["Name"] != ""]["Exhibitor ID"])
    cp = cp[(cp["Name"] != "") | ~cp["Exhibitor ID"].isin(has_named)]
    rows = cp.drop(columns=["Chunk"], errors="ignore").to_dict("records")
    for r in t.to_dict("records"):
        if r["id"] not in searched:
            rows.append({"Exhibitor ID": r["id"], "Company LinkedIn": r["company_linkedin"], "Name": "",
                         "Title (as shown)": "", "LinkedIn URL": "", "Priority": "", "Match Reason": "",
                         "Search Query": "", "Confidence": "", "Notes": NOT_SEARCHED})
    people = pd.DataFrame(rows)
    info = t.set_index("id")
    people.insert(1, "Exhibitor Name", people["Exhibitor ID"].map(info["name"]))
    people.insert(2, "Monthly Amazon Revenue", people["Exhibitor ID"].map(info["monthly_revenue"]))
    people.insert(3, "Size", people["Exhibitor ID"].map(info["size"]))
    people["Priority"] = pd.to_numeric(people["Priority"], errors="coerce")
    people = people.sort_values(["Monthly Amazon Revenue", "Exhibitor ID", "Priority"],
                                ascending=[False, True, True])

    named = people[people["Name"] != ""]
    cov = []
    for r in t.to_dict("records"):
        g = named[named["Exhibitor ID"] == r["id"]].sort_values("Priority")
        best = g.iloc[0] if len(g) else None
        status = ("Searched" if r["id"] in searched else "Not searched")
        cov.append({"Exhibitor ID": r["id"], "Exhibitor Name": r["name"], "Monthly Amazon Revenue": r["monthly_revenue"],
                    "Size": r["size"], "Amazon Brands": r["brands"], "Company LinkedIn": (
                        people[people["Exhibitor ID"] == r["id"]]["Company LinkedIn"].replace("", pd.NA).dropna().head(1).tolist()
                        or [r["company_linkedin"]])[0],
                    "Search Status": status, "People Found": len(g),
                    "Best Contact": best["Name"] if best is not None else "",
                    "Best Contact Title": best["Title (as shown)"] if best is not None else "",
                    "Best Contact LinkedIn": best["LinkedIn URL"] if best is not None else ""})
    cov = pd.DataFrame(cov)
    pages = company_pages()
    cov["Company LinkedIn"] = [pages.get(e) or c for e, c in zip(cov["Exhibitor ID"], cov["Company LinkedIn"])]
    people["Company LinkedIn"] = [pages.get(e) or c for e, c in zip(people["Exhibitor ID"], people["Company LinkedIn"])]
    short = shortfall(t, cov, named, cp, first_queries)
    readme = pd.DataFrame({"Note": [
        "People come from public web search results (site:linkedin.com/in queries), not from a LinkedIn data tool. "
        "Titles are as shown in the search result; all rows are Confidence = unverified. No emails were guessed.",
        "Order: exhibitors with any Amazon brand (Yes or Possible), largest combined SmartScout monthly revenue first. "
        "The session's web search limit decides how far down the list searching reached; rows beyond it say "
        "'Not searched ... try Sales Navigator / Surfe'.",
        "Priority 1 = best fit for Amazon decisions. Small companies (under about $200k/month on Amazon): owner / "
        "founder / CEO / president first. Mid and large: e-commerce and digital leaders first, then VP Marketing / "
        "VP Sales, then president / CEO.",
        "Recheck: the top exhibitors by revenue were searched again with new queries (sales, marketing, general "
        "management, press releases) plus the company's own leadership pages, aiming for 5 people each. People found "
        "this way say 'Found in recheck' in Notes; website-only people have no LinkedIn URL.",
        "Shortfall Report: one row per target exhibitor with people found, searches run and the main reason it has "
        "fewer than 5 people, with a suggested next step. Reason counts are at the top.",
        "Next step (not part of this run): email finding with HeyReach / Surfe.",
    ]})
    with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
        excel_safe(people).to_excel(xw, sheet_name="People", index=False)
        excel_safe(cov).to_excel(xw, sheet_name="Coverage", index=False)
        excel_safe(short["counts"]).to_excel(xw, sheet_name="Shortfall Report", index=False)
        excel_safe(short["rows"]).to_excel(xw, sheet_name="Shortfall Report", index=False,
                                           startrow=len(short["counts"]) + 3)
        readme.to_excel(xw, sheet_name="Read Me", index=False)
    format_workbook(OUT)

    n_s = cov["Search Status"].eq("Searched").sum()
    print(f"Target exhibitors: {len(cov)}; searched: {n_s}; not searched: {len(cov) - n_s}")
    print(f"People found: {len(named)} across {cov['People Found'].gt(0).sum()} exhibitors; "
          f"searched but none found: {((cov['Search Status'] == 'Searched') & (cov['People Found'] == 0)).sum()}")
    build_master(cov, named, short)
    state = load_state()
    state.setdefault("phase5", {}).update(searched=int(n_s), people=int(len(named)))
    save_state(state)


NEXT = {
    "R1": "Use the people found; for more, check the company site and Sales Navigator",
    "R2": "Sales Navigator / Surfe filtered on the company and senior titles",
    "R3": "Sales Navigator company filter (search engines mix up the name)",
    "R4": "Sales Navigator filtered to the automotive / aftermarket division, US",
    "R5": "Sales Navigator on the brand's US entity; or reach the owner via Amazon brand storefront / website",
    "R6": "Open the profiles in Sales Navigator to confirm current title",
    "R7": "Run another recheck round next session",
    "R8": "Run the recheck next session (search limit)",
    "R9": "Run the first search next session (search limit), or Sales Navigator / Surfe",
    "R0": "Run the recheck next session (search limit)",
    "OK": "",
}
QA_PATH = os.path.join(ROOT, "pipeline", "work", "p5r_qa.csv")
QA = pd.read_csv(QA_PATH, dtype=str, keep_default_na=False) if os.path.exists(QA_PATH) else pd.DataFrame(
    columns=["Exhibitor ID", "Name", "Action", "Reason Code", "Note"])
REASONS_ALL = dict(REASONS, R9="Not searched yet: the session web search limit was reached before this exhibitor",
                   R0="Searched once (up to 4 searches), recheck not reached before the session search limit")


def shortfall(t, cov, named, cp, first_queries):
    """One row per target exhibitor: people found and why it is fewer than 5."""
    summ = pd.read_csv(SUMMARY, dtype=str, keep_default_na=False).set_index("Exhibitor ID") if os.path.exists(
        SUMMARY) else pd.DataFrame(columns=SUM_FIELDS).set_index("Exhibitor ID")
    first_notes = cp[cp["Name"] == ""].groupby("Exhibitor ID")["Notes"].first()
    rows = []
    for r in cov.to_dict("records"):
        eid, n = r["Exhibitor ID"], int(r["People Found"])
        fq = int(first_queries.get(eid, 0))
        if eid in summ.index:
            s = summ.loc[eid]
            code = "OK" if n >= 5 else (s["Reason Code"] if s["Reason Code"] not in ("", "OK") else "R7")
            reason = "" if n >= 5 else s["Reason Under 5"]
            q = QA[(QA["Exhibitor ID"] == eid) & (QA["Action"] == "code")]
            if n < 5 and len(q):
                code, reason = q.iloc[0]["Reason Code"], q.iloc[0]["Note"]
            dropped = QA[(QA["Exhibitor ID"] == eid) & (QA["Action"] == "drop")]
            rej = "; ".join(filter(None, [s["Rejected Candidates"]] + [
                f"{d['Name']}: {d['Note']}" for d in dropped.to_dict("records")]))
            rq, status = int(s["Searches Used"] or 0), "Rechecked"
        elif r["Search Status"] == "Searched":
            code = "OK" if n >= 5 else "R0"
            note = first_notes.get(eid, "")
            reason = "" if n >= 5 else "; ".join(filter(None, [
                f"First pass ran {fq} web searches and kept {n} people", note]))
            rq, rej, status = 0, "", "Searched once"
        else:
            code, reason, rq, rej, status = "R9", "No searches run for this exhibitor yet", 0, "", "Not searched"
        rows.append({"Exhibitor ID": eid, "Exhibitor Name": r["Exhibitor Name"],
                     "Monthly Amazon Revenue": r["Monthly Amazon Revenue"], "Size": r["Size"],
                     "Search Status": status, "Web Searches Run": fq + rq, "People Found": n,
                     "Short By": max(0, 5 - n), "Reason Code": code,
                     "Reason Category": REASONS_ALL.get(code, ""), "Reason Detail": reason,
                     "Rejected Candidates": rej, "Suggested Next Step": NEXT.get(code, "")})
    rows = pd.DataFrame(rows)
    counts = rows.groupby(["Reason Code", "Reason Category"]).agg(
        Exhibitors=("Exhibitor ID", "count"), People=("People Found", "sum")).reset_index()
    counts = counts.sort_values("Exhibitors", ascending=False)
    return {"rows": rows, "counts": counts}


def build_master(cov, named, short):
    p = lambda f: os.path.join(ROOT, f)
    p1 = pd.read_excel(p("phase1_exhibitors.xlsx"), sheet_name="Exhibitors")
    p2 = pd.read_excel(p("phase2_domains.xlsx"), sheet_name="Exhibitors")
    p3r = pd.read_excel(p("phase3_brands_amazon.xlsx"), sheet_name="Exhibitor Rollup")
    p4b = pd.read_excel(p("phase4_smartscout.xlsx"), sheet_name="Brands")
    p4r = pd.read_excel(p("phase4_smartscout.xlsx"), sheet_name="Exhibitor Rollup")
    p5p = pd.read_excel(OUT, sheet_name="People")
    brands = p4b[p4b["Brand"].fillna("") != ""]
    stats = [
        ("Exhibitors (AAPEX + SEMA, deduped)", len(p1)),
        ("  in both shows", int((p1["Shows"] == "AAPEX; SEMA").sum())),
        ("In scope for brand research (phase 3)", int((p2["Phase 3 Scope"] == "Research").sum())),
        ("Brands found", len(brands)),
        ("Brands on Amazon (Yes)", int((brands["On Amazon"] == "Yes").sum())),
        ("Brands Possible (in SmartScout, no current products)", int((brands["On Amazon"] == "Possible").sum())),
        ("Brands with amazon.com check still pending", int((brands["On Amazon"] == "Pending").sum())),
        ("Exhibitors with at least one Amazon brand", int((p3r["Any Brand On Amazon"] == "Yes").sum())),
        ("Exhibitors with SmartScout revenue", len(p4r)),
        ("Exhibitors searched for decision makers", int((cov["Search Status"] == "Searched").sum())),
        ("People found (unverified public profiles)", len(named)),
        ("Exhibitors with 5 or more people", int((cov["People Found"] >= 5).sum())),
        ("Exhibitors rechecked for more people", int((short["rows"]["Search Status"] == "Rechecked").sum())),
    ]
    summ = pd.DataFrame(stats, columns=["Metric", "Value"])
    top = p4r.head(25).merge(cov[["Exhibitor ID", "Best Contact", "Best Contact Title", "Best Contact LinkedIn",
                                  "People Found", "Company LinkedIn"]], on="Exhibitor ID", how="left")
    top = top[["Exhibitor ID", "Exhibitor Name", "Total Monthly Revenue", "Total Annual Revenue (TTM)",
               "Largest Brand", "Largest Brand Dominant Seller Type", "Amazon Brand List", "Best Contact",
               "Best Contact Title", "Best Contact LinkedIn", "People Found", "Company LinkedIn"]]
    with pd.ExcelWriter(MASTER, engine="openpyxl") as xw:
        summ.to_excel(xw, sheet_name="Summary", index=False)
        excel_safe(top).to_excel(xw, sheet_name="Summary", index=False, startrow=len(summ) + 3)
        for name, df in [("P1 Exhibitors", p1), ("P2 Domains", p2), ("P3 Exhibitor Rollup", p3r),
                         ("P4 Brands", p4b), ("P4 Exhibitor Rollup", p4r), ("P5 People", p5p),
                         ("P5 Coverage", cov), ("P5 Shortfall Report", short["rows"])]:
            excel_safe(df).to_excel(xw, sheet_name=name, index=False)
    format_workbook(MASTER)
    print("\nSUMMARY")
    for k, v in stats:
        print(f"  {k}: {v:,}")
    print("\nTop 25 by combined Amazon revenue, with best contact:")
    for _, r in top.iterrows():
        bc = f"{r['Best Contact']} ({r['Best Contact Title']})" if isinstance(r["Best Contact"], str) and r["Best Contact"] else "-"
        print(f"  {r['Exhibitor Name'][:34]:34} ${r['Total Monthly Revenue']/1e6:5.1f}M/mo  {bc[:80]}")


if __name__ == "__main__":
    main()

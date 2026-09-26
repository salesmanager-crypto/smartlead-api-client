"""Phase 3 build -> phase3_brands_amazon.xlsx (sheets Brands, Exhibitor Rollup, Read Me)."""
import os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, load_state, save_state
from phase1_build import excel_safe, format_workbook
from phase3_work import CP, SS_CACHE

OUT = os.path.join(ROOT, "phase3_brands_amazon.xlsx")


def main():
    p2 = pd.read_excel(os.path.join(ROOT, "phase2_domains.xlsx"), sheet_name="Exhibitors",
                       dtype=str).fillna("")
    scope = p2[p2["Phase 3 Scope"] == "Research"].set_index("Exhibitor ID")
    b = pd.read_csv(CP, dtype=str, keep_default_na=False).drop(columns=["Chunk"], errors="ignore")
    b = b.drop_duplicates(["Exhibitor ID", "Brand"])
    b.insert(1, "Exhibitor Name", b["Exhibitor ID"].map(scope["Exhibitor Name"]))
    b["SS Monthly Revenue"] = pd.to_numeric(b["SS Monthly Revenue"].str.replace(r"[$,]", "", regex=True),
                                            errors="coerce")
    # brands SmartScout knows but with no current products or revenue: downgrade Yes -> Possible
    import json
    cache = json.load(open(SS_CACHE)) if os.path.exists(SS_CACHE) else {}
    idle = {k.lower() for k, v in cache.items()
            if not v.get("profile", {}).get("Total Products") and not v.get("profile", {}).get("Total Monthly Revenue")}
    m = (b["On Amazon"] == "Yes") & b["SmartScout Brand"].str.lower().isin(idle)
    b.loc[m, "On Amazon"] = "Possible"
    b.loc[m, "Amazon Confidence"] = "possible"
    b.loc[m, "Notes"] = b.loc[m, "Notes"].map(lambda n: "; ".join(filter(None, [
        n, "SmartScout knows the brand but shows no current products or revenue"])))
    b = b.sort_values(["Exhibitor ID", "Brand"])

    roll = []
    for eid, r in scope.iterrows():
        g = b[b["Exhibitor ID"] == eid]
        named = g[g["Brand"] != ""]
        yes = named[named["On Amazon"] == "Yes"]
        poss = named[named["On Amazon"] == "Possible"]
        pend = named[named["On Amazon"] == "Pending"]
        if g.empty:
            anyb, note = "", "Phase 3 research not done yet"
        else:
            anyb = "Yes" if len(yes) else "Possible" if len(poss) else "Pending" if len(pend) else "No"
            note = "" if len(named) else "No own brand identified"
        roll.append({
            "Exhibitor ID": eid, "Exhibitor Name": r["Exhibitor Name"], "Shows": r["Shows"],
            "Exhibitor Type": r["Exhibitor Type"], "Domain": r["Domain"], "Parent Company": r["Parent Company"],
            "Brands Found": len(named), "Brands On Amazon": len(yes),
            "Amazon Brand List": "; ".join(yes["Brand"]), "Any Brand On Amazon": anyb,
            "Amazon Checks Pending": len(pend),
            "SmartScout Monthly Revenue (Amazon brands)": yes["SS Monthly Revenue"].sum() if len(yes) else None,
            "Notes": note,
        })
    roll = pd.DataFrame(roll)
    readme = pd.DataFrame({"Note": [
        "Brands: brands each in-scope exhibitor owns, from the show page (About text, Brands section, exhibitor "
        "name), the exhibitor's own website brand pages, and the parent company. No web search was used "
        "(session search limit reached in phase 2).",
        "SmartScout check: every brand checked in SmartScout (Amazon US, Business plan) by exact name, then up to "
        "two name variants. Match counts only if the SmartScout category fits the product type.",
        "amazon.com check: amazon.com served a robot-check page to this session's browser, so per the run rules "
        "that source was paused and brands not found in SmartScout are marked 'Amazon check pending' / On Amazon "
        "'Pending'. They still need a manual or later amazon.com check.",
        "On Amazon: Yes = SmartScout exact/close match with current products. Possible = SmartScout knows the brand "
        "but shows no current products or revenue. Pending = not in SmartScout (or wrong match), amazon.com "
        "check still to do. No = no own brand identified.",
        "Any Brand On Amazon (rollup): Yes / Possible / Pending / No, best status across the exhibitor's brands.",
    ]})
    with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
        excel_safe(b).to_excel(xw, sheet_name="Brands", index=False)
        excel_safe(roll).to_excel(xw, sheet_name="Exhibitor Rollup", index=False)
        readme.to_excel(xw, sheet_name="Read Me", index=False)
    format_workbook(OUT)

    done = roll[roll["Any Brand On Amazon"] != ""]
    named = b[b["Brand"] != ""]
    print(f"Exhibitors researched: {len(done)} of {len(roll)}")
    print(f"Brands found: {len(named)}")
    print(f"Brands on Amazon (Yes): {sum(named['On Amazon'] == 'Yes')}")
    print("SmartScout Match:", named["SmartScout Match"].value_counts().to_dict())
    print(f"Exhibitors with at least one Amazon brand: {sum(done['Any Brand On Amazon'] == 'Yes')}")
    print(f"Rows still 'Amazon check pending': {sum(named['On Amazon'] == 'Pending')}")
    print(f"Exhibitors with no own brand: {sum(done['Brands Found'] == 0)}")
    state = load_state()
    state.setdefault("phase3", {}).update(researched=int(len(done)), brands=int(len(named)))
    save_state(state)


if __name__ == "__main__":
    main()

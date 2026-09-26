"""Phase 4 build -> phase4_smartscout.xlsx (sheets Brands, Exhibitor Rollup, Read Me).

Reads phase3_brands_amazon.xlsx, smartscout_cache.json (profiles from phase 3, sellers and
subcategories from phase 4) and phase4_checkpoint.jsonl.
"""
import json, os, sys
from datetime import datetime, timezone

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, load_state, save_state
from phase1_build import excel_safe, format_workbook
from phase4_work import SS_CACHE, done

OUT = os.path.join(ROOT, "phase4_smartscout.xlsx")
P4_COLS = ["Monthly Revenue", "Annual Revenue (TTM)", "Dominant Seller", "Dominant Seller Sales %",
           "Dominant Seller Type", "Top Subcategory 1", "Sub 1 Market Share", "Sub 1 Brand Rank",
           "Top Subcategory 2", "Sub 2 Market Share", "Sub 2 Brand Rank", "Top Subcategory 3",
           "Sub 3 Market Share", "Sub 3 Brand Rank", "Primary Category", "Primary Subcategory",
           "Total Products", "Total Reviews", "Average Rating", "Average Price", "Seller Count",
           "Reseller Share %", "Amazon 1P %", "MoM Growth", "12-Month MoM Growth", "Has Storefront",
           "Storefront URL", "Top 5 Sellers", "Data Pulled At", "Data Quality Flag"]
FLAG_RE = __import__("re").compile(r"collision|unrelated|homonym|not the exhibitor|same.name|different company|looks like", __import__("re").I)


def num(v):
    try:
        return float(v) if v not in ("", None) else None
    except (TypeError, ValueError):
        return None


def rank_val(v):
    if v in (None, ""):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return str(v)


def main():
    b = pd.read_excel(os.path.join(ROOT, "phase3_brands_amazon.xlsx"), sheet_name="Brands", dtype=str).fillna("")
    cache = json.load(open(SS_CACHE))
    cp = done()
    pulled = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lc = {k.lower(): v for k, v in cache.items()}
    rows = []
    for r in b.to_dict("records"):
        out = {c: None for c in P4_COLS}
        notes = [r["Notes"]] if r["Notes"] else []
        in_scope = r["On Amazon"] in ("Yes", "Possible")
        ss = r["SmartScout Brand"]
        if in_scope and r["SmartScout Match"] in ("exact", "close") and ss:
            c = lc.get(ss.lower(), {})
            prof = c.get("profile", {})
            out.update({
                "Monthly Revenue": num(prof.get("Total Monthly Revenue")),
                "Annual Revenue (TTM)": num(prof.get("Trailing 12-Month Revenue")),
                "Primary Category": prof.get("Primary Category") or None,
                "Primary Subcategory": prof.get("Primary Subcategory") or None,
                "Total Products": num(prof.get("Total Products")),
                "Total Reviews": num(prof.get("Total Reviews")),
                "Average Rating": num(prof.get("Average Rating")),
                "Average Price": num(prof.get("Average Price")),
                "MoM Growth": num(prof.get("Average MoM Growth")),
                "Has Storefront": prof.get("Has Storefront") or None,
                "Data Pulled At": pulled,
            })
            p4 = cp.get(ss.lower())
            if r["On Amazon"] == "Possible":
                notes.append("No current products in SmartScout; sellers and subcategories not pulled")
            elif p4 is None:
                notes.append("Phase 4 sellers/subcategory pull not done yet")
            else:
                sellers = sorted(p4.get("sellers") or [], key=lambda s: num(s.get("Estimated Brand Share")) or 0,
                                 reverse=True)
                if sellers:
                    top = sellers[0]
                    out["Dominant Seller"] = top.get("Seller Name")
                    out["Dominant Seller Sales %"] = num(top.get("Estimated Brand Share"))
                    out["Dominant Seller Type"] = top.get("Type")
                    out["Seller Count"] = len(sellers)
                    out["Amazon 1P %"] = round(sum(num(s.get("Estimated Brand Share")) or 0 for s in sellers
                                                   if s.get("Type") == "Amazon 1P"), 2)
                    out["Reseller Share %"] = round(sum(num(s.get("Estimated Brand Share")) or 0 for s in sellers
                                                        if s.get("Type") == "Third-party reseller"), 2)
                    out["Top 5 Sellers"] = "; ".join(
                        f"{s.get('Seller Name')}: {round(num(s.get('Estimated Brand Share')) or 0, 1)}%" for s in sellers[:5])
                    if len(sellers) >= 15:
                        notes.append("Seller list capped at 15 sellers")
                else:
                    notes.append("SmartScout returned no seller rows")
                for i, sc in enumerate((p4.get("subcats") or [])[:3], start=1):
                    out[f"Top Subcategory {i}"] = sc.get("Subcategory")
                    ms = num(sc.get("Market Share"))
                    out[f"Sub {i} Market Share"] = round(ms * 100, 3) if ms is not None and ms <= 1 else ms
                    out[f"Sub {i} Brand Rank"] = rank_val(sc.get("Rank"))
                if p4.get("notes"):
                    notes.append(p4["notes"])
                    if FLAG_RE.search(p4["notes"]):
                        out["Data Quality Flag"] = ("SmartScout brand name overlaps another company's products; "
                                                    "revenue may include them")
            if r.get("Ownership") == "Licensed":
                notes.append("Licensed brand: SmartScout figures cover every seller of the brand name")
        elif r["On Amazon"] == "Yes":
            notes.append("Not in SmartScout")
        row = dict(r)
        row.update(out)
        row["Notes"] = "; ".join(dict.fromkeys(n for n in notes if n))
        rows.append(row)
    bb = pd.DataFrame(rows)
    front = [c for c in b.columns if c != "Notes"]
    bb = bb[front + P4_COLS + ["Notes"]]

    amz = bb[bb["Monthly Revenue"].notna() & (bb["Ownership"] != "Licensed")]
    roll = []
    for eid, g in amz.groupby("Exhibitor ID"):
        g = g.sort_values("Monthly Revenue", ascending=False)
        roll.append({"Exhibitor ID": eid, "Exhibitor Name": g["Exhibitor Name"].iloc[0],
                     "Amazon Brands (SmartScout)": len(g), "Total Monthly Revenue": g["Monthly Revenue"].sum(),
                     "Total Annual Revenue (TTM)": g["Annual Revenue (TTM)"].sum(),
                     "Largest Brand": g["Brand"].iloc[0], "Largest Brand Monthly Revenue": g["Monthly Revenue"].iloc[0],
                     "Largest Brand Dominant Seller": g["Dominant Seller"].iloc[0],
                     "Largest Brand Dominant Seller Type": g["Dominant Seller Type"].iloc[0],
                     "Amazon Brand List": "; ".join(g["Brand"]),
                     "Data Quality Flag": "; ".join(sorted(set(f"{b}: same-name overlap" for b, fl in
                                                              zip(g["Brand"], g["Data Quality Flag"]) if fl)))})
    roll = pd.DataFrame(roll).sort_values("Total Monthly Revenue", ascending=False)
    readme = pd.DataFrame({"Note": [
        "Source: SmartScout MCP, Amazon US, Business plan (no revenue history, no ad data). Pulled " + pulled + ".",
        "Scope: brands with On Amazon = Yes or Possible and a SmartScout exact/close match. 'Possible' brands have "
        "no current products in SmartScout, so only profile fields are filled.",
        "Monthly Revenue / Annual Revenue (TTM), Total Products, Reviews, Rating, Price, MoM Growth, Has Storefront: "
        "SmartScout brand profile. MoM Growth is SmartScout's average month-over-month growth as a fraction "
        "(-0.27 = -27%). 12-Month MoM Growth and Storefront URL are not returned by SmartScout on this plan and are blank.",
        "Sellers: SmartScout 'which sellers sell the brand' (top 15 by brand share). Seller Count = sellers returned "
        "(15 means 15 or more). Dominant Seller Type: Amazon 1P (Amazon.com), Brand direct (seller is the brand or "
        "its owner), Third-party reseller. Reseller Share % = share held by third-party resellers; Amazon 1P % = "
        "Amazon.com's share.",
        "Top Subcategories: the brand's top 3 subcategories by the brand's revenue, with market share in %. Brand "
        "Rank = position among the subcategory's top 30 brands by revenue; '>30' when outside the top 30. (SmartScout's "
        "single query cannot return rank directly.)",
        "Data Quality Flag: SmartScout groups products by brand name, so a brand that shares its name with another "
        "company (e.g. Lucas, Monroe, Fox) can show revenue and subcategories that belong to the other company. "
        "Treat flagged revenue as an upper bound.",
        "Exhibitor Rollup: sums owned Amazon brands only (licensed brands excluded). Two exhibitors that list the "
        "same brand (e.g. a parent and its division) each show that brand's revenue.",
    ]})
    with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
        excel_safe(bb).to_excel(xw, sheet_name="Brands", index=False)
        excel_safe(roll).to_excel(xw, sheet_name="Exhibitor Rollup", index=False)
        readme.to_excel(xw, sheet_name="Read Me", index=False)
    format_workbook(OUT)

    pulled_rows = bb[bb["Monthly Revenue"].notna()]
    print(f"Brands with SmartScout data: {len(pulled_rows)} rows "
          f"({pulled_rows['SmartScout Brand'].str.lower().nunique()} unique SmartScout brands)")
    print(f"  with sellers/subcategories: {pulled_rows['Dominant Seller'].notna().sum()}")
    print(f"Brands on Amazon not in SmartScout: {(bb['Notes'].str.contains('Not in SmartScout')).sum()}")
    print("Top 15 exhibitors by combined monthly revenue:")
    for _, x in roll.head(15).iterrows():
        print(f"  {x['Exhibitor ID']} {x['Exhibitor Name'][:40]:40} ${x['Total Monthly Revenue']:>13,.0f}/mo  "
              f"largest: {x['Largest Brand']} (${x['Largest Brand Monthly Revenue']:,.0f})")
    state = load_state()
    state.setdefault("phase4", {}).update(brands_with_data=int(len(pulled_rows)))
    save_state(state)


if __name__ == "__main__":
    main()

"""Final Expo West master: one clean table with every Amazon-selling brand (no distributors), its decision makers,
its SmartScout data and its custom email, in colour-coded column groups.

  python3 pipeline/expowest_final.py      -> expowest_final_master.csv and pipeline/work/final_layout.json

One row per decision maker; a brand with nobody found gets one row saying so, so all brands are listed.
Column groups (colour in the sheet):
  Lead (green)              exhibitor, brand, first name, last name, email
  Contact details (green)   title, LinkedIn, country, priority, email status and checks, send status
  Custom email (pink)       the brand's email (same for every contact at the brand), angle, QA flags, review decision
  SmartScout (yellow)       Amazon US data for the exact store: revenue, units, categories, sellers, growth
  Amazon store (purple)     store name and the product used to confirm it
  Company research (orange) type, domain, parent company and sources
  Show list (blue)          tier, years, booths, website, address, socials, old database match
"""
import csv, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
MASTER = os.path.join(ROOT, "expowest_amazon_master.csv")
OUT = os.path.join(ROOT, "expowest_final_master.csv")
LAYOUT = os.path.join(WORK, "final_layout.json")

GROUPS = [  # (group, header colour, cell colour, [(column, source key or callable)])
    ("Lead", "#2E7D32", "#E8F5E9", ["Exhibitor", "Brand", "First Name", "Last Name", "Email"]),
    ("Contact details", "#558B2F", "#F1F8E9", ["Title", "LinkedIn URL", "Country", "Contact Priority", "Email Status",
                                               "Email Check", "Send Status"]),
    ("Custom email", "#AD1457", "#FCE4EC", ["Email Body", "Email Angle", "Email QA Flags", "Review Decision"]),
    ("SmartScout", "#F9A825", "#FFFDE7", ["SmartScout Brand", "SmartScout Match", "Monthly Revenue", "12-Month Revenue",
                                          "Monthly Units", "Primary Category", "Primary Subcategory", "Total Products",
                                          "Total Reviews", "Average Rating", "Average Price", "Average Sellers per Listing",
                                          "MoM Growth %", "12-Mo Avg MoM Growth %", "Amazon Revenue Share %",
                                          "Brand Own Account Share %", "Top Sellers (share of brand revenue)",
                                          "Top Subcategories (brand revenue, market share)", "Has Storefront"]),
    ("Amazon store", "#6A1B9A", "#F3E5F5", ["Amazon Status", "Amazon Store Name", "Has Amazon Store", "Amazon Brand Field",
                                            "Sample ASIN", "Sample Product", "Sold By"]),
    ("Company research", "#E65100", "#FFF3E0", ["Exhibitor Type", "Type Reason", "Domain", "Domain Found", "Domain Source",
                                                "Parent Company", "Parent Domain", "Parent Source", "Research Notes"]),
    ("Show list", "#1565C0", "#E3F2FD", ["Exhibitor ID", "Priority Tier", "In 2027 List", "Years Exhibited", "Booths",
                                         "Website", "Address", "Social Links", "Also Listed As", "In Old Database",
                                         "Old DB Already Sent", "Old DB Company", "Show URLs"]),
]
NUMERIC = {"Monthly Revenue", "12-Month Revenue", "Monthly Units", "Total Products", "Total Reviews", "Average Rating",
           "Average Price", "Average Sellers per Listing", "MoM Growth %", "12-Mo Avg MoM Growth %",
           "Amazon Revenue Share %", "Brand Own Account Share %", "Contact Priority"}


def num(v):
    try:
        f = float(str(v).replace(",", "").replace("$", "").replace("%", ""))
        return int(f) if f.is_integer() else round(f, 2)
    except (TypeError, ValueError):
        return ""


MANGLED = re.compile("Ã.|Â.|â€|â[\x80-\x9f]")


def unmangle(s):
    """Undo text that was UTF-8 read as Windows-1252, sometimes more than once (old database: CafÃƒÂƒÃ‚Â© -> Café)."""
    for _ in range(5):
        if not MANGLED.search(s):
            break
        fixed = None
        for enc in ("cp1252", "latin-1"):
            try:
                fixed = s.encode(enc).decode("utf-8")
                break
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
        if not fixed or fixed == s:
            break
        s = fixed
    # stray C1 control characters are Windows-1252 punctuation read as Latin-1 (\x92 -> ’)
    s = re.sub("[\x80-\x9f]", lambda m: bytes([ord(m.group())]).decode("cp1252", "ignore"), s)
    return s.replace("​", "")


def records():
    out = {}
    for f in sorted(glob.glob(os.path.join(WORK, "lg_in_*.jsonl")), key=lambda f: int(re.search(r"_(\d+)\.", f).group(1))):
        for l in open(f, encoding="utf-8"):
            r = json.loads(l)
            out[r["id"]] = r
    return out


def build():
    ss = {r["Exhibitor ID"]: r for r in csv.DictReader(open(os.path.join(ROOT, "smartscout_brands.csv"), encoding="utf-8"))}
    ex = {r["Exhibitor ID"]: r for r in csv.DictReader(open(os.path.join(ROOT, "expowest_master.csv"), encoding="utf-8"))}
    lg = records()
    cols = [c for _, _, _, cs in GROUPS for c in cs]
    rows = []
    for m in csv.DictReader(open(MASTER, encoding="utf-8")):
        eid, s, r = m["Exhibitor ID"], ss.get(m["Exhibitor ID"], {}), lg.get(m["Exhibitor ID"], {})
        sellers = "; ".join(f'{x["seller"]} {x["share_pct"]}%' if x.get("share_pct") is not None else x["seller"]
                            for x in r.get("top_sellers") or [])
        subs = "; ".join(f'{x["subcategory"]}: {x.get("brand_revenue") or "n/a"}, {x.get("market_share_pct")}% share'
                         for x in r.get("top_subcategories") or [])
        mrr = num(s.get("Monthly Revenue"))
        row = {
            "Exhibitor": m["Exhibitor"],
            "Brand": m["Amazon Store Name"] or s.get("SmartScout Brand") or m["Exhibitor"],
            "First Name": m["First Name"], "Last Name": m["Last Name"], "Email": m["Email"],
            "Title": m["Title"], "LinkedIn URL": m["LinkedIn URL"], "Country": m["Country"],
            "Contact Priority": num(m["Priority"]), "Email Status": m["Email Status"], "Email Check": m["Email Check"],
            "Send Status": m["Row Status"],
            "Email Body": m["Email Body"], "Email Angle": m["Email Angle"], "Email QA Flags": m["Email QA Flags"],
            "Review Decision": "",
            "SmartScout Brand": s.get("SmartScout Brand", ""), "SmartScout Match": s.get("SmartScout Match", ""),
            "Monthly Revenue": mrr, "12-Month Revenue": num(s.get("TTM Revenue")),
            "Monthly Units": num(s.get("Monthly Units")), "Primary Category": s.get("Primary Category", ""),
            "Primary Subcategory": s.get("Primary Subcategory", ""), "Total Products": num(s.get("Total Products")),
            "Total Reviews": num(s.get("Total Reviews")), "Average Rating": num(s.get("Average Rating")),
            "Average Price": num(s.get("Average Price")), "Average Sellers per Listing": num(s.get("Average Sellers")),
            "MoM Growth %": num(s.get("MoM Growth")), "12-Mo Avg MoM Growth %": num(s.get("12-Month MoM Growth")),
            "Amazon Revenue Share %": num(s.get("Amazon Revenue %")),
            "Brand Own Account Share %": r.get("brand_own_share_pct", "") if r.get("top_sellers") else "",
            "Top Sellers (share of brand revenue)": sellers,
            "Top Subcategories (brand revenue, market share)": subs, "Has Storefront": s.get("Has Storefront", ""),
            "Show URLs": m["Show URLs"], "Social Links": ex.get(eid, {}).get("Social Links", ""),
        }
        for c in cols:
            if c not in row:
                row[c] = m.get(c, "")
        rows.append(row)
    for row in rows:
        for c in cols:
            if isinstance(row[c], str):
                row[c] = re.sub(r"\s*[–—]\s*", ", ", unmangle(row[c]))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    spans, i = [], 0
    for g, head, cell, cs in GROUPS:
        spans.append({"group": g, "header": head, "cell": cell, "start": i, "end": i + len(cs), "columns": cs})
        i += len(cs)
    json.dump({"columns": cols, "groups": spans, "numeric": sorted(NUMERIC), "rows": len(rows)}, open(LAYOUT, "w"), indent=1)
    from collections import Counter
    print(f"{len(rows)} rows, {len({r['Exhibitor'] + r['Brand'] for r in rows})} brands, {len(cols)} columns -> {OUT}")
    print(dict(Counter(r["Send Status"] for r in rows)))


if __name__ == "__main__":
    build()

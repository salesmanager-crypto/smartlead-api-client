"""Phase 2 build: domain, parent company, exhibitor type -> phase2_domains.xlsx.

Reads phase1_exhibitors.xlsx, pipeline/work/site_signals.csv and phase2_checkpoint.csv.
"""
import os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, domain_of, load_state, registrable_domain, save_state
from phase1_build import excel_safe, format_workbook
from phase2_work import CP, company_host

OUT = os.path.join(ROOT, "phase2_domains.xlsx")
AGGREGATORS = ("cbinsights.", "pitchbook.", "zoominfo.", "crunchbase.", "mergr.", "craft.co", "owler.",
               "rocketreach.", "dnb.com", "tracxn.", "apollo.io", "signalhire.", "leadiq.", "growjo.")
SCOPE = {"Brand / Manufacturer": "Research", "Distributor / Wholesaler": "Research", "Unclear": "Research",
         "Service / Software / Media / Association": "Skip", "Tool & Equipment / Shop Supplier": "Skip"}


def main():
    ex = pd.read_excel(os.path.join(ROOT, "phase1_exhibitors.xlsx"), sheet_name="Exhibitors",
                       dtype=str).fillna("")
    import gzip, json
    from phase2_fetch_sites import SITE_CACHE, signals

    def site_sig(website):
        h = company_host(website)
        path = os.path.join(SITE_CACHE, h + ".json.gz") if h else ""
        if not path or not os.path.exists(path):
            return {}
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return {k: str(v) for k, v in signals(json.load(fh)).items()}
    cp = pd.read_csv(CP, dtype=str, keep_default_na=False).drop_duplicates("Exhibitor ID") \
        .set_index("Exhibitor ID") if os.path.exists(CP) else pd.DataFrame()

    overrides = {}
    ov_path = os.path.join(ROOT, "pipeline", "work", "p2_overrides.csv")
    if os.path.exists(ov_path):
        for o in pd.read_csv(ov_path, dtype=str, keep_default_na=False).to_dict("records"):
            overrides.setdefault(o["Exhibitor ID"], []).append(o)

    rows = []
    for r in ex.to_dict("records"):
        eid = r["Exhibitor ID"]
        notes = [r["Notes"]] if r["Notes"] else []
        c = cp.loc[eid].to_dict() if eid in cp.index else None
        s = site_sig(r["Website"])

        host = company_host(r["Website"])
        if host:
            domain, conf = host, "from show page"
            final = domain_of(s.get("Site Final URL", ""))
            if s.get("Site Error") or s.get("Site Status") in ("", "0"):
                notes.append("Website did not load when fetched")
            elif s.get("Site Status", "").isdigit() and int(s["Site Status"]) >= 400:
                notes.append(f"Website returned HTTP {s['Site Status']}")
            elif final and registrable_domain(final) != registrable_domain(host):
                notes.append(f"Website redirects to {final}")
        elif c and c.get("Domain Found"):
            domain, conf = domain_of(c["Domain Found"]) or c["Domain Found"], "found by search"
            if r["Website"]:
                notes.append(f"Show page website was not a company site ({r['Website']})")
        else:
            domain, conf = "", "not found"
            if c is not None:
                notes.append("No company domain on show page or by search")

        if c is None:
            etype = reason = parent = pdom = psrc = pq = ""
            notes.append("Phase 2 research not done yet")
        else:
            etype, reason = c["Exhibitor Type"], c["Type Reason"]
            parent, pdom, psrc, pq = (c["Parent Company"], domain_of(c["Parent Domain"]) or c["Parent Domain"],
                                      c["Parent Source"], c["Parent Query"])
            if c.get("Notes"):
                notes.append(c["Notes"])
            if psrc.strip().lower() in ("site_about_url", "site about url"):
                psrc = s.get("About URL", "") or r["Website"]
            for o in overrides.get(eid, []):
                if o["Field"] == "Parent Company":
                    parent = o["Value"]
                    pdom, psrc = "", ("" if not parent else "show page exhibitor name")
                elif o["Field"] == "Exhibitor Type":
                    etype = o["Value"]
                if o["Note"]:
                    notes.append(o["Note"])
            if parent and any(a in psrc.lower() for a in AGGREGATORS):
                notes.append("Parent source is a data-aggregator profile; verify")
        rows.append({
            "Exhibitor ID": eid, "Exhibitor Name": r["Exhibitor Name"], "Shows": r["Shows"],
            "AAPEX Booth": r["AAPEX Booth"], "SEMA Booth": r["SEMA Booth"], "Website": r["Website"],
            "Domain": domain, "Domain Confidence": conf, "Parent Company": parent,
            "Parent Domain": pdom, "Parent Source": psrc, "Exhibitor Type": etype,
            "Type Reason": reason, "Phase 3 Scope": SCOPE.get(etype, ""),
            "LinkedIn": r["LinkedIn"], "About Summary": r["About Summary"], "Categories": r["Categories"],
            "Show Brands": r["Show Brands"], "About": r["About"],
            "Site About URL": s.get("About URL", ""), "Site Brand Links": s.get("Brand Links", ""),
            "Parent Search Query": pq, "Notes": "; ".join(dict.fromkeys(n for n in notes if n)),
        })
    out = pd.DataFrame(rows)
    readme = pd.DataFrame({"Note": [
        "Domain: from the show-page Website (protocol, www and path stripped); for missing or marketplace "
        "websites, one web search '<name> official site'. Domain Confidence says which.",
        "Parent Company: filled only when a source states it plainly (company About page, or one web search "
        "'<name> <domain> parent company OR acquired by OR subsidiary of'). Parent Source is that URL. "
        "Blank = no stated parent found; many exhibitors are independent.",
        "LinkedIn company pages could not be read in this session (LinkedIn requires login), so the LinkedIn "
        "check for parent companies was not possible.",
        "Exhibitor Type and Type Reason: decided from the show About text, categories and the company website.",
        "Phase 3 Scope: Research for Brand / Manufacturer, Distributor / Wholesaler and Unclear; Skip otherwise. "
        "Flip any row to Research before phase 3 to include it.",
        "Site Brand Links: links on the company homepage that mention 'brand' (a starting point for phase 3).",
    ]})
    with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
        excel_safe(out).to_excel(xw, sheet_name="Exhibitors", index=False)
        readme.to_excel(xw, sheet_name="Read Me", index=False)
    format_workbook(OUT)

    done = out[out["Exhibitor Type"] != ""]
    print(f"Exhibitors: {len(out)}; researched: {len(done)}")
    print("By Exhibitor Type:")
    for k, v in done["Exhibitor Type"].value_counts().items():
        print(f"  {k}: {v}")
    print(f"With parent company: {sum(done['Parent Company'] != '')}")
    print(f"Phase 3 scope Research: {sum(done['Phase 3 Scope'] == 'Research')}, Skip: {sum(done['Phase 3 Scope'] == 'Skip')}")
    print("Domain Confidence:", out["Domain Confidence"].value_counts().to_dict())
    state = load_state()
    state.setdefault("phase2", {}).update(researched=len(done), exhibitors=len(out))
    save_state(state)
    return out


if __name__ == "__main__":
    main()

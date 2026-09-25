"""Phase 1 build: dedupe AAPEX + SEMA pulls, attach About summaries, write phase1_exhibitors.xlsx.

Reads phase1_checkpoint.csv (from phase1_scrape.py) and pipeline/work/summaries.csv
(About Summary per About text hash). Exhibitor IDs are assigned once and persisted in
run_state.json (phase1.exhibitor_ids keyed by the sorted member keys), so reruns keep them.
"""
import hashlib, os, sys
from collections import defaultdict

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NON_COMPANY_DOMAINS, ROOT, domain_of, load_state, norm_name, save_state

CP_PATH = os.path.join(ROOT, "phase1_checkpoint.csv")
SUMMARIES = os.path.join(ROOT, "pipeline", "work", "summaries.csv")
OUT = os.path.join(ROOT, "phase1_exhibitors.xlsx")


def about_key(text):
    return hashlib.sha1((text or "").strip().encode("utf-8")).hexdigest()[:16]


def company_domain(url):
    d = domain_of(url)
    if not d:
        return ""
    for bad in NON_COMPANY_DOMAINS:
        if d == bad or d.endswith("." + bad):
            return ""
    return d


def split_list(s):
    return [x.strip() for x in (s or "").split(";") if x.strip()]


def load_raw():
    df = pd.read_csv(CP_PATH, dtype=str, keep_default_na=False)
    df = df.drop_duplicates("Key", keep="last")
    df["_nn"] = df["Exhibitor Name"].map(norm_name)
    df["_dom"] = df["Website"].map(company_domain)
    return df


def collapse_within_show(df):
    """Merge rows in the same show that share a normalized name (one company, several listings)."""
    out = []
    for (show, nn), g in df.groupby(["Show", "_nn"], sort=False):
        if not nn or len(g) == 1:
            out.extend(g.to_dict("records"))
            continue
        recs = g.to_dict("records")
        base = dict(max(recs, key=lambda r: len(r["About"])))
        base["Key"] = "+".join(r["Key"] for r in recs)
        base["Booth"] = "; ".join(dict.fromkeys(b for r in recs for b in split_list(r["Booth"])))
        base["Detail URL"] = " | ".join(r["Detail URL"] for r in recs)
        base["Categories"] = "; ".join(dict.fromkeys(c for r in recs for c in split_list(r["Categories"])))
        base["Show Brands"] = "; ".join(dict.fromkeys(c for r in recs for c in split_list(r["Show Brands"])))
        for f in ("Website", "LinkedIn", "Address City", "Address State", "Address Country"):
            base[f] = base[f] or next((r[f] for r in recs if r[f]), "")
        base["_dom"] = base["_dom"] or next((r["_dom"] for r in recs if r["_dom"]), "")
        base["Notes"] = "; ".join(filter(None, [f"Listed {len(recs)} times in {show} (exhids "
                                                + ", ".join(r["exhid"] for r in recs) + "); merged"]
                                             + [r["Notes"] for r in recs if r["Notes"]]))
        out.append(base)
    return pd.DataFrame(out)


def match(df):
    a = df[df.Show == "AAPEX"].copy()
    s = df[df.Show == "SEMA"].copy()
    pairs, basis, notes = [], {}, defaultdict(list)
    used_a, used_s = set(), set()

    # 1) normalized-name matches (one-to-one; if a name repeats inside a show, pair in order)
    s_by_name = defaultdict(list)
    for k, nn in zip(s.Key, s._nn):
        if nn:
            s_by_name[nn].append(k)
    for k, nn in zip(a.Key, a._nn):
        cands = [c for c in s_by_name.get(nn, []) if c not in used_s]
        if nn and cands:
            pairs.append((k, cands[0]))
            used_a.add(k)
            used_s.add(cands[0])
            basis[(k, cands[0])] = "name"

    # 2) domain matches among the rest; only when the domain is unique to one row in each show
    dom_a = a[~a.Key.isin(used_a) & (a._dom != "")].groupby("_dom").Key.apply(list)
    dom_s = s[~s.Key.isin(used_s) & (s._dom != "")].groupby("_dom").Key.apply(list)
    all_dom_a = a[a._dom != ""].groupby("_dom").Key.apply(list)
    all_dom_s = s[s._dom != ""].groupby("_dom").Key.apply(list)
    for dom, ka in dom_a.items():
        ks = dom_s.get(dom)
        if not ks:
            continue
        if len(all_dom_a[dom]) == 1 and len(all_dom_s[dom]) == 1:
            pairs.append((ka[0], ks[0]))
            used_a.add(ka[0])
            used_s.add(ks[0])
            basis[(ka[0], ks[0])] = "domain"
        else:
            for k in ka + ks:
                notes[k].append(f"Shares website domain {dom} with another exhibitor; not merged on domain")

    # upgrade name matches whose domains also agree
    lookup = df.set_index("Key")
    for p in pairs:
        if basis[p] == "name":
            da, ds = lookup.at[p[0], "_dom"], lookup.at[p[1], "_dom"]
            if da and da == ds:
                basis[p] = "both"
            elif da and ds and da != ds:
                notes[p[0]].append(f"Name match but websites differ ({da} vs {ds})")
    return pairs, basis, notes, used_a, used_s


def merge_rows(ra, rs, match_basis, extra_notes):
    def pick_longer(field):
        va, vs = ra.get(field, ""), rs.get(field, "")
        return va if len(va) >= len(vs) else vs

    notes = []
    for r in (ra, rs):
        if r.get("Notes"):
            notes.append(f"{r['Show']}: {r['Notes']}")
    name = ra["Exhibitor Name"] or rs["Exhibitor Name"]
    if rs["Exhibitor Name"] and rs["Exhibitor Name"] != ra["Exhibitor Name"]:
        notes.append(f"SEMA lists name as '{rs['Exhibitor Name']}'")
    website = ra["Website"] or rs["Website"]
    if ra["Website"] and rs["Website"] and company_domain(ra["Website"]) != company_domain(rs["Website"]):
        notes.append(f"SEMA website: {rs['Website']}")
    cats = list(dict.fromkeys(split_list(ra["Categories"]) + split_list(rs["Categories"])))
    brands = list(dict.fromkeys(split_list(ra["Show Brands"]) + split_list(rs["Show Brands"])))
    notes += extra_notes
    return {
        "Exhibitor Name": name, "Shows": "AAPEX; SEMA",
        "AAPEX Booth": ra["Booth"], "SEMA Booth": rs["Booth"],
        "AAPEX URL": ra["Detail URL"], "SEMA URL": rs["Detail URL"],
        "Website": website, "LinkedIn": ra["LinkedIn"] or rs["LinkedIn"],
        "About": pick_longer("About"), "Categories": "; ".join(cats),
        "Show Brands": "; ".join(brands),
        "Address City": ra["Address City"] or rs["Address City"],
        "Address State": ra["Address State"] or rs["Address State"],
        "Address Country": ra["Address Country"] or rs["Address Country"],
        "Match Basis": match_basis, "Source Keys": f"{ra['Key']}; {rs['Key']}",
        "Notes": "; ".join(notes),
    }


def single_row(r, extra_notes):
    show = r["Show"]
    notes = ([r["Notes"]] if r.get("Notes") else []) + extra_notes
    return {
        "Exhibitor Name": r["Exhibitor Name"], "Shows": show,
        "AAPEX Booth": r["Booth"] if show == "AAPEX" else "",
        "SEMA Booth": r["Booth"] if show == "SEMA" else "",
        "AAPEX URL": r["Detail URL"] if show == "AAPEX" else "",
        "SEMA URL": r["Detail URL"] if show == "SEMA" else "",
        "Website": r["Website"], "LinkedIn": r["LinkedIn"], "About": r["About"],
        "Categories": r["Categories"], "Show Brands": r["Show Brands"],
        "Address City": r["Address City"], "Address State": r["Address State"],
        "Address Country": r["Address Country"], "Match Basis": "", "Source Keys": r["Key"],
        "Notes": "; ".join(notes),
    }


def main():
    state = load_state()
    raw = load_raw()
    qa = os.path.join(ROOT, "pipeline", "work", "qa_notes.csv")
    if os.path.exists(qa):
        for k, note in pd.read_csv(qa, dtype=str, keep_default_na=False).values:
            m = raw.Key == k
            raw.loc[m, "Notes"] = raw.loc[m, "Notes"].map(lambda n: "; ".join(filter(None, [n, note])))
    df = collapse_within_show(raw)
    pairs, basis, notes, used_a, used_s = match(df)
    rows = {r["Key"]: r for r in df.to_dict("records")}
    out = []
    for ka, ks in pairs:
        out.append(merge_rows(rows[ka], rows[ks], basis[(ka, ks)], notes[ka] + notes[ks]))
    for k, r in rows.items():
        if k not in used_a and k not in used_s:
            out.append(single_row(r, notes[k]))

    # About Summary
    summ = {}
    if os.path.exists(SUMMARIES):
        sdf = pd.read_csv(SUMMARIES, dtype=str, keep_default_na=False)
        summ = dict(zip(sdf["about_key"], sdf["summary"]))
    missing_summary = 0
    for r in out:
        if r["About"]:
            s = summ.get(about_key(r["About"]), "")
            r["About Summary"] = s
            if not s:
                missing_summary += 1
                r["Notes"] = "; ".join(filter(None, [r["Notes"], "About Summary not generated yet"]))
        else:
            r["About Summary"] = ""

    # stable Exhibitor IDs
    ids = state.setdefault("phase1", {}).setdefault("exhibitor_ids", {})
    by_member = {}
    for member_key, eid in ids.items():
        for k in member_key.split("; "):
            by_member[k] = eid
    next_n = max([int(e[1:]) for e in ids.values()] or [0]) + 1
    out.sort(key=lambda r: (norm_name(r["Exhibitor Name"]), r["Source Keys"]))
    for r in out:
        mk = r["Source Keys"]
        eid = ids.get(mk) or next((by_member[k] for k in mk.split("; ") if k in by_member), None)
        if not eid:
            eid = f"E{next_n:04d}"
            next_n += 1
        ids[mk] = eid
        r["Exhibitor ID"] = eid
    save_state(state)

    cols = ["Exhibitor ID", "Exhibitor Name", "Shows", "AAPEX Booth", "SEMA Booth", "Website",
            "LinkedIn", "About", "About Summary", "Categories", "Show Brands", "Address City",
            "Address State", "Address Country", "AAPEX URL", "SEMA URL", "Match Basis",
            "Source Keys", "Notes"]
    ex = pd.DataFrame(out)[cols].sort_values("Exhibitor ID")
    raw_cols = ["Key", "Show", "exhid", "Exhibitor Name", "Booth", "Website", "LinkedIn", "About",
                "Categories", "All Categories Count", "Show Brands", "Address City",
                "Address State", "Address Country", "Detail URL", "Gallery Name",
                "Gallery Booths", "Fetched At", "Notes"]
    raw_a = raw[raw.Show == "AAPEX"][raw_cols]
    raw_s = raw[raw.Show == "SEMA"][raw_cols]
    ex, raw_a, raw_s = (excel_safe(t) for t in (ex, raw_a, raw_s))
    with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
        ex.to_excel(xw, sheet_name="Exhibitors", index=False)
        raw_a.to_excel(xw, sheet_name="Raw AAPEX", index=False)
        raw_s.to_excel(xw, sheet_name="Raw SEMA", index=False)
    format_workbook(OUT)

    both = ex[ex.Shows == "AAPEX; SEMA"]
    print(f"Raw AAPEX: {len(raw_a)}  (gallery total {state['phase1'].get('AAPEX', {}).get('gallery_total')})")
    print(f"Raw SEMA:  {len(raw_s)}  (gallery total {state['phase1'].get('SEMA', {}).get('gallery_total')})")
    print(f"Merged exhibitors: {len(ex)}")
    print(f"In both shows: {len(both)}  (by name {sum(both['Match Basis']=='name')}, "
          f"domain {sum(both['Match Basis']=='domain')}, both {sum(both['Match Basis']=='both')})")
    print(f"With website: {sum(ex.Website != '')}  LinkedIn: {sum(ex.LinkedIn != '')}  About: {sum(ex.About != '')}")
    print(f"Rows missing About Summary: {missing_summary}")
    return ex


def excel_safe(frame):
    from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
    return frame.apply(lambda col: col.map(
        lambda v: ILLEGAL_CHARACTERS_RE.sub("", v)[:32000] if isinstance(v, str) else v))


def format_workbook(path):
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment, Font
    wb = load_workbook(path)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        for c in ws[1]:
            c.font = Font(bold=True)
        for col in ws.columns:
            header = col[0].value or ""
            width = 60 if header in ("About",) else 45 if header in ("About Summary", "Categories", "Notes") else 18
            ws.column_dimensions[col[0].column_letter].width = width
            if header in ("About", "About Summary"):
                for c in col[1:]:
                    c.alignment = Alignment(wrap_text=False, vertical="top")
        ws.auto_filter.ref = ws.dimensions
    wb.save(path)


if __name__ == "__main__":
    main()

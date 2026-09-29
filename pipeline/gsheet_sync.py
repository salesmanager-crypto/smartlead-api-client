"""Build the value blocks that update the Google Sheet after a recheck batch.

  python gsheet_sync.py people N    rows for People!A{N}:K... (people with Notes 'Found in recheck' whose
                                    Exhibitor ID is in the given chunks) -> JSON on stdout
  python gsheet_sync.py rows IDS    for the exhibitors (comma-separated IDs): their sheet rows (position in
                                    the Coverage order + 2) and the G:H, K, M:N values, as contiguous blocks

The sheet's Shortfall Report and People tabs are in the same order as the local build (Coverage order,
people in build order), so row = index + 2. Values are printed as JSON ready for update_values.
"""
import json, os, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

MASTER = os.path.join(ROOT, "AAPEX_SEMA_MASTER.xlsx")
P5 = os.path.join(ROOT, "phase5_decision_makers.xlsx")


def people(chunks):
    p = pd.read_excel(P5, sheet_name="People").fillna("")
    p = p[p["Name"] != ""]
    cp = pd.read_csv(os.path.join(ROOT, "phase5_recheck_people.csv"), dtype=str, keep_default_na=False)
    keys = set((r["Exhibitor ID"], r["Name"]) for r in cp[cp["Chunk"].isin(chunks)].to_dict("records"))
    rows = []
    for _, x in p.iterrows():
        if (x["Exhibitor ID"], x["Name"]) in keys:
            rows.append([x["Exhibitor ID"], x["Exhibitor Name"], x["Name"], x["Title (as shown)"], x["LinkedIn URL"],
                         int(x["Priority"]) if x["Priority"] != "" else "", x["Match Reason"], x["Search Query"],
                         "unverified", x["Notes"], x["Company LinkedIn"]])
    return rows


def rows(ids):
    r = pd.read_excel(MASTER, sheet_name="P5 Shortfall Report").fillna("")
    r["row"] = r.index + 2
    sel = r[r["Exhibitor ID"].isin(ids)].sort_values("row")
    blocks, cur = [], []
    for x in sel.to_dict("records"):
        if cur and x["row"] != cur[-1]["row"] + 1:
            blocks.append(cur)
            cur = []
        cur.append(x)
    if cur:
        blocks.append(cur)
    out = []
    for b in blocks:
        a, z = b[0]["row"], b[-1]["row"]
        out.append({"GH": {"range": f"'Shortfall Report'!G{a}:H{z}",
                           "values": [[x["Search Status"], int(x["Web Searches Run"])] for x in b]},
                    "K": {"range": f"'Shortfall Report'!K{a}:K{z}", "values": [[x["Reason Code"]] for x in b]},
                    "MN": {"range": f"'Shortfall Report'!M{a}:N{z}",
                           "values": [[x["Reason Detail"], x["Rejected Candidates"]] for x in b]},
                    "ids": [x["Exhibitor ID"] for x in b]})
    return out


if __name__ == "__main__":
    if sys.argv[1] == "people":
        print(json.dumps(people(sys.argv[2].split(",")), ensure_ascii=False))
    else:
        print(json.dumps(rows(sys.argv[2].split(",")), ensure_ascii=False))

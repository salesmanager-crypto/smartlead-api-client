"""First-touch cold emails in Yoni's voice, one per decision maker.

  python cold_emails.py export N     write pipeline/work/ce_in_XX.jsonl chunks of N people (people with an email
                                     first), each with the facts the email may use
  python cold_emails.py check        validate every ce_out_XX.jsonl line against the cold-mode rules; prints
                                     failures (the agents fix and rewrite those keys)
  python cold_emails.py collect      merge passing emails -> cold_emails.csv
  python cold_emails.py status

Agents (prompt pipeline/ce_agent_prompt.txt) write the emails. The facts come from the pipeline files only:
show and booth (phase 1), the exact Amazon store name (amazon_stores.csv), SmartScout numbers rounded here so
the writer never sees an exact figure, and the person's title from Surfe.
"""
import glob, json, os, re, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
OUT = os.path.join(ROOT, "cold_emails.csv")
CAL = "https://calendly.com/yonilebovits/30min"
BANNED = [r"—", r"–", r"!", r"\bI'?d love\b", r"\bwould love\b", r"hope this (email )?finds",
          r"\bleverag", r"\bsynerg", r"game.?changer", r"unlock", r"strategic opportunit", r"smartscout",
          r"\bbump", r"[\U0001F300-\U0001FAFF☀-➿]", r"^\s*[-*•]", r"\$\d{1,3},\d{3}",
          r"touch base", r"circle back", r"\bquick question\b"]


def money(x):
    """Rounded monthly revenue phrase, or '' when too small or missing to be worth citing."""
    try:
        x = float(x)
    except (TypeError, ValueError):
        return ""
    if x < 5000 or x > 3000000:
        return ""  # too small to be worth citing, or a whole-brand figure too big to pin on one division
    if x < 100000:
        return f"about ${int(round(x / 5000.0) * 5)}k a month"
    if x < 1000000:
        return f"about ${int(round(x / 50000.0) * 50)}k a month"
    v = round(x / 1e6, 1)
    return f"about ${v:g}M a month"


def pct(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def brand_facts():
    """Exhibitor ID -> facts for its main verified Amazon brand."""
    a = pd.read_csv(os.path.join(ROOT, "amazon_stores.csv"), dtype=str).fillna("")
    b = pd.read_csv(os.path.join(ROOT, "smartscout_store.csv"), dtype=str).fillna("")
    ss = b.set_index("Key").to_dict("index")
    out = {}
    for _, r in a.iterrows():
        if r["Amazon Status"] not in ("verified", "possible"):
            continue
        s = ss.get(r["Key"], {})
        rev = pd.to_numeric(s.get("Monthly Revenue", ""), errors="coerce")
        rev = 0 if pd.isna(rev) else float(rev)
        f = {"brand": r["Brand"], "amazon_store_name": r["Amazon Store Name"],
             "has_amazon_store": r["Has Amazon Store"] == "True", "amazon_status": r["Amazon Status"],
             "monthly_revenue": money(rev), "top_subcategory": s.get("Top Subcategory 1", ""),
             "dominant_seller_type": s.get("Dominant Seller Type", ""), "rev": rev}
        rs = pct(s.get("Reseller Share %"))
        f["resellers_most_sales"] = bool(rs is not None and rs >= 50)
        cur = out.get(r["Exhibitor ID"])
        rank = (r["Amazon Status"] == "verified", rev)
        if cur is None or rank > (cur["amazon_status"] == "verified", cur["rev"]):
            out[r["Exhibitor ID"]] = f
    return out


def export(n):
    p = pd.read_csv(os.path.join(ROOT, "surfe_people.csv"), dtype=str).fillna("")
    from surfe_emails import person_key
    p["key"] = p.apply(person_key, axis=1)
    em = {}
    if os.path.exists(os.path.join(ROOT, "surfe_emails.csv")):
        e = pd.read_csv(os.path.join(ROOT, "surfe_emails.csv"), dtype=str).fillna("")
        em = dict(zip(e["Key"], e["Email"]))
    ex = pd.read_excel(os.path.join(ROOT, "phase2_domains.xlsx"), sheet_name="Exhibitors", dtype=str).fillna("")
    ex = ex.set_index("Exhibitor ID").to_dict("index")
    facts = brand_facts()
    queued = set()
    for f in glob.glob(os.path.join(WORK, "ce_in_*.jsonl")):
        queued |= {json.loads(l)["key"] for l in open(f)}
    rows = []
    for _, r in p.iterrows():
        if r["key"] in queued or r["Exhibitor ID"] not in facts:
            continue
        x = ex.get(r["Exhibitor ID"], {})
        shows = []
        for show in ("AAPEX", "SEMA"):
            if show in x.get("Shows", ""):
                booth = x.get(f"{show} Booth", "")
                shows.append(f"{show} booth {booth}" if booth else show)
        f = {k: v for k, v in facts[r["Exhibitor ID"]].items() if k != "rev"}
        rows.append({"key": r["key"], "id": r["Exhibitor ID"], "has_email": bool(em.get(r["key"])),
                     "first_name": r["First Name"], "last_name": r["Last Name"], "title": r["Title"],
                     "company": x.get("Exhibitor Name", r["Exhibitor Name"]), "shows": "; ".join(shows),
                     "about": x.get("About Summary", ""), "priority": int(r["Priority"] or 9), **f})
    rows.sort(key=lambda r: (not r["has_email"], r["id"], r["priority"]))
    existing = glob.glob(os.path.join(WORK, "ce_in_*.jsonl"))
    k = max([int(os.path.basename(f)[6:8]) for f in existing] or [-1]) + 1
    made, s = [], 0
    while s < len(rows):
        e = min(s + n, len(rows))
        while e < len(rows) and rows[e]["id"] == rows[e - 1]["id"]:
            e += 1  # keep a company's people in one chunk so their emails differ
        with open(os.path.join(WORK, f"ce_in_{k:02d}.jsonl"), "w") as fh:
            for r in rows[s:e]:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k, s = k + 1, e
    print(f"exported {len(rows)} people into chunks {' '.join(made)}")


def problems(r, src):
    out = []
    body, subj = r.get("body", ""), r.get("subject", "")
    lines = [l for l in body.strip().split("\n") if l.strip()]
    if not lines or lines[0].strip() != f'Hi {src["first_name"]},':
        out.append("greeting must be 'Hi {first_name},'")
    if not lines or lines[-1].strip() != "Yoni":
        out.append("must end with 'Yoni' alone")
    core = " ".join(lines[1:-1]).replace(CAL, "")
    w = len(core.split())
    if not 40 <= w <= 75:
        out.append(f"body is {w} words (40 to 70)")
    for pat in BANNED:
        if re.search(pat, body + "\n" + subj, re.I | re.M):
            out.append(f"banned pattern {pat}")
    if core.count("?") != 1:
        out.append("exactly one question (the ask)")
    if len(subj) > 60 or not subj.strip():
        out.append("subject missing or over 60 characters")
    if src.get("monthly_revenue") == "" and re.search(r"\$\d", core):
        out.append("revenue cited but none provided")
    return out


def load(pattern):
    out = {}
    for f in sorted(glob.glob(os.path.join(WORK, pattern))):
        for l in open(f):
            l = l.strip()
            if l:
                try:
                    r = json.loads(l)
                    out[r["key"]] = r  # a later line for the same key replaces the earlier one
                except (json.JSONDecodeError, KeyError):
                    pass
    return out


def check(quiet=False):
    src, got = load("ce_in_*.jsonl"), load("ce_out_*.jsonl")
    bad = {k: problems(r, src[k]) for k, r in got.items() if k in src}
    bad = {k: v for k, v in bad.items() if v}
    if not quiet:
        for k, v in bad.items():
            print(k, "|", "; ".join(v))
        print(f"{len(got)} written, {len(bad)} failing, {len(set(src) - set(got))} not written yet")
    return src, got, bad


def collect():
    src, got, bad = check(quiet=True)
    rows = [{"Key": k, "Exhibitor ID": src[k]["id"], "Email Subject": r["subject"].strip(),
             "Email Body": r["body"].strip(), "Email Angle": r.get("angle", "")}
            for k, r in got.items() if k in src and k not in bad]
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"{len(rows)} emails collected, {len(bad)} still failing")


def status():
    for f in sorted(glob.glob(os.path.join(WORK, "ce_in_*.jsonl"))):
        k = os.path.basename(f)[6:8]
        o = os.path.join(WORK, f"ce_out_{k}.jsonl")
        print(k, sum(1 for _ in open(f)), "out", sum(1 for _ in open(o)) if os.path.exists(o) else 0,
              "DONE" if os.path.exists(os.path.join(WORK, f"ce_done_{k}.txt")) else "")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(int(sys.argv[2]))
    elif cmd == "check":
        check()
    elif cmd == "collect":
        collect()
    else:
        status()

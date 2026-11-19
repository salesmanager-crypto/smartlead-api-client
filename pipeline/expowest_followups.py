"""Yoni's Expo West copy (initial email + follow-up 1 + follow-up 2, one set per brand) -> one row per contact,
formatted for Smartlead and checked.

  python3 pipeline/expowest_followups.py <workbook.xlsx> <contacts.json>

workbook.xlsx: the Final Campaign workbook, one row per brand. Columns used: "New New Email" (initial),
"Follow-Up Number 2 - After three days" (follow-up 1) and "Follow-Up Number 3" (follow-up 2), plus its SmartScout
columns, which the figure check reads.
contacts.json: [[Exhibitor, Brand, First Name, Last Name, Email], ...] in sheet order (the Master Sheet's A:E).

The copy is Yoni's and is used as written. Only these things change, so Smartlead reads it correctly:
  - the greeting names the contact ("Hi <their name>,"), or the brand team where Yoni wrote a team greeting
  - line breaks become <br> (Smartlead sends HTML, where a plain line break collapses)
  - "Schedule a Call" becomes a link to Yoni's calendar

Outputs (pipeline/work/followups/): contacts_rendered.csv, sheet_import.csv (Custom Email, Follow-up 1, Follow-up 2,
Check), smartlead_leads.csv, issues.csv
"""
import csv, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl
from common import ROOT
from expowest_presend import greet_name, email_brand

OUT = os.path.join(ROOT, "pipeline", "work", "followups")
INITIAL, FU1, FU2 = "New New Email", "Follow-Up Number 2 - After three days", "Follow-Up Number 3"
CAL = "https://calendly.com/yonilebovits/30min?back=1&amp;month=2026-11"
LINK = f'<a href="{CAL}">Schedule a Call</a>'
SIGN_INITIAL = "Best,\nYoni\nAlbert Scott\nFull Service Amazon Agency"
SIGN_FU = "Best,\nYoni\nAlbert Scott"
LEGAL = re.compile(r"[,.]?\s+(?:LLC|L\.L\.C\.?|Inc\.?|Ltd\.?|Corp\.?|Corporation|Co\.)$", re.I)
# claims written into every follow-up 1, the same for all brands (Yoni's own, not from our data)
FIXED_USD = (30e6, 10e6)
PLACEHOLDER = re.compile(r"\{\{|\}\}|\{|\}|\[|\]|<|>|\bTBD\b|\bXX+\b|\bnull\b|\bnan\b|\bNone\b|undefined|RESEARCH NEEDED|lorem", re.I)
DECLINE = re.compile(r"\b(declin\w*|fell|fall(?:ing|en)?|drop(?:ped|ping)?|shrank|shrink\w*|down about|down \d)", re.I)
YOY_SENT = re.compile(r"[^.]*(?:[Yy]ear over year)[^.]*\.")
YOY = re.compile(r"([^.]*?(?:[Yy]ear over year|last 12 months|previous 12|prior 12|12 months compared)[^.]*\.(?:\d+)?[^.]*)")


def html(text):
    return text.replace("\n\n", "<br><br>").replace("\n", "<br>")


def num(v):
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None


def usd(s):
    m = re.fullmatch(r"\$?\s*([\d,]+(?:\.\d+)?)\s*(million|billion|thousand|[MBKmbk])?", s.strip())
    if not m:
        return None
    x = float(m.group(1).replace(",", ""))
    u = (m.group(2) or "").lower()
    return x * {"": 1, "k": 1e3, "thousand": 1e3, "m": 1e6, "million": 1e6, "b": 1e9, "billion": 1e9}[u]


def evidence(b):
    """The brand's own figures from the workbook's SmartScout columns: ({percent values}, {dollar values})."""
    pct, dol = set(), set()
    for k in ("Monthly Revenue", "12-Month Revenue"):
        if num(b.get(k)) is not None:
            dol.add(num(b[k]))
    for k in ("Amazon Revenue Share %", "Brand Own Account Share %", "MoM Growth %", "12-Mo Avg MoM Growth %"):
        if num(b.get(k)) is not None:
            pct.add(round(num(b[k]) * 100, 2))
    shares = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)%", b.get("Top Sellers (share of brand revenue)") or "")]
    pct.update(shares)
    pct.update(round(100 - x, 1) for x in shares)
    if shares:
        pct.add(round(sum(shares), 1))
        pct.add(round(100 - sum(shares), 1))
    market, subs = [], len(re.findall(r"% share", b.get("Top Subcategories (brand revenue, market share)") or ""))
    for name, rev, share in re.findall(r"([^;:]+): about (\$[\d.,]+[KMB]?), ([\d.]+)% share", b.get("Top Subcategories (brand revenue, market share)") or ""):
        r, s = usd(rev), float(share)
        dol.add(r)
        pct.add(s)
        if r and s:
            market.append(r / (s / 100))
            dol.add(r / (s / 100))
    return pct, dol, (market, subs)


def figures(text):
    pcts = [(float(m.group(1)), m.group(0)) for m in re.finditer(r"(\d+(?:\.\d+)?)%", text)]
    # $120 million+, $2.8M, $2,750,000, $36 million; not "$30K" style twice
    dols = [(usd(m.group(1)), m.group(0)) for m in re.finditer(r"(\$\s?[\d,]+(?:\.\d+)?\s*(?:million|billion|thousand|[MBK]\b)?)", text)]
    return pcts, [(v, s) for v, s in dols if v is not None]


def check(kind, text, b):
    """Problems with one rendered email (text, plain). Returns list of (severity, message)."""
    out = []
    plain = text
    if PLACEHOLDER.search(plain):
        out.append(("REVIEW", f"placeholder-like text '{PLACEHOLDER.search(plain).group(0)}'"))
    if re.search(r"[—–]", plain):
        out.append(("REVIEW", "dash in copy"))
    if "\r" in plain or "\n\n\n" in plain or re.search(r"[ \t]\n", plain) or "  " in plain:
        out.append(("WARN", "odd spacing in copy"))
    sign = SIGN_INITIAL if kind == "initial" else SIGN_FU
    if not plain.rstrip().endswith(sign):
        out.append(("REVIEW", "signature is not Yoni's block"))
    if not re.match(r"Hi [^,\n]+,\n\n", plain):
        out.append(("REVIEW", "greeting missing"))
    if kind != "initial" and plain.count("Schedule a Call") != 1:
        out.append(("REVIEW", "Schedule a Call link missing or repeated"))
    pct, dol, (market, subs) = evidence(b)
    pcts, dols = figures(plain)
    for v, s in pcts:
        ctx = plain[max(0, plain.find(s) - 80):plain.find(s)]
        if re.search(r"year over year|last 12|previous 12|prior 12", ctx + plain[plain.find(s):plain.find(s) + 40], re.I) and kind == "initial":
            out.append(("REVIEW", "states a year-over-year % we cannot trace to our data"))
            continue
        if any(abs(v - p) <= max(0.6, 0.08 * p) for p in pct) or (v <= 0.15 and any(p <= 0.15 for p in pct)):
            continue
        out.append(("REVIEW", f"figure {s} not in our data"))
    for v, s in dols:
        if kind == "fu1" and any(abs(v - f) < 1 for f in FIXED_USD):
            continue
        if kind == "fu2" and re.search(re.escape(s) + r"\+", plain):
            total = sum(market)  # "$120 million+": the top subcategories' monthly sales, brand revenue / its market share
            if market and len(market) == subs and 0.5 * total <= v <= 1.12 * total:
                continue
            if len(market) < max(subs, 1) and v >= 0.8 * total:  # a share that rounds to 0.0% cannot be turned back into a market size
                out.append(("WARN", f"{s} not fully traceable (a subcategory share rounds to 0.0%)"))
                continue
        if any(abs(v - d) <= max(0.16 * d, 600) for d in dol):
            continue
        sentence = next((x for x in re.split(r"(?<=[.?!])\s", plain) if s in x), "")
        if v >= 1e6 and re.search(r"subcategor|categor|across all brands|shoppers spend", sentence):
            out.append(("WARN", f"market-size figure {s} not traceable to this workbook's columns (subcategory total)"))
        else:
            out.append(("REVIEW", f"figure {s} not in our data"))
    if kind == "initial" and DECLINE.search(YOY_SENT.sub("", plain)) and not any("year-over-year" in m for _, m in out):
        out.append(("REVIEW", "says sales fell or declined"))
    return list(dict.fromkeys(out))


def main(path, contacts_path):
    os.makedirs(OUT, exist_ok=True)
    rows = list(openpyxl.load_workbook(path).worksheets[0].iter_rows(values_only=True))
    H = list(rows[0])
    brands = {}
    for r in rows[1:]:
        d = dict(zip(H, r))
        t = (d[INITIAL] or "").strip()
        if t.startswith("Hi "):
            brands[(d["Exhibitor"], d["Brand"])] = d
    contacts = json.load(open(contacts_path, encoding="utf-8"))
    out, issues, summary = [], [], {"PASS": 0, "WARN": 0, "REVIEW": 0}
    for i, c in enumerate(contacts):
        exh, brand, first, last, email = (c + [""] * 5)[:5]
        b = brands.get((exh, brand))
        if not b:
            issues.append((email, "no email copy for this brand in the workbook"))
            continue
        # the workbook's greeted name for its first contact; a team greeting applies to that contact only
        gname = re.match(r"Hi ([^,\n]+),", b[INITIAL]).group(1)
        g, _ = greet_name(first, last, email)
        if gname.endswith(" team") and first == b["First Name"]:
            g = gname
        if not g:
            g = "there"
        texts, res = {}, []
        for kind, col in (("initial", INITIAL), ("fu1", FU1), ("fu2", FU2)):
            t = b[col].strip()
            m = re.match(r"Hi ([^,\n]+),\n\n", t)
            if not m:
                res.append(("REVIEW", f"{kind}: greeting missing"))
                texts[kind] = t
                continue
            t = f"Hi {g},\n\n" + t[m.end():]
            if LEGAL.search(b["Exhibitor"]) and b["Exhibitor"] in t:
                t = t.replace(b["Exhibitor"], LEGAL.sub("", b["Exhibitor"]))
            texts[kind] = t
            res += [(s, f"{kind}: {msg}") for s, msg in check(kind, t, b)]
        # the brand named in the three emails must be the same
        names = [email_brand(texts[k].split("\n\n", 1)[1].replace("Albert Scott", "AS"), [b["Brand"], b["Exhibitor"], b.get("Amazon Store Name"), b.get("SmartScout Brand"),
                                                            *re.split(r"[;/]", b.get("Also Listed As") or "")]) for k in texts]
        if not names[0]:
            res.append(("WARN", "brand name as written not found in the initial email"))
        elif len({n.lower() for n in names if n}) > 1:
            res.append(("WARN", "brand named differently across the three emails (Yoni's wording)"))
        rank = {"REVIEW": 2, "WARN": 1}
        worst = max((rank[s] for s, _ in res), default=0)
        label = ["PASS", "WARN", "REVIEW"][worst]
        reasons = list(dict.fromkeys(m for s, m in res if rank[s] == worst))
        chk = label if not reasons else f"{label}: " + "; ".join(reasons[:3])
        summary[label] += 1
        pf = lambda k: texts[k].replace("Schedule a Call", "@@LINK@@")
        initial = html(texts["initial"])
        fu1 = html(pf("fu1")).replace("@@LINK@@", LINK)
        fu2 = html(pf("fu2")).replace("@@LINK@@", LINK)
        out.append({"Exhibitor ID": b["Exhibitor ID"], "Exhibitor": exh, "Brand": brand, "Email": email,
                    "First Name": first, "Last Name": last, "Greeting": g, "Company": names[0] or brand,
                    "Custom Email": initial, "Follow-up 1": fu1, "Follow-up 2": fu2, "Check": chk, "Row": i + 3})
    with open(os.path.join(OUT, "contacts_rendered.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    with open(os.path.join(OUT, "sheet_import.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Custom Email", "Follow-up 1", "Follow-up 2", "Custom Email Check"])
        for o in out:
            w.writerow([o["Custom Email"], o["Follow-up 1"], o["Follow-up 2"], o["Check"]])
    with open(os.path.join(OUT, "smartlead_leads.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["email", "first_name", "last_name", "company_name", "custom_email", "custom_followup_1", "custom_followup_2",
                    "exhibitor_id", "check"])
        for o in out:
            w.writerow([o["Email"], "" if o["Greeting"].endswith(" team") else o["Greeting"], o["Last Name"], o["Company"], o["Custom Email"], o["Follow-up 1"], o["Follow-up 2"],
                        o["Exhibitor ID"], o["Check"]])
    with open(os.path.join(OUT, "issues.csv"), "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows([("Email", "Issue")] + issues)
    print(f"{len(out)} contacts rendered, {len(issues)} without copy; checks {summary}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

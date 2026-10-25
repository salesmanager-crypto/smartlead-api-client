"""Check every Expo West email against the brand data it was written from.

  python3 pipeline/expowest_email_audit.py        -> pipeline/work/email_audit.jsonl (one line per problem) and a summary

For each brand, the record is the last lg_in_NN.jsonl line for its id (the data the writer saw) and the email is the
final version in expowest_emails.csv. Checks:
- every dollar figure ($45K, $1.3M) is within rounding of a revenue in the record (monthly, 12-month, subcategory,
  average price);
- every percentage is within rounding of a share, growth or 100-minus-share in the record, or a sum of seller shares;
- other numbers (ratings, review and product counts) are near a value in the record;
- the email names the brand (exhibitor, Amazon store, SmartScout brand or also-listed name).
A flagged email is not necessarily wrong ("roughly two thirds" style rounding passes; an unusual derived figure may not),
so each flag is for a person to read.
"""
import csv, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

WORK = os.path.join(ROOT, "pipeline", "work")
EMAILS = os.path.join(ROOT, "expowest_emails.csv")
OUT = os.path.join(WORK, "email_audit.jsonl")
UNIT = {"k": 1e3, "m": 1e6, "b": 1e9}
YEARS = {2024, 2025, 2026, 2027}


def records():
    out = {}
    for f in sorted(glob.glob(os.path.join(WORK, "lg_in_*.jsonl")), key=lambda f: int(re.search(r"_(\d+)\.", f).group(1))):
        for l in open(f, encoding="utf-8"):
            r = json.loads(l)
            out[r["id"]] = r
    return out


def money(text):
    """'about $1.3M' -> 1300000.0 for every dollar figure in the text."""
    return [float(n.replace(",", "")) * UNIT.get(u.lower(), 1)
            for n, u in re.findall(r"\$\s?(\d[\d,]*(?:\.\d+)?)\s?([KkMmBb])?\b", text or "")]


def num(v):
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None


def pools(r):
    usd = money(r.get("monthly_revenue")) + money(r.get("trailing_12_month_revenue"))
    sub = [x for s in r.get("top_subcategories") or [] for x in money(s.get("brand_revenue"))]
    usd += sub + [a + b for i, a in enumerate(sub) for b in sub[i + 1:]] + ([sum(sub)] if sub else [])
    if num(r.get("average_price")):
        usd.append(num(r["average_price"]))
    shares = [s.get("share_pct") for s in r.get("top_sellers") or [] if s.get("share_pct") is not None]
    pct = shares + [r.get(k) for k in ("brand_own_share_pct", "amazon_1p_share_pct", "mom_growth_pct",
                                       "avg_monthly_growth_12mo_pct") if r.get(k) is not None]
    pct += [s.get("market_share_pct") for s in r.get("top_subcategories") or [] if s.get("market_share_pct") is not None]
    pct += [100 - x for x in list(pct)] + [sum(shares[:i]) for i in range(2, len(shares) + 1)]
    pct += [abs(x) for x in pct]
    other = [num(r.get(k)) for k in ("average_rating", "total_reviews", "total_products", "monthly_units",
                                     "average_sellers_per_listing")] + [len(r.get("top_sellers") or [])]
    return usd, pct, [x for x in other if x is not None]


def near(x, vals, rel, absolute):
    return any(abs(x - v) <= max(absolute, rel * abs(v)) for v in vals)


def key(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def names_ok(body, r):
    b = key(body)
    for n in (r.get("exhibitor"), r.get("amazon_store_name"), r.get("smartscout_brand"), r.get("also_listed_as")):
        for part in re.split(r"[,/;|]| and ", n or ""):
            words = [w for w in re.split(r"\s+", part.strip()) if w]
            for k in range(len(words), 0, -1):  # longest leading run of the name that appears
                cand = key(" ".join(words[:k]))
                if cand and (len(cand) >= 4 or len(words) == k == len(re.split(r"\s+", n.strip()))) and cand in b:
                    return True
    return False


def audit():
    recs = records()
    rows = list(csv.DictReader(open(EMAILS, encoding="utf-8")))
    probs = []
    for e in rows:
        r, body = recs.get(e["Exhibitor ID"]), e["Email Body"]
        if not r:
            probs.append({"id": e["Exhibitor ID"], "kind": "no data record"})
            continue
        usd, pct, other = pools(r)
        text = body.replace("{{first_name}}", "")
        for x in money(text):
            if not near(x, usd, 0.2, 0):
                probs.append({"id": r["id"], "brand": e["Brand"], "kind": "dollar figure not in data", "value": x})
        for p in re.findall(r"(\d+(?:\.\d+)?)\s?%", text):
            if not near(float(p), pct, 0.15, 1.0):
                probs.append({"id": r["id"], "brand": e["Brand"], "kind": "percent not in data", "value": float(p)})
        bare = re.sub(r"\$\s?\d[\d,.]*\s?[KkMmBb]?|\d+(?:\.\d+)?\s?%", " ", text)
        for n in (r.get("exhibitor"), r.get("amazon_store_name"), r.get("smartscout_brand"), e["Brand"]):
            for d in re.findall(r"\d+", n or ""):  # numbers that are part of the brand's name (88 Acres)
                bare = re.sub(rf"(?<!\d){d}(?!\d)", " ", bare)
        for p in re.findall(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)(?![\w%])", bare):
            x = num(p)
            if x is None or x in YEARS or x in (1, 2, 3, 4, 5, 10, 12, 15, 20, 30, 90):  # years, counts, "20 minutes"
                continue
            if not near(x, other, 0.25, 0.3):
                probs.append({"id": r["id"], "brand": e["Brand"], "kind": "number not in data", "value": x})
        if not names_ok(body, r):
            probs.append({"id": r["id"], "brand": e["Brand"], "kind": "brand name not found in email"})
    with open(OUT, "w", encoding="utf-8") as fh:
        for p in probs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    from collections import Counter
    print(f"{len(rows)} emails audited; {len({p['id'] for p in probs})} with something to check -> {OUT}")
    print(dict(Counter(p["kind"] for p in probs)))


if __name__ == "__main__":
    audit()

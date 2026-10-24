"""First-touch lead-gen emails for the Expo West Amazon brands: one email per brand, in Yoni's voice
(my-writing-style skill, Outbound lead-gen mode). Every contact at a brand gets the same email; only
{{first_name}} changes.

  python3 pipeline/expowest_emails.py export N [IDS]   brands with decision makers and no email yet, priority order,
                                                         chunks of N -> pipeline/work/lg_in_NN.jsonl (IDS: optional
                                                         comma list to export only those brands)
  python3 pipeline/expowest_emails.py check            validate lg_out_NN.jsonl against the lead-gen rules
  python3 pipeline/expowest_emails.py collect          passing emails -> expowest_emails.csv
  python3 pipeline/expowest_emails.py status

The facts come from the pipeline files only: SmartScout profile (smartscout_brands.csv), sellers and top
subcategories (ssd_sellers / ssd_subcats), parent company research and the show data. Figures are rounded here so
the writer never sees an exact number.
"""
import csv, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT
from expowest_smartscout import detail_rows, key

WORK = os.path.join(ROOT, "pipeline", "work")
MASTER = os.path.join(ROOT, "expowest_amazon_master.csv")
SS = os.path.join(ROOT, "smartscout_brands.csv")
OUT = os.path.join(ROOT, "expowest_emails.csv")
BANNED = [r"—", r"–", r"!", r"\bI'?d love\b", r"\bwould love\b", r"hope this (email )?finds", r"\bleverag",
          r"\bsynerg", r"game.?changer", r"\bunlock", r"strategic opportunit", r"smartscout", r"amazon management agency",
          r"\bwe would\b", r"drive meaningful", r"[\U0001F300-\U0001FAFF☀-➿]", r"^\s*[-*•]", r"\bbump",
          r"touch base", r"circle back", r"\bquick question\b", r"\{\{calendar_link\}\}"]


def money(x):
    """Rounded revenue phrase: about $45K, about $350K, about $1.3M."""
    try:
        x = float(x)
    except (TypeError, ValueError):
        return ""
    if x < 1000:
        return ""
    if x < 100000:
        return f"about ${int(round(x / 1000.0))}K"
    if x < 1000000:
        return f"about ${int(round(x / 10000.0) * 10)}K"
    return f"about ${round(x / 1e6, 1):g}M"


def pct(x, frac=False):
    try:
        v = float(x) * (100 if frac else 1)
    except (TypeError, ValueError):
        return None
    return round(v, 1)


def sim(a, b):
    """Seller name looks like the brand: one name starts with the other, a long name (5+) is contained in the
    other, or they share a 5-character prefix. A bare substring match on a short name (EO in "Jude Our...")
    does not count."""
    a, b = key(a), key(b)
    if not a or not b:
        return False
    short, long_ = sorted((a, b), key=len)
    return (long_.startswith(short) or (len(short) >= 5 and short in long_)
            or len(os.path.commonprefix([a, b])) >= 5)


def seller_type(name, names):
    n = name.lower()
    if n == "amazon.com":
        return "Amazon 1P"
    if n == "whole foods market":
        return "Whole Foods Market (Amazon-owned)"
    if any(sim(name, x) for x in names if x):
        return "likely the brand's own or affiliated account"
    return "another seller (not confirmed as reseller or brand)"


def brand_rows():
    """One record per brand that has decision makers, in campaign priority order."""
    ss = {r["Exhibitor ID"]: r for r in csv.DictReader(open(SS, encoding="utf-8"))}
    sellers, subcats = detail_rows("sellers"), detail_rows("subcats")
    seen, out = {}, []
    for r in csv.DictReader(open(MASTER, encoding="utf-8")):
        eid = r["Exhibitor ID"]
        if not r["First Name"]:
            continue
        if eid in seen:
            seen[eid]["contacts"] += 1
            continue
        s = ss.get(eid, {})
        names = [r["Exhibitor"], r["Also Listed As"], s.get("SmartScout Brand", ""), r["Amazon Store Name"],
                 r["Parent Company"]]
        k = key(s.get("SmartScout Brand", ""))
        sl = sorted(sellers.get(k, []), key=lambda x: int(x.get("Rn") or 99))[:5]
        sc = sorted(subcats.get(k, []), key=lambda x: int(x.get("Rn") or 99))[:3]
        sl = [{"seller": x["Seller Name"], "share_pct": pct(x.get("Estimated Brand Share")),
               "type": seller_type(x["Seller Name"], names)} for x in sl]
        own = round(sum(x["share_pct"] or 0 for x in sl if x["type"].startswith("likely the brand")), 1)
        amz = round(sum(x["share_pct"] or 0 for x in sl if x["type"].startswith(("Amazon 1P", "Whole Foods"))), 1)
        rev = s.get("Monthly Revenue", "")
        booth = re.search(r"2027: ([^;]+)", r["Booths"])
        rec = {
            "id": eid, "tier": r["Priority Tier"], "exhibitor": r["Exhibitor"], "also_listed_as": r["Also Listed As"],
            "amazon_store_name": r["Amazon Store Name"], "smartscout_brand": s.get("SmartScout Brand", ""),
            "smartscout_match": s.get("SmartScout Match", ""), "parent_company": r["Parent Company"],
            "exhibiting_expo_west_2027": r["In 2027 List"] == "Yes" and bool(booth),
            "expo_west_years": r["Years Exhibited"], "old_database_only": eid.startswith("O"),
            "monthly_revenue": money(rev), "trailing_12_month_revenue": money(s.get("TTM Revenue", "")),
            "monthly_units": s.get("Monthly Units", ""), "primary_subcategory": s.get("Primary Subcategory", ""),
            "total_products": s.get("Total Products", ""), "total_reviews": s.get("Total Reviews", ""),
            "average_rating": s.get("Average Rating", ""), "average_price": s.get("Average Price", ""),
            "average_sellers_per_listing": s.get("Average Sellers", ""),
            "mom_growth_pct": pct(s.get("MoM Growth"), True),
            "avg_monthly_growth_12mo_pct": pct(s.get("12-Month MoM Growth"), True),
            "top_sellers": sl, "brand_own_share_pct": own if sl else None,
            "amazon_1p_share_pct": amz if sl else None,
            "top_subcategories": [{"subcategory": x["Subcategory Context Name"],
                                   "brand_revenue": money(x.get("Monthly Revenue")),
                                   "market_share_pct": pct(x.get("Market Share"), True)} for x in sc],
            "data_flags": [], "contacts": 1}
        if not rev:
            rec["data_flags"].append("no SmartScout numbers: " + (s.get("SmartScout Match") or "not pulled"))
        elif float(rev) < 5000:
            rec["data_flags"].append("very small measurable Amazon revenue")
        if s.get("SmartScout Match", "").startswith("same name"):
            rec["data_flags"].append("SmartScout name differs from the store name only in case or spacing")
        if rev and not sl:
            rec["data_flags"].append("no seller breakdown returned")
        seen[eid] = rec
        out.append(rec)
    return out


def queued():
    return {json.loads(l)["id"] for f in glob.glob(os.path.join(WORK, "lg_in_*.jsonl")) for l in open(f, encoding="utf-8")}


def detail_ready():
    """SmartScout brand keys whose sellers / subcategory chunk has finished."""
    ok = set()
    for f in glob.glob(os.path.join(WORK, "ssd_in_*.jsonl")):
        if os.path.exists(f.replace("ssd_in_", "ssd_done_").replace(".jsonl", ".txt")):
            ok |= {key(json.loads(l)["brand"]) for l in open(f, encoding="utf-8")}
    return ok


def export(n, ids=None):
    q, ready = queued(), detail_ready()
    todo = [r for r in brand_rows() if r["id"] not in q and (not ids or r["id"] in ids)
            and (not r["monthly_revenue"] or key(r["smartscout_brand"]) in ready)]
    nums = [int(re.search(r"_(\d+)\.jsonl$", f).group(1)) for f in glob.glob(os.path.join(WORK, "lg_in_*.jsonl"))]
    k, made = max(nums, default=0) + 1, []
    for s in range(0, len(todo), n):
        with open(os.path.join(WORK, f"lg_in_{k:02d}.jsonl"), "w", encoding="utf-8") as fh:
            for r in todo[s:s + n]:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k += 1
    print(f"exported {len(todo)} brands into chunks {' '.join(made) or '(none)'}")


def load(pattern):
    out = {}
    for f in sorted(glob.glob(os.path.join(WORK, pattern))):
        for l in open(f, encoding="utf-8"):
            try:
                r = json.loads(l)
                out[r["id"]] = r  # a later line for the same brand replaces the earlier one
            except (json.JSONDecodeError, KeyError):
                pass
    return out


def problems(r, src):
    out, body = [], r.get("body", "").strip()
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    if not lines or lines[0] != "Hi {{first_name}},":
        out.append("first line must be 'Hi {{first_name}},'")
    if len(lines) < 2 or lines[-2:] != ["Best,", "Yoni"]:
        out.append("must end with 'Best,' then 'Yoni'")
    w = len(body.split())
    if not 80 <= w <= 125:
        out.append(f"{w} words (85 to 120 including greeting and sign-off)")
    for pat in BANNED:
        if re.search(pat, body, re.I | re.M):
            out.append(f"banned pattern {pat}")
    if body.count("?") != 1:
        out.append("exactly one question mark (the ask)")
    if "Albert Scott" not in body:
        out.append("must name Albert Scott")
    if not src.get("monthly_revenue") and re.search(r"\$\d", body):
        out.append("cites revenue but none was provided")
    if re.search(r"expo west", body, re.I) and not src.get("exhibiting_expo_west_2027"):
        out.append("mentions Expo West but the brand is not on the 2027 exhibitor list")
    if re.search(r"\b(see you|meet you|I'll be|I will be|we'll be) (at|in)\b", body, re.I):
        out.append("implies Yoni will be at the show")
    if not r.get("angle", "").strip():
        out.append("angle missing")
    return out


def check(quiet=False):
    src, got = load("lg_in_*.jsonl"), load("lg_out_*.jsonl")
    bad = {k: problems(r, src[k]) for k, r in got.items() if k in src}
    bad = {k: v for k, v in bad.items() if v}
    if not quiet:
        for k, v in bad.items():
            print(k, "|", "; ".join(v))
        print(f"{len(got)} written, {len(bad)} failing, {len(set(src) - set(got))} not written yet")
    return src, got, bad


def collect():
    src, got, bad = check(quiet=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["Exhibitor ID", "Brand", "Email Body", "Angle", "QA Flags"])
        w.writeheader()
        for k, r in got.items():
            if k in src and k not in bad:
                w.writerow({"Exhibitor ID": k, "Brand": src[k]["smartscout_brand"] or src[k]["exhibitor"],
                            "Email Body": r["body"].strip(), "Angle": r.get("angle", "").strip(),
                            "QA Flags": r.get("qa_flags", "").strip()})
    print(f"{len(got) - len(bad)} emails -> {OUT}; {len(bad)} still failing")


def status():
    for f in sorted(glob.glob(os.path.join(WORK, "lg_in_*.jsonl"))):
        k = re.search(r"_(\d+)\.jsonl$", f).group(1)
        o = os.path.join(WORK, f"lg_out_{k}.jsonl")
        print(k, sum(1 for _ in open(f)), "out", sum(1 for _ in open(o)) if os.path.exists(o) else 0,
              "DONE" if os.path.exists(os.path.join(WORK, f"lg_done_{k}.txt")) else "")


if __name__ == "__main__":
    a = sys.argv[1:] or [""]
    if a[0] == "export":
        export(int(a[1]), set(a[2].split(",")) if len(a) > 2 else None)
    else:
        {"check": check, "collect": collect, "status": status}.get(a[0], lambda: print(__doc__))()

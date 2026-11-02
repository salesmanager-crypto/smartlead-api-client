"""First-touch lead-gen emails for the Expo West Amazon brands: one email per brand, in Yoni's voice
(my-writing-style skill, Outbound lead-gen mode). Every contact at a brand gets the same email; only
{{first_name}} changes.

  python3 pipeline/expowest_emails.py export N [IDS]   brands with decision makers and no email yet, priority order,
                                                         chunks of N -> pipeline/work/lg_in_NN.jsonl (IDS: optional
                                                         comma list to export only those brands)
  python3 pipeline/expowest_emails.py redo N IDS       re-export brands already written, once new data arrived
  python3 pipeline/expowest_emails.py check            validate lg_out_NN.jsonl against the lead-gen rules
  python3 pipeline/expowest_emails.py collect          passing emails -> expowest_emails.csv
  python3 pipeline/expowest_emails.py status

Second version (November 2026 rewrite to Yoni's revised lead-gen standard, three short paragraphs, "an Amazon
management agency", support the business as it runs, no control / decline / rank / thin-business claims):
  python3 pipeline/expowest_emails.py v2-export N       every brand with an email, fresh data -> lg2_in_NN.jsonl
  python3 pipeline/expowest_emails.py v2-check          validate lg2_out_NN.jsonl
  python3 pipeline/expowest_emails.py v2-collect        passing emails -> expowest_emails.csv (old copy kept as
                                                         expowest_emails_v1.csv)
  python3 pipeline/expowest_emails.py v2-status

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
          r"touch base", r"circle back", r"\bfollow(ing)?[ -]up\b", r"\breconnect", r"\bas promised\b", r"\bgreat (meeting|connecting)\b", r"\bquick question\b", r"\{\{calendar_link\}\}"]


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
    """Seller name looks like the brand: the brand is one of the seller's words ("Drink Juni", "Authorized Goya
    Seller"), one name starts with the other, a long name (5+) is contained in the other, or they share a
    5-character prefix. A bare substring match on a short name (EO in "Jude Our...") does not count."""
    words = {key(w) for w in re.split(r"[\s&/,.-]+", str(a) + " " + str(b)) if key(w)}
    ka, kb = key(a), key(b)
    if not ka or not kb:
        return False
    short, long_ = sorted((ka, kb), key=len)
    wa = {key(w) for w in re.split(r"[\s&/,.-]+", str(a)) if key(w)}
    wb = {key(w) for w in re.split(r"[\s&/,.-]+", str(b)) if key(w)}
    return (ka in wb or kb in wa or long_.startswith(short) or (len(short) >= 5 and short in long_)
            or len(os.path.commonprefix([ka, kb])) >= 5)


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
        num = lambda v: float(v) if v not in (None, "") else 0.0
        rank = lambda x: int(x.get("Rn") or x.get("Rnk") or 99)  # rebuilt queries name it Rnk, or leave it out

        def top(rows, name, value, n):
            """Largest first by the value itself (rebuilt queries return every row, ranks out of order), one row per
            seller or subcategory, skipping rows in another query's field names."""
            seen, out = set(), []
            for x in sorted((x for x in rows if x.get(name)), key=lambda x: (-num(x.get(value)), rank(x))):
                if x[name] not in seen:
                    seen.add(x[name])
                    out.append(x)
            return out[:n]
        sl = top(sellers.get(k, []), "Seller Name", "Estimated Brand Share", 5)
        sc = top(subcats.get(k, []), "Subcategory Context Name", "Monthly Revenue", 3)
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


def export(n, ids=None, redo=False):
    """redo=True re-exports the given ids even if they were written before (for example once seller data arrived)."""
    q, ready = (set() if redo else queued()), detail_ready()
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


V2_OPEN = "I'm Yoni with Albert Scott, an Amazon management agency."
V2_ASKS = ("Would you be open to a short call to discuss this?", "Would you be open to a short call to discuss your plans?")
V2_BANNED = [b for b in BANNED if b != r"amazon management agency"] + [
    r"full-service", r"\bcontrol", r"\bno say\b", r"gap is in execution", r"\bdeclin", r"\beas(ed|ing)\b", r"\bslipp?(ed|ing)\b",
    r"\bdown from\b", r"\bfell\b", r"\bdropped\b", r"\bsoften", r"\btiny\b", r"\blimited\b", r"undeveloped",
    r"little activity", r"no (amazon )?presence", r"\bsmall\b", r"exhibitor list", r"run rate", r"case stud",
    r"leading position", r"\bleader\b", r"\bleads (the|its)\b", r"\branked\b", r"\branks?\b", r"#\s?\d", r"number one",
    r"\breseller", r"seasonality|seasonal (dip|drop|slow|low|lull)|because of (the )?season", r"over the (past|last) (year|month)", r"month over month", r"year over year",
    r"\{\{(?!first_name\}\})[^}]*\}\}", r"\bsmallest\b", r"\bweak", r"\bpoor", r"\bmismanag", r"nobody|no one (manages|owns)"]


def problems2(r, src):
    out, body = [], r.get("body", "").strip()
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    if not paras or paras[0] != "Hi {{first_name}},":
        out.append("first paragraph must be exactly 'Hi {{first_name}},'")
    if paras[-1:] != ["Best,\nYoni"]:
        out.append("must end with 'Best,' then 'Yoni' on the next line")
    if len(paras) > 1 and not paras[1].startswith(V2_OPEN):
        out.append(f"first paragraph must open with \"{V2_OPEN}\"")
    if len(paras) < 3 or paras[-2] not in V2_ASKS:
        out.append("the paragraph before the sign-off must be exactly one of: " + " / ".join(V2_ASKS))
    if not 5 <= len(paras) <= 6:
        out.append(f"{len(paras) - 2} body paragraphs (3 or 4, the ask being the last)")
    w = len(body.split())
    if not 75 <= w <= 110:
        out.append(f"{w} words (80 to 105 including greeting and sign-off)")
    claims = body
    for n in (src.get("exhibitor"), src.get("amazon_store_name"), src.get("smartscout_brand"), src.get("also_listed_as")):
        for part in re.split(r"[;/|]", n or ""):
            if part.strip():
                claims = re.sub(re.escape(part.strip()), " ", claims, flags=re.I)  # brand names can hold banned words
    for pat in V2_BANNED:
        if re.search(pat, claims, re.I | re.M):
            out.append(f"banned pattern {pat}: '{re.search(pat, claims, re.I | re.M).group(0)}'")
    if (src.get("amazon_1p_share_pct") or 0) >= 50 and re.search(r"\b3P\b|hybrid|seller central|own (seller )?account", body, re.I):
        out.append("Amazon retail sells most of it: support the vendor business, do not pitch 3P, hybrid or a seller account")
    if body.count("?") != 1:
        out.append("exactly one question mark (the ask)")
    if not src.get("monthly_revenue") and re.search(r"\$\d|\d\s?%", body):
        out.append("cites figures but the brand has no SmartScout numbers")
    figs = re.findall(r"\$\s?\d[\d,.]*\s?[KMB]?|\d+(?:\.\d+)?\s?%", body)
    if len(figs) > 3:
        out.append(f"{len(figs)} figures; keep to the one or two that carry the point")
    if re.search(r"(?<!\.)\b0(\.0)?\s?%", body):
        out.append("cites a 0% share")
    if re.search(r"expo west", body, re.I) and not src.get("exhibiting_expo_west_2027"):
        out.append("mentions Expo West but the brand is not on the 2027 exhibitor list")
    if src.get("exhibiting_expo_west_2027") and not re.search(r"Natural Products Expo West", body):
        out.append("2027 exhibitor: name Natural Products Expo West in the opening paragraph")
    if re.search(r"\b(see you|meet(ing)? you|met you|I'll be|I will be|we'll be|we will be)\b", body, re.I):
        out.append("implies Yoni will be at the show or has met them")
    if not r.get("angle", "").strip():
        out.append("angle missing")
    return out


def export2(n):
    """Fresh brand records (current data) for every brand that has an email, in chunks of n."""
    ids = {r["Exhibitor ID"] for r in csv.DictReader(open(OUT if os.path.exists(OUT) else OUT, encoding="utf-8"))}
    v1 = OUT.replace(".csv", "_v1.csv")
    if os.path.exists(v1):
        ids |= {r["Exhibitor ID"] for r in csv.DictReader(open(v1, encoding="utf-8"))}
    done = {json.loads(l)["id"] for f in glob.glob(os.path.join(WORK, "lg2_in_*.jsonl")) for l in open(f, encoding="utf-8")}
    todo = [r for r in brand_rows() if r["id"] in ids and r["id"] not in done]
    nums = [int(re.search(r"_(\d+)\.jsonl$", f).group(1)) for f in glob.glob(os.path.join(WORK, "lg2_in_*.jsonl"))]
    k, made = max(nums, default=0) + 1, []
    for s in range(0, len(todo), n):
        with open(os.path.join(WORK, f"lg2_in_{k:02d}.jsonl"), "w", encoding="utf-8") as fh:
            for r in todo[s:s + n]:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k += 1
    print(f"exported {len(todo)} brands into lg2 chunks {' '.join(made) or '(none)'}")


def check2(quiet=False, only=None):
    src, got = load("lg2_in_*.jsonl"), load("lg2_out_*.jsonl")
    if only:
        got = {k: v for k, v in got.items() if k in only}
    bad = {k: problems2(r, src[k]) for k, r in got.items() if k in src}
    bad = {k: v for k, v in bad.items() if v}
    if not quiet:
        for k, v in bad.items():
            print(k, "|", "; ".join(v))
        print(f"{len(got)} written, {len(bad)} failing, {len(set(src) - set(load('lg2_out_*.jsonl')))} not written yet")
    return src, got, bad


def collect2():
    src, got, bad = check2(quiet=True)
    v1 = OUT.replace(".csv", "_v1.csv")
    if not os.path.exists(v1):
        os.replace(OUT, v1)
    missing = set(src) - set(got) - set(bad)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["Exhibitor ID", "Brand", "Email Body", "Angle", "QA Flags"])
        w.writeheader()
        for k, r in got.items():
            if k in src and k not in bad:
                w.writerow({"Exhibitor ID": k, "Brand": src[k]["smartscout_brand"] or src[k]["exhibitor"],
                            "Email Body": r["body"].strip(), "Angle": r.get("angle", "").strip(),
                            "QA Flags": r.get("qa_flags", "").strip()})
    print(f"{len(got) - len(bad)} emails -> {OUT}; {len(bad)} still failing; {len(missing)} not written")


def status2():
    for f in sorted(glob.glob(os.path.join(WORK, "lg2_in_*.jsonl"))):
        k = re.search(r"_(\d+)\.jsonl$", f).group(1)
        o = os.path.join(WORK, f"lg2_out_{k}.jsonl")
        print(k, sum(1 for _ in open(f)), "out", len({json.loads(l)["id"] for l in open(o)}) if os.path.exists(o) else 0,
              "DONE" if os.path.exists(os.path.join(WORK, f"lg2_done_{k}.txt")) else "")


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
    elif a[0] == "redo":
        export(int(a[1]), set(a[2].split(",")), redo=True)
    elif a[0] == "v2-export":
        export2(int(a[1]))
    elif a[0] == "v2-check":
        check2(only=set(a[1].split(",")) if len(a) > 1 else None)
    else:
        {"check": check, "collect": collect, "status": status, "v2-collect": collect2,
         "v2-status": status2}.get(a[0], lambda: print(__doc__))()

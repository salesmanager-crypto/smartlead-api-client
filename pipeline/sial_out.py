"""SIAL Paris 2026 back end: people, emails, custom emails and the master sheet, on top of the shared scripts.

  python sial_out.py people_export N [all] Surfe search work units (sf_in_XX.jsonl) for Brand / Manufacturer
                                           exhibitors with a verified or possible Amazon store, highest revenue
                                           first, one unit per company domain set (duplicate exhibitors skipped)
  python sial_out.py people_select         raw Surfe candidates -> surfe_people.csv, surfe_companies.csv
  python sial_out.py emails_export N BUDGET   se_in_XX.jsonl, verified first, then possible, each by revenue
  python sial_out.py ce_export N [IDS..]   ce_in_XX.jsonl: one email per exhibitor (my-writing-style Outbound
                                           lead-gen mode), with rounded SmartScout facts for its best store
  python sial_out.py ce_check | ce_collect validate ce_out_XX.jsonl / merge passing emails -> cold_emails.csv
  python sial_out.py review_export N       sr_in_XX.jsonl: every matched store, for the store review agents
  python sial_out.py master                -> master_sheet.csv (one row per person)

The title filter, ranking, email collection and SmartScout merge are the shared ones
(surfe_people.py, surfe_emails.py, cold_emails.py, smartscout_store.py), so the rules match every other show.
"""
import glob, json, os, re, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NON_COMPANY_DOMAINS, ROOT
from surfe_people import EXCLUDE, KEEP, PRESIDENT, load, norm_li, rank

WORK = os.path.join(ROOT, "pipeline", "work")
# titles the shared filter lets through that are not sales, marketing or e-commerce owners
EXTRA_EXCLUDE = re.compile(r"\b(financ\w*|sourcing|intelligence|insights?|science|scientist|research|r&d|regulatory|"
                           r"legal|compliance|sustainab\w*|csr|trainee|apprentice)\b", re.I)
# company-name (pass C) hits checked by hand and found to be a different company with the same name
WRONG_COMPANY = {("E0290", "verdeflorperu.com.pe"), ("E0319", "tazne.cz")}
# Surfe emails on a domain that, checked by hand, belongs to a different company than the exhibitor (the person
# has likely moved on): kept visible but not marked Ready
OTHER_COMPANY_EMAIL = {"safefoodcorp.com", "nivagelato.com", "agremat.ca", "jollygoodpud.co.uk", "comeverde.mx",
                       "pfgc.com", "compagniamediterranealiquori.com", "ducsa.com.uy", "idilia.es", "shd.com.lb",
                       "rawpressery.com", "medici-care.com"}
# QA flags that should hold an email until a person checks it (minor notes such as "thin data" do not)
SERIOUS_QA = re.compile(r"same.name|unsure|do not send|don't send|hold|wrong|different (brand|company)|mix(es|ed)? in|"
                        r"not the exhibitor|unrelated", re.I)
STATUS_ORDER = {"verified": 0, "possible": 1, "different brand": 2, "not found": 3, "error": 4}


def csv(name):
    p = os.path.join(ROOT, name)
    return pd.read_csv(p, dtype=str).fillna("") if os.path.exists(p) else pd.DataFrame()


def exhibitors():
    p2 = pd.read_excel(os.path.join(ROOT, "phase2_domains.xlsx"), sheet_name="Exhibitors", dtype=str).fillna("")
    return p2[p2["Exhibitor Type"] == "Brand / Manufacturer"].set_index("Exhibitor ID")


def best_store():
    """Exhibitor ID -> its best Amazon store row (verified before possible, then SmartScout revenue)."""
    amz, ss = csv("amazon_stores.csv"), csv("smartscout_store.csv")
    if not len(amz):
        return {}
    rev = dict(zip(ss["Key"], pd.to_numeric(ss.get("Monthly Revenue", pd.Series(dtype=str)), errors="coerce"))) \
        if len(ss) else {}
    sub = dict(zip(ss["Key"], ss.get("Primary Subcategory", pd.Series(dtype=str)))) if len(ss) else {}
    amz["o"] = amz["Amazon Status"].map(lambda s: STATUS_ORDER.get(s, 9))
    amz["rev"] = amz["Key"].map(lambda k: rev.get(k)).fillna(0)
    # a same-name store outside food and drink (a denture cleanser called Weiss) never outranks a food store
    amz["nonfood"] = amz["Key"].map(lambda k: int(bool(NONFOOD_SUB.search(str(sub.get(k) or "")))))
    rv = store_review()
    wrong = amz["Key"].map(lambda k: rv.get(k, {}).get("verdict") == "wrong brand")
    amz.loc[wrong, "Amazon Status"] = "different brand"  # a reviewer found the store belongs to another company
    amz.loc[wrong, "Note"] = amz.loc[wrong, "Key"].map(lambda k: "Store review: " + rv[k].get("reason", ""))
    amz["o"] = amz["Amazon Status"].map(lambda s: STATUS_ORDER.get(s, 9))
    out = {}
    for eid, g in amz.sort_values(["o", "nonfood", "rev"], ascending=[True, True, False]).groupby("Exhibitor ID", sort=False):
        r = g.iloc[0].to_dict()
        if r["nonfood"] and r["Amazon Status"] in ("verified", "possible"):
            r["Amazon Status"] = "different brand"  # its only matching store sells razors or cat treats, not food
            r["Note"] = f"Only store found is a same-name non-food brand ({sub.get(r['Key'], '')})"
        out[eid] = r
    return out


def exhibitor_revenue():
    """Exhibitor ID -> SmartScout monthly revenue summed over its verified / possible stores (sheet value until
    the store-level pull is in)."""
    amz, ss = csv("amazon_stores.csv"), csv("smartscout_store.csv")
    ex = exhibitors()
    out = {e: float(v or 0) for e, v in ex["Sheet Monthly Revenue"].items()}
    if len(amz) and len(ss):
        ok = amz[amz["Amazon Status"].isin(["verified", "possible"])]
        r = ss.set_index("Key")["Monthly Revenue"].pipe(pd.to_numeric, errors="coerce").fillna(0)
        seen = set()
        tot = {}
        for _, a in ok.iterrows():
            name = a["Amazon Store Name"] or a["Amazon Brand Field"]
            if (a["Exhibitor ID"], name) in seen:
                continue  # two owned brands that resolve to one store count once
            seen.add((a["Exhibitor ID"], name))
            tot[a["Exhibitor ID"]] = tot.get(a["Exhibitor ID"], 0) + float(r.get(a["Key"], 0))
        out.update(tot)
    return out


def store_review():
    """Key -> verdict ("match", "wrong brand", "unsure") from the store review agents."""
    out = {}
    for f in sorted(glob.glob(os.path.join(WORK, "sr_out_*.jsonl"))):
        for l in open(f):
            l = l.strip()
            if l:
                try:
                    r = json.loads(l)
                    out[r["key"]] = r
                except (json.JSONDecodeError, KeyError):
                    pass
    return out


def review_export(n):
    """Store review units: every verified / possible store of every brand owner, with what the exhibitor makes and
    what the store sells, so an agent can catch same-name stores of unrelated companies (Minerva butter for a
    seafood canner)."""
    amz, ss = csv("amazon_stores.csv"), csv("smartscout_store.csv")
    ex = exhibitors()
    prof = csv(os.path.join("pipeline", "work", "sial_profiles.csv"))
    about = dict(zip(prof["Exhibitor ID"], prof["SIAL Description"])) if len(prof) else {}
    owned = brands_owned()
    from smartscout_store import cache_index, key as ss_key
    c, idx = cache_index()
    done = set(store_review()) | {json.loads(l)["key"] for f in glob.glob(os.path.join(WORK, "sr_in_*.jsonl")) for l in open(f)}
    rows = []
    for _, a in amz[amz["Amazon Status"].isin(["verified", "possible"]) & amz["Exhibitor ID"].isin(ex.index)].iterrows():
        if a["Key"] in done:
            continue
        x = ex.loc[a["Exhibitor ID"]]
        hit = {}
        for nm in (a["Amazon Store Name"], a["Amazon Brand Field"]):
            if nm and ss_key(nm) in idx:
                hit = c[idx[ss_key(nm)]]
                break
        p = hit.get("profile") or {}
        rows.append({"key": a["Key"], "id": a["Exhibitor ID"], "exhibitor": x["Exhibitor Name"], "country": x["Country"],
                     "sector": x["Sector"], "about": (about.get(a["Exhibitor ID"], "") or x["Type Reason"])[:400],
                     "owned_brands": owned.get(a["Exhibitor ID"], "")[:300], "brand_searched": a["Brand"],
                     "amazon_store_name": a["Amazon Store Name"], "amazon_brand_field": a["Amazon Brand Field"],
                     "sample_product": a["Sample Product"], "sold_by_sample": a["Sold By"],
                     "primary_subcategory": p.get("Primary Subcategory", ""),
                     "top_subcategories": [s.get("Subcategory") for s in (hit.get("subcats") or [])][:3],
                     "top_sellers": [s.get("Seller Name") for s in (hit.get("sellers") or [])][:5]})
    k = max([int(os.path.basename(f)[6:8]) for f in glob.glob(os.path.join(WORK, "sr_in_*.jsonl"))] or [-1]) + 1
    made = []
    for st in range(0, len(rows), n):
        with open(os.path.join(WORK, f"sr_in_{k:02d}.jsonl"), "w") as fh:
            for r in rows[st:st + n]:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k += 1
    print(f"exported {len(rows)} stores into chunks {' '.join(made) or '(none)'}")


def in_scope():
    ex, best = exhibitors(), best_store()
    return [e for e in ex.index if best.get(e, {}).get("Amazon Status") in ("verified", "possible")]


def people_export(n, scope="amazon"):
    """scope "amazon": exhibitors with a verified / possible store; "all": every brand owner (people search costs
    no email credits, so it can run while the Amazon check is still going)."""
    ex, rev = exhibitors(), exhibitor_revenue()
    owned = brands_owned()
    ids = sorted(in_scope() if scope == "amazon" else list(ex.index), key=lambda e: -rev.get(e, 0))
    queued = set()
    for f in glob.glob(os.path.join(WORK, "sf_in_*.jsonl")):
        queued |= {json.loads(l)["id"] for l in open(f)}
    seen_domains, rows = {}, []
    for f in glob.glob(os.path.join(WORK, "sf_in_*.jsonl")):
        for l in open(f):
            r = json.loads(l)
            for d in r["domains"]:
                seen_domains[d] = r["id"]
    for e in ids:
        if e in queued:
            continue
        x = ex.loc[e]
        doms = [d for d in x["People Domains"].split("; ") if d] or ([x["Domain"]] if x["Domain"] else [])
        if not doms and scope == "all":
            pass  # searched by company name (pass C)
        dup = [seen_domains[d] for d in doms if d in seen_domains]
        if dup:
            continue  # same company exhibiting twice; its people are found under the first exhibitor
        for d in doms:
            seen_domains[d] = e
        rows.append({"id": e, "name": x["Exhibitor Name"], "country": x["Country"], "domains": doms,
                     "brands": owned.get(e, ""), "monthly_revenue": int(rev.get(e, 0))})
    k = max([int(os.path.basename(f)[6:8]) for f in glob.glob(os.path.join(WORK, "sf_in_*.jsonl"))] or [-1]) + 1
    made = []
    for s in range(0, len(rows), n):
        with open(os.path.join(WORK, f"sf_in_{k:02d}.jsonl"), "w") as fh:
            for r in rows[s:s + n]:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k += 1
    print(f"exported {len(rows)} exhibitors into chunks {' '.join(made) or '(none)'}")


def name_words(company):
    stop = {"the", "and", "group", "foods", "food", "international", "company", "sa", "sas", "srl", "spa", "gmbh",
            "ltd", "llc", "inc", "co", "limited", "corporation", "s", "a", "de", "of"}
    return [w for w in re.findall(r"[a-z0-9]{3,}", company.lower()) if w not in stop]


def clean_name(s):
    """'Denham (née Wright) - She/Her' -> 'Denham'; 'Bill (B.T.)' -> 'Bill'; 'Smith, MBA' -> 'Smith'."""
    s = re.sub(r"\(.*?\)|\[.*?\]", " ", str(s or ""))
    s = re.split(r"\s+[-|]\s+|,", s)[0]
    s = re.sub(r"\b(she|he|they)/(her|him|them)s?\b", " ", s, flags=re.I)
    return re.sub(r"\s+", " ", s).strip(" .-")


def people_select():
    raw, cos = load("sf_raw_*.jsonl"), load("sf_co_*.jsonl")
    ex = exhibitors()
    by = {}
    for p in raw:
        p = {k: (p.get(k) or "") for k in ("id", "firstName", "lastName", "jobTitle", "linkedInUrl", "country",
                                            "seniorities", "departments", "companyName", "companyDomain", "pass")}
        p["sen"] = " ".join(p["seniorities"]).lower() if isinstance(p["seniorities"], list) else str(p["seniorities"]).lower()
        p["country"] = str(p["country"]).lower()
        t = p["jobTitle"]
        if not p["firstName"] or not t or p["pass"] in ("error", "done"):
            continue
        dom = str(p["companyDomain"]).lower()
        if (p["id"], dom) in WRONG_COMPANY or any(dom == b or dom.endswith("." + b) for b in NON_COMPANY_DOMAINS):
            continue
        if EXCLUDE.search(t) or EXTRA_EXCLUDE.search(t) or PRESIDENT.search(t) or not KEEP.search(t):
            continue
        m = re.search(r"\s(?:at|@)\s+(.+)$", t, re.I)
        if m and not any(w in m.group(1).lower() for w in name_words(ex["Exhibitor Name"].get(p["id"], ""))):
            continue  # "Market Manager at Firestone Walker": the title names a different employer
        p["firstName"], p["lastName"] = clean_name(p["firstName"]), clean_name(p["lastName"])
        if not p["firstName"] or len(p["lastName"].rstrip(".")) <= 1 or p["firstName"].lower() == p["lastName"].lower():
            continue  # surname shown as an initial only, or a handle repeated as both names
        key = (p["id"], norm_li(p["linkedInUrl"]) or f'{p["firstName"]} {p["lastName"]}'.lower())
        by.setdefault(p["id"], {}).setdefault(key, p)
    seen_li = {}  # the same person found under two exhibitors of one group (VAHDAM, Savencia / Valrhona) stays once
    for eid in sorted(by):
        for key in list(by[eid]):
            li = key[1] if "linkedin.com" in key[1] else ""
            if li and seen_li.setdefault(li, eid) != eid:
                del by[eid][key]
    rows = []
    for eid, d in by.items():
        for i, p in enumerate(sorted(d.values(), key=rank)[:5], 1):
            fix = lambda s: s.strip().title() if s.islower() or s.isupper() else s.strip()
            rows.append({"Exhibitor ID": eid, "Exhibitor Name": ex["Exhibitor Name"].get(eid, p["companyName"]),
                         "First Name": fix(p["firstName"]), "Last Name": fix(p["lastName"]),
                         "Title": p["jobTitle"].strip(), "LinkedIn URL": p["linkedInUrl"],
                         "Country": p["country"].upper(), "Seniority": p["sen"], "Surfe Company": p["companyName"],
                         "Company Domain": p["companyDomain"], "Priority": i, "Source": "Surfe people search"})
    pd.DataFrame(rows).to_csv(os.path.join(ROOT, "surfe_people.csv"), index=False)
    c = pd.DataFrame(cos).drop_duplicates("id", keep="last") if cos else pd.DataFrame()
    c.to_csv(os.path.join(ROOT, "surfe_companies.csv"), index=False)
    got = pd.DataFrame(rows).groupby("Exhibitor ID").size() if rows else pd.Series(dtype=int)
    n = len({json.loads(l)["id"] for f in glob.glob(os.path.join(WORK, "sf_in_*.jsonl")) for l in open(f)})
    print(f"{len(rows)} people for {len(got)} of {n} searched exhibitors; with 5 people: {(got >= 5).sum()}; "
          f"companies enriched: {len(c)}")


def emails_export(n, budget):
    from surfe_emails import person_key
    p = csv("surfe_people.csv")
    best, rev = best_store(), exhibitor_revenue()
    ex = exhibitors()
    p["key"] = p.apply(person_key, axis=1)
    p["arank"] = p["Exhibitor ID"].map(lambda e: STATUS_ORDER.get(best.get(e, {}).get("Amazon Status"), 9))
    p["rev"] = p["Exhibitor ID"].map(lambda e: rev.get(e, 0))
    p["pri"] = pd.to_numeric(p["Priority"])
    p = p[p["arank"] < 2].sort_values(["arank", "rev", "Exhibitor ID", "pri"], ascending=[True, False, True, True])
    queued = set()
    for f in glob.glob(os.path.join(WORK, "se_in_*.jsonl")):
        queued |= {json.loads(l)["key"] for l in open(f)}
    p = p[~p["key"].isin(queued)].head(max(0, budget))
    rows = [{"key": r["key"], "id": r["Exhibitor ID"], "firstName": r["First Name"], "lastName": r["Last Name"],
             "linkedinUrl": r["LinkedIn URL"], "companyDomain": r["Company Domain"] or ex["Domain"].get(r["Exhibitor ID"], ""),
             "companyName": r["Surfe Company"] or r["Exhibitor Name"]} for _, r in p.iterrows()]
    k = max([int(os.path.basename(f)[6:8]) for f in glob.glob(os.path.join(WORK, "se_in_*.jsonl"))] or [-1]) + 1
    made = []
    for s in range(0, len(rows), n):
        with open(os.path.join(WORK, f"se_in_{k:02d}.jsonl"), "w") as fh:
            for r in rows[s:s + n]:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k += 1
    print(f"exported {len(rows)} people into chunks {' '.join(made) or '(none)'}")


def brands_owned():
    b = pd.read_excel(os.path.join(ROOT, "phase4_smartscout.xlsx"), sheet_name="Brands", dtype=str).fillna("")
    b = b[b["Ownership"].isin(["Owned", "Licensed"]) & (b["Brand"] != "")]
    return b.groupby("Exhibitor ID")["Brand"].apply(lambda s: "; ".join(dict.fromkeys(s))).to_dict()


# subcategory words that mark a same-name brand outside food and drink (SmartScout's top-level category is not
# reliable for this: it files coconut milk under Everything Else and cheese spread under Tools & Home Improvement)
NONFOOD_SUB = re.compile(r"denture|face|facial|skin|hair|fragrance|perfume|cologne|makeup|cosmetic|lip |nail|lotion|"
                         r"shampoo|soap|deodorant|shoe|boot|sneaker|apparel|shirt|\bdress(es)?\b|jewel|watch|toy|game|furniture|"
                         r"mattress|bedding|lighting|tool|automotive|cable|phone|laptop|computer|camera|bath|"
                         r"footwear|handbag|wallet|sunglass|eyeglass|vitamin d|keyboard|guitar|book|razor|shav|\bdog|\bcat |\bpet |\blitter", re.I)
CAL = "{{calendar_link}}"
CE_BANNED = [r"—", r"–", r"!", r"\bI'?d love\b", r"\bwould love\b", r"hope this (email )?finds", r"\bleverag",
             r"\bsynerg", r"game.?changer", r"unlock", r"strategic opportunit", r"smartscout", r"touch base",
             r"circle back", r"\bquick question\b", r"[\U0001F300-\U0001FAFF☀-➿]", r"^\s*[-*•]",
             r"\$\d{1,3},\d{3}", r"mouthwatchers", r"run rate", r"\batlas\b", r"case stud",
             r"stop by", r"swing by", r"see you (at|there)", r"meet (you )?(at|in) (sial|paris)", r"I'?ll be at",
             r"we'?ll be at", r"walking (the|sial)", r"\bdrive meaningful", r"growth potential",
             r"\bleads? (the|its|in|balsamic|\w+ (category|categories))\b", r"\bleader\b", r"number one", r"#\s?1\b",
             r"\branked?\b", r"\btop (brand|spot|position)\b", r"\bleading (position|brand)\b"]


def pct_round(x, nd=0):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return round(v, nd) if nd else int(round(v))


def sane_rank(s):
    """SmartScout's "Rank In Subcategory" comes back as 1 for nearly every brand and subcategory (checked across all
    pulls for this show), so it says nothing about the brand's position and is never passed to the writer."""
    return None


def lead_facts(eid, a):
    """Everything the writer may use about one exhibitor's best Amazon store, already rounded."""
    from cold_emails import money
    from smartscout_store import cache_index, key as ss_key
    c, idx = cache_index()
    hit = {}
    for x in (a.get("Amazon Store Name", ""), a.get("Amazon Brand Field", "")):
        if x and ss_key(x) in idx:
            hit = c[idx[ss_key(x)]]
            break
    p, sellers, subs = hit.get("profile") or {}, hit.get("sellers") or [], hit.get("subcats") or []
    rev = pd.to_numeric(p.get("Total Monthly Revenue"), errors="coerce")
    rev = 0.0 if pd.isna(rev) else float(rev)
    ttm = pd.to_numeric(p.get("Trailing 12-Month Revenue"), errors="coerce")
    f = {"brand": a.get("Brand", ""), "amazon_store_name": a.get("Amazon Store Name", "") or a.get("Amazon Brand Field", ""),
         "has_amazon_store": a.get("Has Amazon Store", "") in ("Yes", "True"), "amazon_status": a.get("Amazon Status", ""),
         "in_smartscout": bool(p), "monthly_revenue": money(rev),
         "trailing_12m_revenue": ("" if pd.isna(ttm) or ttm < 60000 or rev > 3000000 or ttm > 36e6 else
                                  f"about ${ttm / 1e6:.1f}M" if ttm >= 1e6 else f"about ${int(round(ttm / 50000) * 50)}k"),
         "mom_growth_pct": pct_round((p.get("Average MoM Growth") or 0) * 100) if p.get("Average MoM Growth") is not None else None,
         "products": p.get("Total Products"), "reviews_rounded": (int(round(float(p["Total Reviews"]), -2))
                                                                   if p.get("Total Reviews") else None),
         "average_rating": p.get("Average Rating"), "average_price": pct_round(p.get("Average Price")),
         "average_sellers_per_product": pct_round(p.get("Average Sellers"), 1), "has_storefront": p.get("Has Storefront"),
         "primary_subcategory": p.get("Primary Subcategory", "")}
    total = sum(float(s.get("Estimated Brand Share") or 0) for s in sellers)
    if sellers and total:
        f["sellers"] = [{"seller": s.get("Seller Name"), "type": s.get("Type"),
                         "share_pct": pct_round(s.get("Estimated Brand Share"))}
                        for s in sorted(sellers, key=lambda s: -float(s.get("Estimated Brand Share") or 0))[:6]
                        if float(s.get("Estimated Brand Share") or 0) >= 1]
        f["seller_count_with_sales"] = sum(1 for s in sellers if float(s.get("Estimated Brand Share") or 0) > 0)
        for t, k in (("Third-party reseller", "reseller_share_pct"), ("Amazon 1P", "amazon_1p_share_pct"),
                     ("Brand direct", "brand_direct_share_pct")):
            f[k] = pct_round(sum(float(s.get("Estimated Brand Share") or 0) for s in sellers if s.get("Type") == t))
    f["subcategories"] = [{"subcategory": s.get("Subcategory"), "brand_revenue_in_it": money(s.get("Revenue")),
                           "share_of_brand_revenue_pct": pct_round(100 * float(s.get("Revenue") or 0) / rev) if rev else None,
                           "market_share_pct": pct_round(s.get("Market Share"), 1)}
                          for s in subs[:3]]
    flags = []
    if a.get("Amazon Status") == "possible":
        flags.append("Amazon store is a possible match, not verified")
    if not p:
        flags.append("Store not in SmartScout; limited data")
    elif rev > 3000000:
        flags.append("Revenue over $3M a month, not cited (likely the whole global brand)")
    cat = p.get("Primary Category", "")
    f["primary_category"] = cat
    odd = [x for x in [p.get("Primary Subcategory", "")] + [s.get("Subcategory", "") for s in subs[:3]]
           if x and NONFOOD_SUB.search(x)]
    if odd:
        flags.append(f"Amazon data includes non-food subcategories ({', '.join(odd)}): may be or mix in a same-name "
                     "non-food brand; use only food and drink figures, or none")
    rv = store_review().get(a.get("Key", ""), {})
    if rv.get("verdict") == "unsure":
        flags.append("Store review unsure this store is the exhibitor's: " + rv.get("reason", ""))
    f["qa_hints"] = flags
    return f, rev


def ce_export(n, redo=()):
    """One email per exhibitor (Outbound lead-gen mode): every contact at the brand gets the same email. Ids in redo
    are exported again even if already queued (their new email replaces the old one)."""
    e = csv("surfe_emails.csv")
    with_email = set(e.loc[e["Email"] != "", "Exhibitor ID"]) if len(e) else set()
    ex, best = exhibitors(), best_store()
    prof = csv(os.path.join("pipeline", "work", "sial_profiles.csv"))
    about = dict(zip(prof["Exhibitor ID"], prof["SIAL Description"])) if len(prof) else {}
    p = csv("surfe_people.csv")
    titles = p.groupby("Exhibitor ID")["Title"].apply(list).to_dict() if len(p) else {}
    queued = set()
    for f in glob.glob(os.path.join(WORK, "ce_in_*.jsonl")):
        queued |= {json.loads(l)["id"] for l in open(f)}
    from smartscout_store import cache_index, key as ss_key
    _, idx = cache_index()
    pulled = set()  # names whose SmartScout chunk has finished, so a miss really means "not in SmartScout"
    for f in glob.glob(os.path.join(WORK, "ssx_in_*.jsonl")):
        if os.path.exists(f.replace("ssx_in_", "ssx_done_").replace(".jsonl", ".txt")):
            pulled |= {ss_key(json.loads(l)["name"]) for l in open(f)}
    rows = []
    for eid in in_scope():
        if (eid in queued and eid not in redo) or eid not in with_email or (redo and eid not in redo):
            continue
        names = [ss_key(n) for n in (best[eid].get("Amazon Store Name", ""), best[eid].get("Amazon Brand Field", "")) if n]
        if not any(n in idx or n in pulled for n in names):
            continue  # SmartScout pull for this store not finished yet; export it in a later round
        x = ex.loc[eid]
        f, rev = lead_facts(eid, best[eid])
        rows.append({"id": eid, "company": x["Exhibitor Name"], "country": x["Country"],
                     "show": f"SIAL Paris, stand {x['SIAL Stand']}" if x["SIAL Stand"] else "SIAL Paris",
                     "about": (about.get(eid, "") or x["Type Reason"])[:400], "contact_titles": titles.get(eid, []),
                     "rev": rev, **f})
    rows.sort(key=lambda r: -r.pop("rev"))
    k = max([int(os.path.basename(f)[6:8]) for f in glob.glob(os.path.join(WORK, "ce_in_*.jsonl"))] or [-1]) + 1
    made = []
    for s in range(0, len(rows), n):
        with open(os.path.join(WORK, f"ce_in_{k:02d}.jsonl"), "w") as fh:
            for r in rows[s:s + n]:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        made.append(f"{k:02d}")
        k += 1
    print(f"exported {len(rows)} exhibitors into chunks {' '.join(made) or '(none)'}")


def ce_problems(r):
    out = []
    body = r.get("body", "")
    lines = [l.strip() for l in body.strip().split("\n") if l.strip()]
    if not lines or lines[0] != "Hi {{first_name}},":
        out.append("first line must be 'Hi {{first_name}},'")
    if not lines or lines[-1] != "Yoni":
        out.append("last line must be 'Yoni' alone")
    if CAL not in lines:
        out.append("{{calendar_link}} must be on its own line")
    core = " ".join(l for l in lines[1:-1] if l != CAL)
    w = len(core.split())
    if not 50 <= w <= 115:
        out.append(f"body is {w} words (aim 60 to 95, at most 110)")
    for pat in CE_BANNED:
        if re.search(pat, body, re.I | re.M):
            out.append(f"banned pattern {pat}")
    if core.count("?") != 1:
        out.append("exactly one question (the ask)")
    if "SIAL" not in core:
        out.append("mention SIAL Paris")
    if "{{" in core.replace("{{first_name}}", ""):
        out.append("unexpected placeholder")
    return out


def ce_load():
    out = {}
    for f in sorted(glob.glob(os.path.join(WORK, "ce_out_*.jsonl"))):
        for l in open(f):
            l = l.strip()
            if l:
                try:
                    r = json.loads(l)
                    out[r["id"]] = r  # a later line for the same exhibitor replaces the earlier one
                except (json.JSONDecodeError, KeyError):
                    pass
    return out


def ce_check(quiet=False):
    src = {json.loads(l)["id"] for f in glob.glob(os.path.join(WORK, "ce_in_*.jsonl")) for l in open(f)}
    got = {k: v for k, v in ce_load().items() if k in src}
    bad = {k: ce_problems(r) for k, r in got.items()}
    bad = {k: v for k, v in bad.items() if v}
    if not quiet:
        for k, v in bad.items():
            print(k, "|", "; ".join(v))
        print(f"{len(got)} written, {len(bad)} failing, {len(src - set(got))} not written yet")
    return got, bad


def ce_collect():
    got, bad = ce_check(quiet=True)
    rows = [{"Exhibitor ID": k, "Email Body": r["body"].strip(), "Email Angle": r.get("angle", "").strip(),
             "QA Flags": r.get("qa_flags", "").strip()} for k, r in got.items() if k not in bad]
    pd.DataFrame(rows, columns=["Exhibitor ID", "Email Body", "Email Angle", "QA Flags"]).to_csv(
        os.path.join(ROOT, "cold_emails.csv"), index=False)
    print(f"{len(rows)} emails collected, {len(bad)} still failing")


COLUMNS = [
    "Exhibitor ID", "Exhibitor Name", "Country", "Sector", "Show", "SIAL Stand", "SIAL Profile", "Website", "Domain",
    "Company LinkedIn", "Facebook", "Instagram", "X", "Parent Company", "Brands Owned", "Amazon Brand",
    "Amazon Store Name", "Has Amazon Store", "Amazon Store URL", "Amazon Status", "Amazon Sold By (sample)",
    "SmartScout Match", "Monthly Revenue", "Annual Revenue (TTM)", "Primary Category", "Primary Subcategory",
    "Average Sellers", "Employees", "HQ Country", "Priority", "First Name", "Last Name", "Title", "Person LinkedIn",
    "Person Country", "Email", "Email Status", "Email Body", "Email Angle", "QA Flags", "Row Status",
]


def short_list(s, n=12):
    items = [x for x in s.split("; ") if x]
    return "; ".join(items[:n]) + (f"; and {len(items) - n} more" if len(items) > n else "")


def master():
    from surfe_emails import person_key
    ex = exhibitors().reset_index()
    social = csv(os.path.join("pipeline", "work", "social_links.csv"))
    social = social.set_index("Exhibitor ID").to_dict("index") if len(social) else {}
    owned = brands_owned()
    co = csv("surfe_companies.csv")
    co = co.drop_duplicates("id", keep="last").set_index("id").to_dict("index") if len(co) else {}
    ss = csv("smartscout_store.csv")
    ss = ss.set_index("Key").to_dict("index") if len(ss) else {}
    best = best_store()
    searched_domains = {}
    for f in glob.glob(os.path.join(WORK, "sf_in_*.jsonl")):
        for l in open(f):
            r = json.loads(l)
            searched_domains[r["id"]] = set(r["domains"])
    searched = set(searched_domains)
    people = csv("surfe_people.csv")
    if len(people):
        people["key"] = people.apply(person_key, axis=1)
    em = csv("surfe_emails.csv")
    em = em.set_index("Key").to_dict("index") if len(em) else {}
    ce = csv("cold_emails.csv")
    ce = ce.set_index("Exhibitor ID").to_dict("index") if len(ce) else {}
    by_ex = {e: g.assign(_p=pd.to_numeric(g["Priority"])).sort_values("_p") for e, g in people.groupby("Exhibitor ID")} \
        if len(people) else {}
    rows = []
    for _, x in ex.iterrows():
        eid = x["Exhibitor ID"]
        a, so = best.get(eid, {}), social.get(eid, {})
        s, c = ss.get(a.get("Key", ""), {}), co.get(eid, {})
        base = {"Exhibitor ID": eid, "Exhibitor Name": x["Exhibitor Name"], "Country": x["Country"],
                "Sector": x["Sector"], "Show": x["Shows"], "SIAL Stand": x["SIAL Stand"],
                "SIAL Profile": x["SIAL Profile URL"], "Website": x["Website"], "Domain": x["Domain"],
                "Company LinkedIn": c.get("linkedInURL") or x["LinkedIn"], "Facebook": so.get("Facebook", ""),
                "Instagram": so.get("Instagram", ""), "X": so.get("X", ""), "Parent Company": x["Parent Company"],
                "Brands Owned": short_list(owned.get(eid, "")), "Amazon Brand": a.get("Brand", ""),
                "Amazon Store Name": a.get("Amazon Store Name", ""),
                "Has Amazon Store": {"True": "Yes", "False": "No"}.get(a.get("Has Amazon Store", ""), a.get("Has Amazon Store", "")),
                "Amazon Store URL": str(a.get("Amazon Store URL", "")).split("?")[0], "Amazon Status": a.get("Amazon Status", ""),
                "Amazon Sold By (sample)": a.get("Sold By", ""), "Employees": c.get("employeeCount", ""),
                "HQ Country": c.get("hqCountry", "")}
        for col in ("SmartScout Match", "Monthly Revenue", "Annual Revenue (TTM)", "Primary Category",
                    "Primary Subcategory", "Average Sellers"):
            base[col] = s.get(col, "")
        for col in ("Monthly Revenue", "Annual Revenue (TTM)"):
            v = pd.to_numeric(base[col], errors="coerce")
            base[col] = "" if pd.isna(v) else str(int(round(v)))
        g = by_ex.get(eid)
        if a and a.get("Amazon Status") not in ("verified", "possible"):
            note = a.get("Note") if isinstance(a.get("Note"), str) else ""
            why = note or {"not found": "no Amazon product found under its brand names",
                           "different brand": "the Amazon store with that name belongs to a different brand",
                           "error": "Amazon check failed"}.get(a.get("Amazon Status"), a.get("Amazon Status", ""))
            rows.append({**base, "Row Status": f"Not on Amazon ({why}); not contacted"})
            continue
        if g is None or not len(g):
            if not a:
                why = "Amazon check not run yet"
            elif a.get("Amazon Status") in ("not found", "different brand", "error"):
                why = f"Not on Amazon ({a['Amazon Status']}); no people searched"
            elif eid not in searched:
                mine = {d for d in [x["Domain"]] + x["People Domains"].split("; ") if d}
                dup = [o for o, ds in searched_domains.items() if o != eid and mine & ds]
                why = f"Same company as {dup[0]}; people listed there" if dup else "People search pending"
            else:
                why = "No sales, marketing or e-commerce people found in Surfe"
            rows.append({**base, "Row Status": why})
            continue
        for _, r in g.iterrows():
            e, m = em.get(r["key"], {}), ce.get(eid, {})
            other = e.get("Email", "").split("@")[-1].lower() in OTHER_COMPANY_EMAIL
            ready = "Ready, check QA flag first" if SERIOUS_QA.search(m.get("QA Flags", "")) else "Ready"
            status = "Check: email is on another company's domain" if other else ready if e.get("Email") and m.get("Email Body") else (
                "No email from Surfe" if e and not e.get("Email") else
                ("Email pending" if not e else "Custom email pending"))
            rows.append({**base, "Priority": r["Priority"], "First Name": r["First Name"], "Last Name": r["Last Name"],
                         "Title": r["Title"], "Person LinkedIn": r["LinkedIn URL"], "Person Country": r["Country"],
                         "Email": e.get("Email", ""), "Email Status": e.get("Email Status", ""),
                         "Email Body": m.get("Email Body", ""), "Email Angle": m.get("Email Angle", ""),
                         "QA Flags": m.get("QA Flags", ""),
                         "Row Status": status})
    d = pd.DataFrame(rows, columns=COLUMNS).fillna("")
    # one person can show up twice (two LinkedIn profiles, or a group listed at two stands): keep the first row per email
    dup = (d["Email"] != "") & d["Email"].str.lower().duplicated()
    first = dict(zip(d.loc[(d["Email"] != "") & ~dup, "Email"].str.lower(), d.loc[(d["Email"] != "") & ~dup, "Exhibitor ID"]))
    lost = set(d.loc[dup, "Exhibitor ID"]) - set(d.loc[~dup, "Exhibitor ID"])
    extra = []
    for eid in lost:
        r = d[dup & (d["Exhibitor ID"] == eid)].iloc[0].to_dict()
        keep = {c: r[c] for c in COLUMNS[:COLUMNS.index("Priority")]}
        extra.append({**keep, "Row Status": f"Same contacts as {first[r['Email'].lower()]}; listed there"})
    d = pd.concat([d[~dup], pd.DataFrame(extra, columns=COLUMNS)], ignore_index=True).fillna("")
    d["_o"] = d["Amazon Status"].map(lambda s: STATUS_ORDER.get(s, 9))
    d["_r"] = pd.to_numeric(d["Monthly Revenue"], errors="coerce").fillna(-1)
    d["_p"] = pd.to_numeric(d["Priority"], errors="coerce").fillna(99)
    d = d.sort_values(["_o", "_r", "Exhibitor ID", "_p"], ascending=[True, False, True, True]).drop(columns=["_o", "_r", "_p"])
    for col in COLUMNS:
        d[col] = d[col].astype(str).str.replace("—", ", ").str.replace("–", "-")
    d.to_csv(os.path.join(ROOT, "master_sheet.csv"), index=False)
    print(f"{len(d)} rows, {d['Exhibitor ID'].nunique()} exhibitors, {(d['First Name'] != '').sum()} people, "
          f"{(d['Email'] != '').sum()} emails, {(d['Email Body'] != '').sum()} custom emails")
    print(d["Row Status"].value_counts().to_string())


NUMERIC = {"Monthly Revenue", "Annual Revenue (TTM)", "Average Sellers", "Employees", "Priority"}


def col_letter(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def sheet_blocks(n, tab="Outbound master"):
    """master_sheet.csv -> pipeline/work/sheet_block_XX.json: {"range", "values"} blocks of n rows (the header in the
    first), ready for Google Sheets update_values. Numbers are written as numbers, everything else as text."""
    d = pd.read_csv(os.path.join(ROOT, "master_sheet.csv"), dtype=str).fillna("")
    for f in glob.glob(os.path.join(WORK, "sheet_block_*.json")):
        os.remove(f)

    def cell(col, v):
        if col in NUMERIC and v != "":
            try:
                x = float(v)
                return int(x) if x.is_integer() else round(x, 2)
            except ValueError:
                return v
        return v
    rows = [list(d.columns)] + [[cell(c, r[c]) for c in d.columns] for _, r in d.iterrows()]
    last = col_letter(len(d.columns))
    k = 0
    for st in range(0, len(rows), n):
        block = rows[st:st + n]
        rng = f"'{tab}'!A{st + 1}:{last}{st + len(block)}"
        # one cell per line, so a reader that truncates long lines still sees every cell in full
        json.dump({"range": rng, "values": block}, open(os.path.join(WORK, f"sheet_block_{k:02d}.json"), "w"),
                  ensure_ascii=False, indent=1)
        k += 1
    print(f"{len(rows)} rows (with header) in {k} blocks of up to {n}")


def sheet_verify(path):
    """Compare a get_values dump of the tab (JSON {"values": [...]}) with master_sheet.csv; print mismatched cells by
    block so a bad block can be rewritten."""
    got = json.load(open(path))["values"]
    d = pd.read_csv(os.path.join(ROOT, "master_sheet.csv"), dtype=str).fillna("")
    want = [list(d.columns)] + d.values.tolist()

    def norm(v, col):
        v = str(v).strip()
        if col in NUMERIC and v:
            try:
                return str(round(float(v.replace(",", "").replace("$", "")), 2))
            except ValueError:
                return v
        return v.replace("\r\n", "\n")
    bad = {}
    for i, w in enumerate(want):
        g = got[i] if i < len(got) else []
        for j, col in enumerate(d.columns):
            if norm(w[j], col) != norm(g[j] if j < len(g) else "", col):
                bad.setdefault(i // 30, []).append((i + 1, col))
    print(f"sheet rows {len(got)}, expected {len(want)}; blocks with mismatches: "
          f"{ {f'{k:02d}': len(v) for k, v in bad.items()} }")
    for k, v in list(bad.items())[:5]:
        print(f"  block {k:02d}: first mismatches {v[:4]}")


if __name__ == "__main__":
    a = sys.argv
    {"people_export": lambda: people_export(int(a[2]), a[3] if len(a) > 3 else "amazon"), "people_select": people_select,
     "emails_export": lambda: emails_export(int(a[2]), int(a[3])), "ce_export": lambda: ce_export(int(a[2]), set(a[3:])),
     "ce_check": ce_check, "ce_collect": ce_collect, "review_export": lambda: review_export(int(a[2])),
     "master": master, "sheet_blocks": lambda: sheet_blocks(int(a[2])),
     "sheet_verify": lambda: sheet_verify(a[2])}[a[1]]()

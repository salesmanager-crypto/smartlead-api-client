"""Phase 10: pre-send QA gate. Builds the Smartlead upload file, and only if every send row passes.

  python presend_qa.py --master <master.csv> --evidence <phase4_smartscout.xlsx> --show "<show name>" --out <dir>

master.csv: one row per contact with Exhibitor ID, Exhibitor Name, Brands Owned, Domain, First Name, Last Name,
Card Email, Email Body, Row Status. Email Body may hold {{first_name}}; the gate renders each contact's own name into
it (Smartlead does not fill merge fields that sit inside a lead's custom field), converts paragraphs to <br>, then checks
the rendered copy exactly as the recipient will read it.

FAIL (blocks the upload file): unresolved merge tags, greeting name not this contact's name, invalid or duplicate
email, a $ or % figure not found in this company's SmartScout data, figures cited without a usable SmartScout match,
company or brand not named, wrong or missing show, a claim Yoni's rules ban, held rows.
WARN (listed for a human to check, does not block): role inboxes, email domain differs from the company's, first names
that look like typos or were cleaned up, length outside range, 3P / hybrid / reseller wording.

--only <smartlead export.csv> keeps just the contacts whose card, alt or work email is in that export (for a V2 campaign of
leads that were never sent). When a card email is a shared inbox (info@, sales@) and Surfe found a VALID work email for the
same person, the person's own email is used.

Writes <out>/qa_report.csv always; writes <out>/smartlead_upload.csv only when there are 0 FAIL rows. Exit code 1 on FAIL.
"""
import argparse, os, re, sys
import pandas as pd

MERGE = re.compile(r"\{\{[^}]*\}\}|\{[a-z_ ]+\}|\[(first ?name|name|company)\]|<(first_?name|name)>", re.I)
BANNED = {
    r"\bno say\b|\bno control\b|doesn't control|does not control": "claims the brand lacks control",
    r"gap is in execution": "diagnoses execution",
    r"\bdeclin|\bslipp?ed\b|\bdown from\b|\bfell\b|\bdropped\b": "claims a decline",
    r"\btiny\b|limited (presence|traction)|undeveloped|little activity|no (amazon )?presence": "calls the business small or absent",
    r"exhibitor list|among the .{0,40}exhibitors": "exhibitor-list framing",
    r"run rate|case stud": "case study in a first email",
    r"—|–": "dash",
    r"leading position|category leader|market leader|leads (the|its) category|\branked\b|\branks\b|#\s?\d\b|number one": "category rank claim",
}
TYPO = re.compile(r"'s'|(?<!\.)\.\.(?!\.)|,,|  |\s[,.]|\b(\w+) \1\b", re.I)
WARN_WORDS = {r"\b3P\b|hybrid": "3P / hybrid pitch, check there is a business reason", r"\breseller": "calls a seller a reseller, check ownership"}
ROLE = re.compile(r"^(info|sales|saleshelp|media|press|pr|support|service|customerservice|customer_service|customersuccess|hello|orders?|wholesale|office|admin|contact|help|"
                  r"investorrelations|ir|marketing|retail|books|product|consumer|consumeraffairs|team|general|enquiries|inquiries)\b", re.I)
WORDS = {"a third": 33.3, "one third": 33.3, "two thirds": 66.7, "half": 50, "a quarter": 25, "three quarters": 75, "a fifth": 20}
GENERIC = {"inc", "llc", "ltd", "co", "corp", "company", "brands", "brand", "foods", "food", "group", "the", "and", "usa", "us",
           "products", "international", "industries", "enterprises", "trading", "designs", "design", "sales", "global", "america"}


def num(v):
    v = pd.to_numeric(str(v).replace(",", "").replace("$", "").replace("%", ""), errors="coerce")
    return None if pd.isna(v) else float(v)


def name_for(first, last):
    """The name the greeting should use, and why it differs from the raw field (for a WARN)."""
    f, note = first.strip().strip(",;"), ""
    if not re.fullmatch(r"(?:[A-Z]\.)+", f):
        f = f.strip(".")
    if f in ("Dr", "Mr", "Ms", "Mrs"):
        return f"{f}. {last.strip().title()}", "title + last name used"
    if not f:
        return "there", "no first name on record"
    if "+" in f:
        f, note = f.replace("+", " and "), "two names"
    if (f.isupper() and len(f) > 2) or f.islower():
        f, note = f.title(), "case fixed"
    if f != first.strip():
        note = note or "punctuation removed"
    return f, note


BRAND_FIX = {}  # Exhibitor ID -> brand name, for names the email writes differently from the sheet (loaded with --brand-fix)


def brand_name(x, text=""):
    """Short brand name for Smartlead's company_name: the brand the email itself names first (as written there),
    else the first brand the company owns, else the cleaned exhibitor name."""
    cands = [b.strip() for b in re.split(r"[;/]", x.get("Brands Owned", "") + ";" + x.get("SmartScout Brand", "")) if b.strip()]
    clean = SUFFIX.sub("", re.split(r"\s*[|(]", x["Exhibitor Name"])[0].strip()).strip()
    cands.append(clean)
    plain = re.sub(r"<br>", " ", text).split("Albert Scott", 1)[-1]
    best = None
    for c in cands:
        c = SUFFIX.sub("", c).strip().rstrip(",.")
        if len(c) < 2:
            continue
        m = re.search(r"(?<![A-Za-z0-9])" + re.escape(c) + r"(?![A-Za-z0-9])", plain, re.I)
        if m and (best is None or (m.start(), len(c)) < (best[0], len(best[1]))):
            best = (m.start(), m.group(0))
    if x["Exhibitor ID"] in BRAND_FIX:
        return BRAND_FIX[x["Exhibitor ID"]]
    if best:
        return best[1]
    return cands[0] if cands else clean


def edit1(a, b):
    a, b = a.lower(), b.lower()
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        d = [i for i in range(len(a)) if a[i] != b[i]]
        return len(d) == 1 or (len(d) == 2 and a[d[0]] == b[d[1]] and a[d[1]] == b[d[0]])
    s, t = (a, b) if len(a) < len(b) else (b, a)
    return any(s == t[:i] + t[i + 1:] for i in range(len(t)))


def render(body, greet):
    body = body.replace("{{first_name}}", greet)
    if "<br>" not in body:
        body = "<br><br>".join(p.strip().replace("\n", "<br>") for p in body.strip().split("\n\n"))
    if body.endswith("<br><br>Yoni") and not body.endswith("Best,<br>Yoni"):
        body = body[: -len("Yoni")] + "Best,<br>Yoni"  # every email signs off "Best," / "Yoni"
    return body


def evidence(rows):
    """Every figure this company's SmartScout data supports: percents, dollar amounts and counts."""
    pct, usd, cnt = [], [], []
    for _, r in rows.iterrows():
        mo, ttm = num(r["Monthly Revenue"]), num(r["Annual Revenue (TTM)"])
        shares = [num(r[c]) for c in ("Dominant Seller Sales %", "Reseller Share %", "Amazon 1P %",
                                       "Sub 1 Market Share", "Sub 2 Market Share", "Sub 3 Market Share")]
        sellers = [float(x) for x in re.findall(r":\s*([\d.]+)%", r["Top 5 Sellers"])]
        rs, p1 = num(r["Reseller Share %"]), num(r["Amazon 1P %"])
        own = [100 - (rs or 0) - (p1 or 0)] if rs is not None or p1 is not None else []
        others = [100 - s for s in sellers[:1]] + [sum(sellers[1:])] if sellers else []
        for g in ("MoM Growth", "12-Month MoM Growth"):
            if num(r[g]) is not None:
                pct += [abs(num(r[g])), abs(num(r[g])) * 100]
        pct += [x for x in shares + sellers + own + others if x is not None]
        for v in (mo, ttm, ttm / 12 if ttm else None, num(r["Sub 1 Revenue"]), num(r["Sub 2 Revenue"]),
                  num(r["Sub 3 Revenue"]), num(r["Average Price"])):
            if v:
                usd.append(v)
        if mo:
            usd += [mo * x / 100 for x in shares[:3] + sellers + own if x]
            # a category's part of the brand's own revenue ("penne brings in about half of that")
            pct += [100 * v / mo for v in (num(r["Sub 1 Revenue"]), num(r["Sub 2 Revenue"]), num(r["Sub 3 Revenue"])) if v]
        cnt += [x for x in (num(r["Total Products"]), num(r["Total Reviews"]), num(r["Seller Count"])) if x]
    for col in ("Monthly Revenue", "Annual Revenue (TTM)", "Total Products"):  # portfolio totals across the company's brands
        tot = sum(num(v) or 0 for v in rows[col])
        if tot:
            (cnt if col == "Total Products" else usd).append(tot)
    return pct, usd, cnt


def supported(val, pool, kind, qual):
    if not pool:
        return False
    if qual in ("under", "less than", "below", "well under", "fewer than"):
        return any(0 <= p <= val * 1.02 for p in pool)
    if qual in ("over", "more than", "above", "at least"):
        return any(val * 0.98 <= p <= val * 2.5 for p in pool)
    tol = (lambda p: abs(p - val) <= max(1.6, 0.16 * val)) if kind == "pct" else (lambda p: abs(p - val) <= 0.16 * val)
    return any(tol(p) for p in pool)


def figures(text):
    t = re.sub(r"<br>", " ", text)
    out = []
    for m in re.finditer(r"(under|less than|below|well under|over|more than|above|at least|nearly|almost|about|roughly|around)?\s*"
                         r"\$(\d[\d,]*(?:\.\d+)?)\s*([KMB])?", t, re.I):
        v = float(m.group(2).replace(",", "")) * {"K": 1e3, "M": 1e6, "B": 1e9}.get((m.group(3) or "").upper(), 1)
        out.append(("usd", v, (m.group(1) or "").lower(), m.group(0).strip()))
    for m in re.finditer(r"(under|less than|below|well under|over|more than|above|at least|nearly|almost|about|roughly|around)?\s*"
                         r"(\d+(?:\.\d+)?)\s*%", t, re.I):
        out.append(("pct", float(m.group(2)), (m.group(1) or "").lower(), m.group(0).strip()))
    for w, v in WORDS.items():
        for m in re.finditer(rf"(less than|more than|over|under|nearly|about|roughly|close to)?\s*\b{w}\b of", t, re.I):
            out.append(("pct", v, (m.group(1) or "").lower(), m.group(0).strip()))
    for m in re.finditer(r"(more than|over|about|roughly|nearly|around)?\s*(\d[\d,]{2,})\s+(products|reviews|sellers|items|listings)", t, re.I):
        out.append(("cnt", float(m.group(2).replace(",", "")), (m.group(1) or "").lower(), m.group(0).strip()))
    return out


SUFFIX = re.compile(r"[,.]?\s+(inc|llc|ltd|co|corp|corporation|company|limited)\.?$", re.I)


def named(text, *names):
    """True when the email names the company or one of its brands (whole name, or a distinctive word of it)."""
    low = text.lower().replace("’", "'")
    for n in names:
        for part in re.split(r"[;/|]", n):
            part = SUFFIX.sub("", part.strip()).strip().lower().replace("’", "'")
            if len(part) >= 2 and re.search(r"(?<![a-z0-9])" + re.escape(part) + r"(?![a-z0-9])", low):
                return True
    return bool(tokens(*names) & tokens(text))


def tokens(*names):
    s = set()
    for n in names:
        for w in re.findall(r"[a-z0-9']+", n.lower().replace("’", "'")):
            w = w.strip("'")
            if w.endswith("'s"):
                w = w[:-2]
            if len(w) >= 3 and w not in GENERIC:
                s.add(w)
    return s


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--master", required=True)
    a.add_argument("--evidence", required=True)
    a.add_argument("--show", required=True, help="exact show name, e.g. 'NACS Show' or 'Las Vegas Souvenir & Resort Gift Show'")
    a.add_argument("--other-shows", default="NACS;Las Vegas;LV Souvenir;AAPEX;SEMA;Surf Expo")
    a.add_argument("--out", required=True)
    a.add_argument("--min-words", type=int, default=60)
    a.add_argument("--max-words", type=int, default=125)
    a.add_argument("--brand-fix", help="CSV with Exhibitor ID, Brand: brand names to use for company_name")
    a.add_argument("--card-only", action="store_true", help="send only to the email on the card; never swap in a Surfe work email")
    a.add_argument("--show-col", help="column saying per contact whether the show is mentioned: 'Yes' = the email must name the show, "
                                      "anything else = it must not (for lists where only some companies exhibit at the next show)")
    a.add_argument("--only", help="CSV exported from Smartlead (any column holding emails): keep only contacts whose email is in it")
    o = a.parse_args()
    os.makedirs(o.out, exist_ok=True)
    m = pd.read_csv(o.master, dtype=str, keep_default_na=False)
    ev = pd.read_excel(o.evidence, dtype=str).fillna("")
    ev = ev[ev["SmartScout Match"].isin(["exact", "close"])]
    others = [s for s in o.other_shows.split(";") if s and s.lower() not in o.show.lower()]
    if o.brand_fix:
        bf = pd.read_csv(o.brand_fix, dtype=str, keep_default_na=False)
        BRAND_FIX.update(dict(zip(bf["Exhibitor ID"], bf["Brand"])))
    only = None
    if o.only:
        ex = pd.read_csv(o.only, dtype=str, keep_default_na=False)
        only = {v.strip().lower() for c in ex.columns for v in ex[c] if re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", v.strip(), re.I)}
        print(f"unsent-leads export: {len(only)} email addresses")
    seen, rows, send = {}, [], []
    shared = m[m["Email Body"] != ""]["Card Email"].str.strip().str.lower().value_counts().to_dict()
    for i, x in m.iterrows():
        body, status = x["Email Body"], x["Row Status"]
        if not body:
            continue
        fail, warn = [], []
        email = x["Card Email"].strip()
        work = x.get("Work Email (Surfe, same person)", "").strip()
        work_ok = work and x.get("Work Email Status", "VALID").upper() in ("VALID", "")
        if o.card_only:
            work = work_ok = ""
        if not email and work:
            email = work
            warn.append("no card email, using the Surfe work email found for this same person")
        elif work_ok and (ROLE.match(email.split("@")[0]) or shared.get(email.lower(), 0) > 1):
            email = work  # the person's own verified inbox beats a shared info@ / sales@ inbox
        if only is not None and not ({e.strip().lower() for e in (x["Card Email"], x.get("Card Alt Email", ""), work) if e} & only):
            rows.append({"Row": i + 2, "Exhibitor ID": x["Exhibitor ID"], "Company": x["Exhibitor Name"], "Contact": x["First Name"],
                         "Email": email, "Result": "SKIP", "Issues": "not in the unsent-leads export"})
            continue
        greet, note = name_for(x["First Name"], x["Last Name"])
        text = render(body, greet)
        if status != "Ready":
            rows.append({"Row": i + 2, "Exhibitor ID": x["Exhibitor ID"], "Company": x["Exhibitor Name"], "Contact": greet,
                         "Email": email, "Result": "HELD", "Issues": status})
            continue
        # merge tags and greeting
        if MERGE.search(text):
            fail.append(f"unresolved merge tag {MERGE.search(text).group(0)}")
        g = re.match(r"Hi ([^,<]+),", text)
        if not g:
            fail.append("does not open with 'Hi <name>,'")
        elif g.group(1) != greet:
            fail.append(f"greeting says '{g.group(1)}' but this contact is '{greet}'")
        if note:
            warn.append(f"first name '{x['First Name']}' -> '{greet}' ({note})")
        local = email.split("@")[0].lower()
        for part in re.split(r"[._\-0-9]+", local):
            fn = greet.split()[0].lower()
            if len(part) >= 4 and greet != "there" and part != fn and not part.startswith(fn) and edit1(part, fn):
                warn.append(f"first name '{greet}' vs email '{local}': possible misspelling")
        # email
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email, re.I):
            fail.append(f"invalid email '{email}'")
        elif email.lower() in seen:
            fail.append(f"duplicate email (also row {seen[email.lower()]})")
        else:
            seen[email.lower()] = i + 2
        if ROLE.match(local):
            warn.append(f"role inbox '{local}@', not a person")
        dom = email.split("@")[-1].lower()
        root = lambda d: ".".join(d.strip().lower().split(".")[-2:])
        if x["Domain"] and root(dom) != root(x["Domain"]) and not re.search(r"gmail|yahoo|hotmail|outlook|aol|msn|comcast|icloud|sbcglobal|earthlink", dom):
            warn.append(f"email domain {dom} differs from company domain {x['Domain']}")
        # company and show
        plain = re.sub(r"<br>", " ", text)
        if not named(plain, x["Exhibitor Name"], x["Brands Owned"]):
            fail.append("company or brand not named")
        need = x.get(o.show_col, "Yes") == "Yes" if o.show_col else True
        if need and o.show.lower() not in plain.lower():
            fail.append(f"show '{o.show}' not mentioned")
        elif not need and o.show.lower() in plain.lower():
            fail.append(f"mentions '{o.show}' but this company is not exhibiting there")
        for s in others:
            if s.lower() in plain.lower():
                fail.append(f"mentions another show '{s}'")
        # claims
        claims = plain  # company and brand names can contain banned words ("Fell"), so take them out first
        for n in re.split(r"[;/|]", x["Exhibitor Name"] + ";" + x["Brands Owned"]):
            if n.strip():
                claims = re.sub(re.escape(SUFFIX.sub("", n.strip())), " ", claims, flags=re.I)
        for pat, why in BANNED.items():
            if re.search(pat, claims, re.I):
                fail.append(f"{why}: '{re.search(pat, claims, re.I).group(0)}'")
        typo_text = re.sub(r"<br>", "\n", text)  # brand names can repeat a word (Good Good, Kuli Kuli): stand them in
        for n in re.split(r"[;/|]", x["Exhibitor Name"] + ";" + x["Brands Owned"]):
            if n.strip() and re.search(r"\b(\w+) \1\b", n, re.I):
                typo_text = re.sub(re.escape(SUFFIX.sub("", n.strip())), "Brand", typo_text, flags=re.I)
        t = TYPO.search(typo_text)
        if t:
            fail.append(f"typo (double possessive, double punctuation or repeated word): '{t.group(0)}'")
        for pat, why in WARN_WORDS.items():
            if re.search(pat, plain, re.I):
                warn.append(why)
        # figures
        mine = ev[ev["Exhibitor ID"] == x["Exhibitor ID"]]
        pct, usd, cnt = evidence(mine)
        figs = figures(plain)
        if figs and not len(mine):
            fail.append("cites figures but the company has no usable SmartScout match")
        else:
            for kind, v, qual, raw in figs:
                pool = {"pct": pct, "usd": usd, "cnt": cnt}[kind]
                if not supported(v, pool, kind, qual):
                    fail.append(f"figure '{raw}' not found in this company's SmartScout data")
        if not text.endswith("<br><br>Best,<br>Yoni"):
            fail.append("does not end with 'Best,' / 'Yoni'")
        n = len(re.sub(r"<br>", " ", text).split())
        if not o.min_words <= n <= o.max_words:
            warn.append(f"{n} words")
        bn = brand_name(x, text)
        if bn.lower() not in plain.lower():
            warn.append(f"company_name '{bn}' is not how the email names the company")
        res = "FAIL" if fail else ("WARN" if warn else "PASS")
        rows.append({"Row": i + 2, "Exhibitor ID": x["Exhibitor ID"], "Company": x["Exhibitor Name"], "Contact": greet,
                     "Email": email, "Result": res, "Issues": " | ".join(fail + warn)})
        send.append({"email": email, "first_name": greet if greet != "there" else "", "last_name": x["Last Name"],
                     "company_name": brand_name(x, text), "email_body": text})
    r = pd.DataFrame(rows)
    r.to_csv(os.path.join(o.out, "qa_report.csv"), index=False)
    c = r["Result"].value_counts().to_dict()
    print(f"{len(r)} contacts checked: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
    up = os.path.join(o.out, "smartlead_upload.csv")
    if c.get("FAIL"):
        if os.path.exists(up):
            os.remove(up)
        print("BLOCKED: fix every FAIL row, then run the gate again. No upload file written.")
        for _, f in r[r["Result"] == "FAIL"].head(40).iterrows():
            print(f"  row {f['Row']} {f['Company']} ({f['Email']}): {f['Issues']}")
        sys.exit(1)
    pd.DataFrame(send).to_csv(up, index=False)
    print(f"PASSED: {len(send)} leads written to {up}. Review the WARN rows in qa_report.csv before upload.")


if __name__ == "__main__":
    main()

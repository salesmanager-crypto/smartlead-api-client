"""Expo West pre-send step: each contact's own first name in their email, then the Phase 10 gate (presend_qa.py).

  python3 pipeline/expowest_presend.py      -> pipeline/work/presend/ (gate_master.csv, gate_evidence.xlsx,
                                               qa_report.csv, smartlead_upload.csv when nothing fails)

greet_name() picks the name the greeting uses: the name the person goes by when the record shows it (a nickname in
quotes or brackets, or the part of a double first name that the email address itself uses), trailing and leading
initials dropped, case fixed, "there" for names in another script. The gate then renders "Hi <name>," into the copy,
checks every figure against this company's own SmartScout numbers (taken here from the raw SmartScout rows, not from
the rounded figures the writer saw) and writes the upload file only when no row fails.
"""
import csv, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT
from expowest_smartscout import detail_rows, key

WORK = os.path.join(ROOT, "pipeline", "work")
OUT = os.path.join(WORK, "presend")
MASTER = os.path.join(ROOT, "expowest_amazon_master.csv")
EMAILS = os.path.join(ROOT, "expowest_emails.csv")
HOLDS = os.path.join(WORK, "send_holds.csv")  # Exhibitor ID, Reason: brands kept out of the send (restricted, doubtful data)
SHOW = "Natural Products Expo West"
DOUBLE = {"mary", "anna", "juan", "jose", "josé", "maría", "maria", "rosa", "rose", "bobbi", "dee", "jo", "ann"}


def squash(s):
    return re.sub(r"[^a-z]", "", s.lower().replace("é", "e").replace("á", "a").replace("í", "i").replace("ó", "o"))


def greet_name(first, last="", email=""):
    """(name for 'Hi <name>,', note when it differs from the raw first name)."""
    raw = first.strip()
    if not raw:
        return "", "no first name on record"
    if re.search(r"[^\x00-ɏ]", raw):
        return "there", f"'{raw}' is not in Latin script"
    if re.fullmatch(r"(?:[A-Z]\.){2,}", raw):
        return raw, ""
    local = squash(email.split("@")[0]) if email else ""
    nick = re.findall(r"[\"“(]([^\"”)]+)[\"”)]", raw)
    base = re.sub(r"\s*[\"“(][^\"”)]*[\"”)]\s*", " ", raw).strip()
    words = [w.strip(".,") for w in re.split(r"\s+", base) if w.strip(".,")]
    words = [w for w in words if len(w.rstrip(".")) > 1 or len(words) == 1]  # drop initials (Eduardo A., W Ross)
    words = [w for w in words if not re.fullmatch(r"(?:[A-Z]\.?)+", w) or len(words) == 1]
    if words and words[0].lower() == "and":
        words = words[1:]
    if "and" in [w.lower() for w in words]:  # "Leo and Patsy": the address belongs to one of them
        words = words[:[w.lower() for w in words].index("and")]
    pick = None
    for n in nick:  # a nickname the person goes by: used when the address uses it or it shares the first letter
        n = n.strip()
        if n and (local.startswith(squash(n)) or (words and n[0].lower() == words[0][0].lower())) \
                and squash(n) not in squash(last):
            pick = n
    if not pick and len(words) >= 2:
        two = squash(words[0] + words[1])
        if local.startswith(two) or local == two or words[0].lower() in DOUBLE and words[1].lower() in DOUBLE | {"jo", "ann", "grace", "lynn"}:
            pick = f"{words[0]} {words[1]}"
        elif local.startswith(squash(words[1])) and len(words[1]) > 2 and not local.startswith(squash(words[0])):
            pick = words[1]  # "S. Baer" -> baer@
    pick = pick or (words[0] if words else raw)
    if pick.isupper() and len(pick) > 2 or pick.islower():
        pick = pick.title()
    return pick, ("" if pick == raw else f"'{raw}' -> '{pick}'")


def email_brand(body, names):
    """The brand as the email itself writes it: the longest leading run of words of any known name that the email
    contains, in the email's own spelling ("Nightingale" for "Nightingale Ice Cream Sandwiches")."""
    text = body.split("Albert Scott", 1)[-1]
    best = None
    for n in names:
        n = re.sub(r"[,.]?\s+(inc|llc|ltd|co|corp|corporation|company|limited)\.?$", "", (n or "").strip(), flags=re.I)
        words = n.split()
        for k in range(len(words), 0, -1):
            phrase = " ".join(words[:k])
            if len(phrase) < 3:
                break
            m = re.search(r"(?<![A-Za-z0-9])" + re.escape(phrase) + r"(?![A-Za-z0-9])", text, re.I)
            if m:
                if best is None or (k, -m.start()) > (best[0], -best[1]):
                    best = (k, m.start(), m.group(0))
                break
    return best[2].replace("’", "'") if best else ""


def fnum(v):
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None


def build():
    os.makedirs(OUT, exist_ok=True)
    emails = {r["Exhibitor ID"]: r for r in csv.DictReader(open(EMAILS, encoding="utf-8"))}
    ss = {r["Exhibitor ID"]: r for r in csv.DictReader(open(os.path.join(ROOT, "smartscout_brands.csv"), encoding="utf-8"))}
    sellers, subcats = detail_rows("sellers"), detail_rows("subcats")
    rows = list(csv.DictReader(open(MASTER, encoding="utf-8")))
    holds = {r["Exhibitor ID"]: r["Reason"] for r in csv.DictReader(open(HOLDS, encoding="utf-8"))} if os.path.exists(HOLDS) else {}
    gm, notes = [], {}
    for r in rows:
        if not r["First Name"]:
            continue
        e = emails.get(r["Exhibitor ID"], {})
        g, note = greet_name(r["First Name"], r["Last Name"], r["Email"])
        notes[(r["Exhibitor ID"], r["Email"], r["First Name"])] = (g, note)
        s = ss.get(r["Exhibitor ID"], {})
        gm.append({"Exhibitor ID": r["Exhibitor ID"], "Exhibitor Name": r["Exhibitor"],
                   "Brands Owned": "; ".join(x for x in (r["Amazon Store Name"], s.get("SmartScout Brand", ""),
                                                         r["Also Listed As"]) if x),
                   "SmartScout Brand": s.get("SmartScout Brand", ""), "Domain": r["Domain"],
                   "First Name": g, "Last Name": r["Last Name"], "Card Email": r["Email"],
                   "Email Body": e.get("Email Body", ""),
                   "Row Status": ("Held: " + holds[r["Exhibitor ID"]]) if r["Exhibitor ID"] in holds and r["Row Status"] == "Ready"
                   else r["Row Status"] if e else "No email copy",
                   "Show Mention": "Yes" if r["In 2027 List"] == "Yes" and re.search(r"2027: [^;]+", r["Booths"]) else "No"})
    with open(os.path.join(OUT, "brand_fix.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Exhibitor ID", "Brand"])
        for eid, e in emails.items():
            s = ss.get(eid, {})
            m = next((r for r in rows if r["Exhibitor ID"] == eid), {})
            b = email_brand(e["Email Body"], [s.get("SmartScout Brand"), m.get("Amazon Store Name"), m.get("Exhibitor"),
                                              *re.split(r"[;/]", m.get("Also Listed As", ""))])
            if b:
                w.writerow([eid, b])
    with open(os.path.join(OUT, "gate_master.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(gm[0]))
        w.writeheader()
        w.writerows(gm)
    ev = []
    for eid, s in ss.items():
        if eid not in emails:
            continue
        match = {"exact": "exact", "same name, different case or spacing": "close"}.get(s["SmartScout Match"], "")
        k = key(s["SmartScout Brand"])
        sl = sorted({x["Seller Name"]: x for x in sellers.get(k, []) if x.get("Seller Name")}.values(),
                    key=lambda x: -(fnum(x.get("Estimated Brand Share")) or 0))[:5]
        sc = sorted({x["Subcategory Context Name"]: x for x in subcats.get(k, []) if x.get("Subcategory Context Name")}.values(),
                    key=lambda x: -(fnum(x.get("Monthly Revenue")) or 0))[:3]
        share = lambda x: fnum(x.get("Estimated Brand Share")) or 0  # already a percent of the brand's revenue
        amz = sum(share(x) for x in sl if x["Seller Name"].lower() in ("amazon.com", "whole foods market"))
        rec = {"Exhibitor ID": eid, "SmartScout Match": match, "Monthly Revenue": s["Monthly Revenue"],
               "Annual Revenue (TTM)": s["TTM Revenue"], "Dominant Seller Sales %": round(share(sl[0]), 2) if sl else "",
               "Reseller Share %": "", "Amazon 1P %": round(amz, 2) if sl else "",
               "Top 5 Sellers": "; ".join(f"{x['Seller Name']}: {round(share(x), 2)}%" for x in sl),
               "MoM Growth": s["MoM Growth"], "12-Month MoM Growth": s["12-Month MoM Growth"],
               "Average Price": s["Average Price"], "Total Products": s["Total Products"],
               "Total Reviews": s["Total Reviews"], "Seller Count": len(sl) or ""}
        for i in range(3):
            x = sc[i] if i < len(sc) else {}
            ms = fnum(x.get("Market Share"))
            rec[f"Sub {i + 1} Market Share"] = round(ms * 100, 2) if ms is not None else ""
            rec[f"Sub {i + 1} Revenue"] = x.get("Monthly Revenue", "")
        ev.append(rec)
    import pandas as pd
    pd.DataFrame(ev).to_excel(os.path.join(OUT, "gate_evidence.xlsx"), index=False)
    cleaned = sum(1 for g, n in notes.values() if n)
    print(f"{len(gm)} contacts with a person, {sum(1 for x in gm if x['Email Body'])} with copy, {cleaned} first names cleaned; "
          f"{len(ev)} companies of evidence")
    return notes


def run():
    build()
    cmd = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "presend_qa.py"),
           "--master", os.path.join(OUT, "gate_master.csv"), "--evidence", os.path.join(OUT, "gate_evidence.xlsx"),
           "--show", SHOW, "--show-col", "Show Mention",
           "--brand-fix", os.path.join(OUT, "brand_fix.csv"), "--out", OUT, "--min-words", "75", "--max-words", "110"]
    return subprocess.call(cmd)


if __name__ == "__main__":
    a = sys.argv[1:] or ["run"]
    if a[0] == "names":
        for r in csv.DictReader(open(MASTER, encoding="utf-8")):
            g, n = greet_name(r["First Name"], r["Last Name"], r["Email"])
            if n:
                print(f"{r['First Name']!r:32} {r['Email']:45} -> {g}")
    else:
        sys.exit(run())

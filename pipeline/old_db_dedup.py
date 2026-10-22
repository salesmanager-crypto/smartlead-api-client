"""Dedupe the old Expo West database against the new exhibitor list (company level only).

  python3 pipeline/old_db_dedup.py OLD_CSV [OLD_CSV ...]

Step 1: compile the old files into one company list (company name + domain, from the Website column or the
contact's email when it is not a free mailbox), deduped on normalized name or domain.
Step 2: merge that list with the new exhibitor master (2024 / 2026 / 2027) and dedupe again, matching on
normalized company name, a looser name (filler words dropped), the Amazon store name, or the company domain.

Outputs (gitignored):
  old_db_companies.csv           one row per unique old company
  expowest_combined_dedup.csv    union of old and new, one row per company, with where it was found
  pipeline/work/old_db_match.json  new exhibitor id -> old company match (read by expowest_campaign.py)
"""
import csv, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, domain_of, loose_name, norm_name, registrable_domain

WORK = os.path.join(ROOT, "pipeline", "work")
MASTER = os.path.join(ROOT, "expowest_master.csv")
FREE = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com", "me.com", "live.com",
        "msn.com", "comcast.net", "att.net", "verizon.net", "protonmail.com", "mail.com", "gmx.com", "ymail.com",
        "sbcglobal.net", "bellsouth.net", "cox.net", "earthlink.net", "mac.com", "qq.com", "163.com", "126.com",
        "yahoo.co.uk", "hotmail.co.uk", "googlemail.com", "rocketmail.com", "zoho.com", "naver.com"}
# shared or generic domains that would join unrelated companies (a retailer's mail domain, the show organizer)
SHARED = {"worldpantry.com", "newhope.com", "informa.com", "us.com", "uk.com", "eu.com", "linktr.ee"}
csv.field_size_limit(10**9)


def pick(row, *names):
    for n in names:
        for k in row:
            if k and k.strip().lower().replace("_", " ") == n:
                return (row[k] or "").strip()
    return ""


def company_domain(website, email):
    d = domain_of(website) if website else ""
    if not d and "@" in email:
        d = email.split("@", 1)[1].strip().lower()
    d = registrable_domain(d) if d else ""
    return "" if d in FREE or d in SHARED else d


class Groups:
    """Union-find over companies, keyed by normalized name, loose name and domain."""

    def __init__(self):
        self.parent, self.keys = {}, {}

    def find(self, x):
        while self.parent.setdefault(x, x) != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def add(self, item, keys):
        self.parent.setdefault(item, item)
        for k in keys:
            if not k:
                continue
            if k in self.keys:
                a, b = self.find(item), self.find(self.keys[k])
                if a != b:
                    self.parent[a] = b
            else:
                self.keys[k] = item

    def groups(self):
        out = {}
        for x in self.parent:
            out.setdefault(self.find(x), []).append(x)
        return out


def name_keys(name):
    n, l = norm_name(name), loose_name(name)
    keys = []
    if len(n) >= 3:
        keys.append("n:" + n)
    if len(l) >= 4:
        keys.append("n:" + l)
    return keys


def load_old(paths):
    rows = []
    for p in paths:
        src = os.path.basename(p)
        for r in csv.DictReader(open(p, encoding="utf-8-sig", errors="ignore")):
            name = pick(r, "company / account", "company account", "company")
            email = pick(r, "email").lower()
            dom = company_domain(pick(r, "website"), email)
            if not name and not dom:
                continue
            sent = pick(r, "x means already sent").upper() == "X"
            rows.append({"name": name, "domain": dom, "src": src, "sent": sent,
                         "verified": pick(r, "result").lower() == "valid"})
    return rows


def main(paths):
    old = load_old(paths)
    # step 1: dedupe the old files on their own
    g = Groups()
    for i, r in enumerate(old):
        g.add(("o", i), name_keys(r["name"]) + (["d:" + r["domain"]] if r["domain"] else []))
    old_cos = []
    for members in g.groups().values():
        rs = [old[i] for _, i in members]
        names = sorted({r["name"] for r in rs if r["name"]}, key=lambda s: (-sum(1 for r in rs if r["name"] == s), s))
        doms = sorted({r["domain"] for r in rs if r["domain"]})
        old_cos.append({"Company": names[0] if names else doms[0], "Other Names": "; ".join(names[1:4]),
                        "Domain": "; ".join(doms[:3]), "Contacts In Old Files": len(rs),
                        "Already Sent (old)": "Yes" if any(r["sent"] for r in rs) else "No",
                        "Files": "; ".join(sorted({r["src"][:40] for r in rs})),
                        "_names": names, "_doms": doms})
    old_cos.sort(key=lambda c: c["Company"].lower())
    with open(os.path.join(ROOT, "old_db_companies.csv"), "w", newline="", encoding="utf-8") as f:
        fields = ["Company", "Other Names", "Domain", "Contacts In Old Files", "Already Sent (old)", "Files"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(old_cos)

    # step 2: merge with the new exhibitor list and dedupe again
    new = list(csv.DictReader(open(MASTER, encoding="utf-8")))
    stores = {}
    amz = os.path.join(ROOT, "amazon_stores.csv")
    if os.path.exists(amz):
        for r in csv.DictReader(open(amz, encoding="utf-8")):
            if r["Amazon Status"] in ("verified", "possible") and r["Amazon Store Name"]:
                stores.setdefault(r["Exhibitor ID"], set()).add(r["Amazon Store Name"])
    g2 = Groups()
    for i, c in enumerate(old_cos):
        keys = [k for n in c["_names"] for k in name_keys(n)] + ["d:" + d for d in c["_doms"]]
        g2.add(("o", i), keys)
    for r in new:
        names = [r["Exhibitor"]] + [x for x in r["Also Listed As"].split("; ") if x] + sorted(stores.get(r["Exhibitor ID"], []))
        names += re.findall(r"\(([^)]+)\)", r["Exhibitor"])  # "10000 Inc (Magic Mind)" also matches "Magic Mind"
        keys = [k for n in names for k in name_keys(n)] + (["d:" + r["Domain"]] if r["Domain"] and r["Domain"] not in SHARED else [])
        g2.add(("n", r["Exhibitor ID"]), keys)
    newby = {r["Exhibitor ID"]: r for r in new}
    combined, match = [], {}
    for members in g2.groups().values():
        olds = [old_cos[i] for t, i in members if t == "o"]
        news = [newby[i] for t, i in members if t == "n"]
        if news:
            for r in news:
                match[r["Exhibitor ID"]] = {"old_company": "; ".join(c["Company"] for c in olds[:3]),
                                            "old_sent": any(c["Already Sent (old)"] == "Yes" for c in olds),
                                            "old_contacts": sum(c["Contacts In Old Files"] for c in olds)}
        lead = news[0] if news else None
        combined.append({
            "Company": lead["Exhibitor"] if lead else olds[0]["Company"],
            "Domain": (lead["Domain"] if lead and lead["Domain"] else "; ".join(sorted({d for c in olds for d in c["_doms"]}))[:120]),
            "Found In": "Both" if news and olds else ("New list only" if news else "Old database only"),
            "New Exhibitor ID(s)": "; ".join(r["Exhibitor ID"] for r in news),
            "Years Exhibited (new)": "; ".join(sorted({r["Years"] for r in news})),
            "In 2027 List": "Yes" if any(r["In 2027"] == "Yes" for r in news) else ("No" if news else ""),
            "Old Company Name(s)": "; ".join(c["Company"] for c in olds[:3]),
            "Contacts In Old Files": sum(c["Contacts In Old Files"] for c in olds),
            "Already Sent (old)": "Yes" if any(c["Already Sent (old)"] == "Yes" for c in olds) else ("No" if olds else ""),
        })
    combined.sort(key=lambda c: (c["Found In"] != "Both", c["Company"].lower()))
    with open(os.path.join(ROOT, "expowest_combined_dedup.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(combined[0]))
        w.writeheader()
        w.writerows(combined)
    json.dump(match, open(os.path.join(WORK, "old_db_match.json"), "w"))

    from collections import Counter
    print(f"old files: {len(old)} contact rows -> {len(old_cos)} unique companies "
          f"({sum(1 for c in old_cos if c['Already Sent (old)'] == 'Yes')} with contacts already sent)")
    print(f"new list: {len(new)} exhibitors")
    print("combined:", len(combined), dict(Counter(c["Found In"] for c in combined)))
    print(f"new exhibitors matched to the old database: {sum(1 for v in match.values() if v['old_company'])}")


if __name__ == "__main__":
    main(sys.argv[1:])

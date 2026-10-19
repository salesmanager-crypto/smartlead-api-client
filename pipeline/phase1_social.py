"""Phase 1 social links: Facebook, X / Twitter, Instagram, YouTube and TikTok from the cached show pages.

  python phase1_social.py        -> pipeline/work/social_links.csv (Exhibitor ID, Facebook, X, Instagram,
                                    YouTube, TikTok), one row per exhibitor with at least one link

Reads the detail pages cached by phase1_scrape.py (cache/mys/<show>/detail_<exhid>.json.gz) and only the
exhibitor's own social-media block, so share buttons and the show's own accounts are not picked up.
Contact names on MapYourShow sit behind the My Show Planner login and are not public, so they are not
collected here.
"""
import gzip, json, os, re, sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CACHE, ROOT

OUT = os.path.join(ROOT, "pipeline", "work", "social_links.csv")
NETWORKS = {"Facebook": r"facebook\.com", "X": r"(?:twitter|x)\.com", "Instagram": r"instagram\.com",
            "YouTube": r"youtube\.com", "TikTok": r"tiktok\.com"}


def links(html):
    m = re.search(r'class="column social-media_container"(.*?)</div>', html, re.S)
    if not m:
        return {}
    hrefs = re.findall(r'href="([^"]+)"', m.group(1))
    out = {}
    for net, pat in NETWORKS.items():
        for h in hrefs:
            if re.search(r"https?://(?:www\.|m\.)?" + pat + r"/.+", h, re.I) and net not in out:
                out[net] = h.strip()
    return out


def main():
    ex = pd.read_excel(os.path.join(ROOT, "phase1_exhibitors.xlsx"), sheet_name="Exhibitors", dtype=str).fillna("")
    rows = []
    for _, r in ex.iterrows():
        got = {}
        for key in r["Source Keys"].split(";"):
            key = key.strip()
            if ":" not in key:
                continue
            show, exhid = key.split(":", 1)
            f = os.path.join(CACHE, "mys", show, f"detail_{exhid}.json.gz")
            if not os.path.exists(f):
                continue
            with gzip.open(f, "rt") as fh:
                d = json.load(fh)
            for net, url in links(d.get("main_html") or "").items():
                got.setdefault(net, url)
        if got:
            rows.append({"Exhibitor ID": r["Exhibitor ID"], **{n: got.get(n, "") for n in NETWORKS}})
    pd.DataFrame(rows, columns=["Exhibitor ID", *NETWORKS]).to_csv(OUT, index=False)
    print(f"{len(rows)} of {len(ex)} exhibitors have social links; "
          + ", ".join(f"{n} {sum(1 for x in rows if x[n])}" for n in NETWORKS))


if __name__ == "__main__":
    main()

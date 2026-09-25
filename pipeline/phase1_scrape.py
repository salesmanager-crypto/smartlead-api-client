"""Phase 1: pull every AAPEX and SEMA 2026 exhibitor (gallery endpoint + detail pages).

Resumable: gallery pages and detail pages are cached under cache/mys/<show>/, and every
finished detail row is appended to phase1_checkpoint.csv. Rerunning skips done keys.

Usage: python3 pipeline/phase1_scrape.py [--limit N] [--show AAPEX|SEMA]
"""
import argparse, gzip, json, os, re, sys, time
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (CACHE, CHROMIUM, ROOT, UA, Checkpoint, load_state, polite_sleep,
                    save_state)

SHOWS = {
    "AAPEX": "https://aapex2026.mapyourshow.com",
    "SEMA": "https://sema26.mapyourshow.com",
}
GALLERY = "/8_0/explore/exhibitor-gallery.cfm?featured=false"
SEARCH = "/8_0/ajax/remote-proxy.cfm?action=search&searchtype=exhibitorgallery&searchsize=50&start={start}"
DETAIL = "/8_0/exhibitor/exhibitor-details.cfm?exhid={exhid}"

CP_PATH = os.path.join(ROOT, "phase1_checkpoint.csv")
CP_FIELDS = ["Key", "Show", "exhid", "Exhibitor Name", "Booth", "Website", "LinkedIn", "About",
             "Categories", "All Categories Count", "Show Brands", "Address City", "Address State",
             "Address Country", "Detail URL", "Gallery Name", "Gallery Booths", "Fetched At",
             "Notes"]

BLOCK_HOSTS = ("google-analytics", "googletagmanager", "doubleclick", "facebook", "hotjar",
               "clarity.ms", "linkedin", "twitter", "youtube", "vimeo", "hubspot", "adservice")

EXTRACT_JS = r"""
() => {
  const txt = el => el ? el.textContent.replace(/\s+/g, ' ').trim() : '';
  const h1 = document.querySelector('h1.exhibitor-name') || document.querySelector('h1');
  const booths = [...document.querySelectorAll('a[id^="newfloorplanlink_sidebar"]')].map(a => txt(a));
  const descEl = document.querySelector('#section-description');
  let about = '';
  if (descEl) {
    const ps = [...descEl.querySelectorAll('p, li')];
    about = ps.length ? ps.map(p => txt(p)).filter(Boolean).join('\n') : txt(descEl);
  }
  const sections = {};
  for (const art of document.querySelectorAll('main article')) {
    const h = txt(art.querySelector('.section-heading, h2'));
    const items = [...art.querySelectorAll('li')].map(li => txt(li)).filter(Boolean);
    sections[art.id || h] = {heading: h, items: items};
  }
  const webLink = [...document.querySelectorAll('.section--contactinfo a[href]')]
      .find(a => (a.title || '').toLowerCase().includes('on the web'));
  return {
    name: txt(h1), booths: booths, about: about, sections: sections,
    web_link: webLink ? webLink.getAttribute('href') : '',
    title: document.title,
    main_html: (document.querySelector('main') || document.body).outerHTML
        .replace(/<svg[\s\S]*?<\/svg>/g, '<svg/>'),
  };
}
"""


def js_string_value(html, var):
    m = re.search(var + r':\s*"((?:[^"\\]|\\.)*)"', html)
    if not m:
        return ""
    try:
        return json.loads('"' + m.group(1) + '"')
    except Exception:
        return m.group(1).replace("\\/", "/")


def js_object_value(html, var):
    m = re.search(var + r":\s*(\{[^{}]*\})", html)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except Exception:
        return {}


class Browser:
    def __init__(self, pw):
        self.b = pw.chromium.launch(executable_path=CHROMIUM)
        self.ctx = self.b.new_context(user_agent=UA, viewport={"width": 1400, "height": 1000})
        self.ctx.route("**/*", self._route)
        self.page = self.ctx.new_page()
        self.warmed = set()

    @staticmethod
    def _route(route):
        req = route.request
        if req.resource_type in ("image", "media", "font") or any(h in req.url for h in BLOCK_HOSTS):
            return route.abort()
        return route.continue_()

    def warm(self, show):
        if show in self.warmed:
            return
        self.page.goto(SHOWS[show] + GALLERY, wait_until="domcontentloaded", timeout=90000)
        self.page.wait_for_timeout(2500)
        self.warmed.add(show)

    def close(self):
        self.b.close()


def blocked(title, html):
    t = (title or "").lower()
    return any(k in t for k in ("403", "forbidden", "captcha", "access denied", "too many", "attention required")) \
        or "captcha" in (html or "")[:20000].lower()


def fetch_gallery(br, show):
    """Page through the gallery ajax endpoint. Returns list of hit field dicts."""
    cdir = os.path.join(CACHE, "mys", show)
    os.makedirs(cdir, exist_ok=True)
    hits, start, total = [], 0, None
    while total is None or start < total:
        path = os.path.join(cdir, f"gallery_{start}.json")
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
        else:
            br.warm(show)
            url = SHOWS[show] + SEARCH.format(start=start)
            for attempt in range(6):
                try:
                    r = br.ctx.request.get(url, headers={
                        "X-Requested-With": "XMLHttpRequest", "Referer": SHOWS[show] + GALLERY})
                    if r.status == 429:
                        print(f"{show} gallery 429; pausing 10 minutes", flush=True)
                        time.sleep(600)
                        continue
                    data = r.json()
                    break
                except Exception as e:
                    wait = 2 ** (attempt + 1)
                    print(f"{show} gallery start={start} error {e!r}; retry in {wait}s", flush=True)
                    time.sleep(wait)
            else:
                raise RuntimeError(f"gallery fetch failed for {show} start={start}")
            with open(path, "w") as f:
                json.dump(data, f)
            polite_sleep(1, 2)
        ex = data["DATA"]["results"]["exhibitor"]
        total = int(ex["found"])
        page_hits = [h["fields"] for h in ex.get("hit", [])]
        if not page_hits:
            break
        hits.extend(page_hits)
        start += 50
    # the endpoint can repeat a hit across pages; keep first occurrence per exhid
    seen, out = set(), []
    for h in hits:
        if h["exhid_l"] not in seen:
            seen.add(h["exhid_l"])
            out.append(h)
    print(f"{show}: gallery total {total}, unique hits collected {len(out)}", flush=True)
    return total, out


def fetch_detail(br, show, exhid):
    cdir = os.path.join(CACHE, "mys", show)
    path = os.path.join(cdir, f"detail_{exhid}.json.gz")
    if os.path.exists(path):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f), True
    url = SHOWS[show] + DETAIL.format(exhid=exhid)
    last_err = None
    for attempt in range(6):
        try:
            resp = br.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            status = resp.status if resp else 0
            try:
                br.page.wait_for_selector("h1.exhibitor-name", timeout=20000)
                br.page.wait_for_timeout(300)
            except Exception:
                pass
            data = br.page.evaluate(EXTRACT_JS)
            html = br.page.content()
            if status == 429 or blocked(data["title"], html if not data["name"] else ""):
                print(f"{show} {exhid}: blocked (status {status}, title {data['title']!r}); pausing 10 minutes",
                      flush=True)
                time.sleep(600)
                br.warmed.discard(show)
                br.warm(show)
                continue
            if status >= 500 or (status == 202 and not data["name"]):
                raise RuntimeError(f"status {status}")
            data["status"] = status
            data["website_value"] = js_string_value(html, "websiteValue")
            data["linkedin_value"] = js_string_value(html, "linkedInValue")
            data["address"] = js_object_value(html, "addressValues")
            data["url"] = url
            data["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            with gzip.open(path, "wt", encoding="utf-8") as f:
                json.dump(data, f)
            return data, False
        except Exception as e:
            last_err = e
            wait = 2 ** (attempt + 1)
            print(f"{show} {exhid}: error {e!r}; retry in {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"detail failed {show} {exhid}: {last_err!r}")


def booth_number(label):
    # "Venetian Expo - Level 2 — V3044" -> "V3044"; "Hall — V19720 — TAITRA" -> "V19720"
    parts = [p.strip() for p in label.split("—") if p.strip()]
    if len(parts) >= 2:
        return parts[1]
    return parts[0] if parts else label.strip()


def clean_gallery_booth(b):
    return re.sub(r"randomstring$", "", b or "")


def build_row(show, hit, d):
    notes = []
    exhid = hit["exhid_l"]
    name = d.get("name") or hit.get("exhname_t", "")
    if not d.get("name"):
        notes.append("Detail page had no exhibitor name; used gallery name")
    booths = [booth_number(b) for b in d.get("booths", []) if b]
    if not booths:
        gb = [clean_gallery_booth(b) for b in hit.get("boothsdisplay_la", []) if b]
        booths = gb
        notes.append("No booth on detail page; used gallery booth" if gb else "No booth listed")
    website = (d.get("website_value") or d.get("web_link") or "").strip()
    if not website:
        notes.append("No website on show page")
    linkedin = (d.get("linkedin_value") or "").strip()
    if linkedin and "linkedin.com" not in linkedin.lower():
        notes.append(f"LinkedIn field did not look like a LinkedIn URL: {linkedin}")
        linkedin = ""
    about = (d.get("about") or "").strip()
    if not about and hit.get("exhdesc_t"):
        about = hit["exhdesc_t"].strip()
        notes.append("About taken from gallery listing (detail page had none)")
    if not about:
        notes.append("No About text on show page")
    cats, brands = [], []
    for sec in d.get("sections", {}).values():
        heading = (sec.get("heading") or "").lower()
        if heading.startswith("product categories"):
            cats = sec.get("items", [])
        elif heading.startswith("brands"):
            brands = sec.get("items", [])
    if not cats:
        notes.append("No product categories shown")
    addr = d.get("address") or {}
    return {
        "Key": f"{show}:{exhid}", "Show": show, "exhid": exhid, "Exhibitor Name": name,
        "Booth": "; ".join(dict.fromkeys(booths)), "Website": website, "LinkedIn": linkedin,
        "About": about, "Categories": "; ".join(cats[:5]), "All Categories Count": len(cats),
        "Show Brands": "; ".join(brands), "Address City": (addr.get("CITY") or "").strip(),
        "Address State": (addr.get("STATE") or "").strip(),
        "Address Country": (addr.get("COUNTRY") or "").strip(), "Detail URL": d.get("url", ""),
        "Gallery Name": hit.get("exhname_t", ""),
        "Gallery Booths": "; ".join(clean_gallery_booth(b) for b in hit.get("boothsdisplay_la", [])),
        "Fetched At": d.get("fetched_at", ""), "Notes": "; ".join(notes),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--show", choices=list(SHOWS), default=None)
    args = ap.parse_args()

    state = load_state()
    state["current_phase"] = 1
    cp = Checkpoint(CP_PATH, CP_FIELDS, "Key")
    shows = [args.show] if args.show else list(SHOWS)
    with sync_playwright() as pw:
        br = Browser(pw)
        galleries = {}
        for show in shows:
            total, hits = fetch_gallery(br, show)
            galleries[show] = hits
            state.setdefault("phase1", {})[show] = {"gallery_total": total, "gallery_hits": len(hits)}
            save_state(state)
        grand = sum(len(h) for h in galleries.values())
        done_count = sum(1 for k in cp.done if k.split(":")[0] in shows)
        flagged = sum(1 for k, r in cp.done.items() if k.split(":")[0] in shows and r.get("Notes"))
        processed = 0
        for show in shows:
            for hit in galleries[show]:
                key = f"{show}:{hit['exhid_l']}"
                if key in cp.done:
                    continue
                if args.limit and processed >= args.limit:
                    break
                try:
                    d, cached = fetch_detail(br, show, hit["exhid_l"])
                    row = build_row(show, hit, d)
                except Exception as e:
                    cached = True
                    row = build_row(show, hit, {"url": SHOWS[show] + DETAIL.format(exhid=hit["exhid_l"])})
                    row["Notes"] = f"Detail page failed after retries ({e}); gallery fields only; " + row["Notes"]
                cp.add(row)
                processed += 1
                done_count += 1
                flagged += 1 if row["Notes"] else 0
                if done_count % 50 == 0:
                    print(f"phase 1: {done_count} of {grand} done, {flagged} flagged", flush=True)
                if not cached:
                    polite_sleep(1, 2)
        print(f"phase 1: {done_count} of {grand} done, {flagged} flagged (run finished)", flush=True)
        br.close()
    state["phase1"]["detail_done"] = done_count
    save_state(state)
    cp.close()


if __name__ == "__main__":
    main()

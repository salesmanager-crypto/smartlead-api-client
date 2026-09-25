"""Shared helpers for the AAPEX + SEMA 2026 exhibitor pipeline."""
import csv, json, os, random, re, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache")
STATE_PATH = os.path.join(ROOT, "run_state.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
CHROMIUM = "/opt/pw-browsers/chromium"

csv.field_size_limit(10**9)


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"current_phase": 1, "handles": {}, "caches": {}}


def save_state(state):
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_PATH)


def polite_sleep(lo, hi):
    time.sleep(random.uniform(lo, hi))


class Checkpoint:
    """Append-only CSV checkpoint keyed by a column; flushes after every row."""

    def __init__(self, path, fields, key):
        self.path, self.fields, self.key = path, fields, key
        self.done = {}
        if os.path.exists(path):
            with open(path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    self.done[row[key]] = row
        new = not os.path.exists(path)
        self.f = open(path, "a", newline="", encoding="utf-8")
        self.w = csv.DictWriter(self.f, fieldnames=fields, extrasaction="ignore")
        if new:
            self.w.writeheader()
            self.f.flush()

    def add(self, row):
        self.w.writerow(row)
        self.f.flush()
        os.fsync(self.f.fileno())
        self.done[row[self.key]] = row

    def close(self):
        self.f.close()


LEGAL = r"(incorporated|inc|llc|l l c|corp|corporation|co|ltd|limited|company|lp|llp|plc|gmbh|sa|srl|pty)"


def norm_name(name):
    s = (name or "").lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    prev = None
    while prev != s:  # strip trailing legal suffixes repeatedly ("... co inc")
        prev = s
        s = re.sub(r"(?:\s|^)" + LEGAL + r"$", "", s).strip()
    return s.replace(" ", "")


NON_COMPANY_DOMAINS = {
    "facebook.com", "linkedin.com", "instagram.com", "twitter.com", "x.com", "youtube.com",
    "amazon.com", "ebay.com", "alibaba.com", "aliexpress.com", "google.com", "sites.google.com",
    "mapyourshow.com", "wixsite.com", "godaddysites.com", "tiktok.com", "made-in-china.com",
    "etsy.com", "walmart.com", "shopify.com", "myshopify.com", "linktr.ee", "bit.ly",
}


def domain_of(url):
    if not url:
        return ""
    s = url.strip().lower()
    s = re.sub(r"^[a-z]+://", "", s)
    s = s.split("/")[0].split("?")[0].split("#")[0].split(":")[0]
    s = re.sub(r"^www\d?\.", "", s)
    s = s.strip(".")
    if "." not in s or " " in s:
        return ""
    return s

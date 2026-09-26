import sys, os, re, time
sys.path.insert(0, '/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad')
from out import *
sys.path.insert(0, BASE)
from common import fetch
from bs4 import BeautifulSoup
SID, SHOW = 'S15', 'Snowbound Expo'
LIST = 'https://snowboundexpo.com/exhibitors'
t = fetch(LIST); s = BeautifulSoup(t, 'html.parser')
catmap = {o['value']: o.get_text(strip=True) for o in s.select('select.exhibitor_category option') if o['value'] != 'all'}
entries = []
for a in s.find_all('a', href=True):
    h = a['href']
    if '/exhibitor/' not in h: continue
    url = h if h.startswith('http') else 'https://snowboundexpo.com' + h
    ps = [p.get_text(' ', strip=True) for p in a.find_all('p')]
    title = a.select_one('p.title'); stand = a.select_one('p.stand-number')
    tier = ''
    for p in a.find_all('p'):
        if p is not title and p is not stand and p.get_text(strip=True): tier = p.get_text(' ', strip=True)
    cats = [catmap.get(c, '') for c in (a.get('data-categories') or '').split() if c != 'all']
    entries.append(dict(url=url, name=title.get_text(' ', strip=True) if title else a.get_text(' ', strip=True), stand=stand.get_text(' ', strip=True) if stand else '', tier=tier, cats=[c for c in cats if c]))
print('entries', len(entries))
if os.path.exists(csv_path(SID)): os.remove(csv_path(SID))
for n, e in enumerate(entries):
    d = fetch(e['url']); notes = []
    about = web = li = ''
    if d:
        ds = BeautifulSoup(d, 'html.parser')
        sec = ds.select_one('section.company-description')
        if sec:
            links = sec.select_one('.links')
            for a in (links.find_all('a', href=True) if links else []):
                h = a['href']
                if 'Go to website' in a.get_text(): web = h
                elif 'linkedin.com' in h:
                    li = linkedin_ok(h)
                    if not li: notes.append('LinkedIn link on page was not a company page: ' + h)
            if links: links.decompose()
            about = clean(sec.get_text('\n', strip=True))
        if not web: notes.append('detail page had no website')
    else: notes.append('detail page could not be loaded')
    booth = e['stand']
    if booth.upper() == 'TBD': booth = ''; notes.append('booth listed as TBD')
    if booth and not re.search(r'\d', booth):
        notes.append('location shown as "%s" (brand shown within that retailer area, no booth number)' % booth); booth = ''
    if e['tier']: notes.append('listed as ' + e['tier'].title())
    row = {'Show ID': SID, 'Show Name': SHOW, 'Exhibitor Name': e['name'], 'Booth': booth, 'Website': fix_url(web), 'LinkedIn': li,
           'About': about, 'About Summary': summarize(about), 'Categories': '; '.join(e['cats'][:5]), 'City': '', 'State': '', 'Country': '',
           'Detail URL': e['url'], 'Source': LIST, 'List Status': 'current list', 'Notes': '; '.join(notes)}
    append_row(SID, row)
rows = finalize(SID); print('FINAL', stats(rows))

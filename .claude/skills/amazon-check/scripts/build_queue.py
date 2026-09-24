#!/usr/bin/env python3
"""Build the unique-brand queue from a lead sheet.

One entry per brand: key = Company (lower-cased), else the business email domain, else website.
Free-mail domains are ignored. Rows with none of these get a row-number key and are reported.

Usage: build_queue.py leads.xlsx [--sheet NAME] [--out queue.json] [--only-status "Sells,Listed (reseller/unclear)"]
"""
import argparse, json, openpyxl

FREE = {'gmail.com','yahoo.com','hotmail.com','outlook.com','icloud.com','aol.com','me.com','live.com','msn.com',
        'comcast.net','att.net','naver.com','qq.com','163.com','126.com','bellsouth.net','verizon.net','ymail.com',
        'protonmail.com','mac.com','sbcglobal.net','hotmail.co.uk','yahoo.co.uk'}

p = argparse.ArgumentParser()
p.add_argument("xlsx"); p.add_argument("--sheet"); p.add_argument("--out", default="queue.json")
p.add_argument("--only-status", help="comma list; keep rows whose status column has one of these")
p.add_argument("--status-col", default="Flag 2/3 - Amazon (Sells / Does Not Sell)")
p.add_argument("--link-col", default="Amazon Link")
a = p.parse_args()

wb = openpyxl.load_workbook(a.xlsx); ws = wb[a.sheet] if a.sheet else wb[wb.sheetnames[0]]
H = [c.value for c in ws[1]]
def col(name): return H.index(name) + 1 if name in H else None
cC, cE, cE2, cW = col('Company'), col('Email'), col('Email 2'), col('Website')
cS, cL = col(a.status_col), col(a.link_col)
keep = set(s.strip() for s in a.only_status.split(',')) if a.only_status else None

brands, noid = {}, []
for r in range(2, ws.max_row + 1):
    if not any(c.value not in (None, '') for c in ws[r]): continue
    if keep and (ws.cell(r, cS).value if cS else None) not in keep: continue
    comp = str(ws.cell(r, cC).value).strip() if cC and ws.cell(r, cC).value else ''
    doms = [str(e).split('@')[1].strip().lower() for e in ((ws.cell(r, cE).value if cE else None), (ws.cell(r, cE2).value if cE2 else None)) if e and '@' in str(e)]
    dom = next((d for d in doms if d not in FREE), '')
    web = str(ws.cell(r, cW).value).strip() if cW and ws.cell(r, cW).value else ''
    key = comp.lower() if comp else (dom or (web.lower() if web else f'row{r}'))
    if key.startswith('row'): noid.append(r)
    b = brands.setdefault(key, {'key': key, 'company': comp, 'domain': dom, 'website': web, 'link': '', 'rows': []})
    b['rows'].append(r)
    if cL and ws.cell(r, cL).value and not b['link']: b['link'] = str(ws.cell(r, cL).value).strip()

json.dump(list(brands.values()), open(a.out, 'w'), indent=1, ensure_ascii=False)
print(f"rows considered: {sum(len(b['rows']) for b in brands.values())}  unique brands: {len(brands)}  -> {a.out}")
if noid: print(f"rows with no company, business email or website (will be NOT FOUND): {noid}")

import pandas as pd, re, json
from helpers import qa_email, CKPT, load_input, NEW_COLS, SS_COLS
d=pd.read_csv(CKPT)
d['key']=d['show']+'|'+d['exhibitor']
print("rows",len(d),"unique keys",d['key'].nunique(),"with email",d['Email'].notna().sum())
OPEN={"FNCE 2025":"Saw that ","FLIBS 2026":"Saw you're exhibiting at FLIBS next month.","Las Vegas Souvenir & Resort Gift Show 2026":"Saw you're exhibiting at the Las Vegas Souvenir & Resort Gift Show next week."}
BAD_OPEN=["great meeting you","we met","following up on our conversation","great connecting"]
issues=[]
for _,r in d.iterrows():
    e=str(r['Email']); s=str(r['Subject'])
    f=qa_email(s,e); f=list(f[0]) if isinstance(f,tuple) else list(f)
    low=e.lower()
    if 'smartscout' in low or 'smartscout' in s.lower(): f.append('mentions SmartScout')
    for b in BAD_OPEN:
        if b in low: f.append(f'bad opener:{b}')
    lines=[l for l in e.split('\n') if l.strip()]
    op=lines[1] if len(lines)>1 else ''
    exp=OPEN[r['show']]
    if r['show']=="FNCE 2025":
        if not (op.startswith("Saw that ") and op.endswith(" exhibited at FNCE last year.")): f.append('opener mismatch')
    elif op!=exp: f.append('opener mismatch')
    if '{{company}}' in e: f.append('unfilled company')
    if 'quick question' in s.lower(): f.append('subject quick question')
    if f: issues.append((r['key'],f))
print("issues",len(issues))
for k,f in issues: print(k,f)
# show counts
print(d.groupby('show').size().to_dict())
print(d.groupby('show')['SS_Match_Confidence'].value_counts().to_dict())

import json, os, re, csv, sys, datetime
import pandas as pd

INPUT='tradeshow_exhibitors_amazon_check_verified.xlsx'
CKPT='tradeshow_checkpoint.csv'
CACHE='smartscout_cache.json'
QUEUE='queue.json'
SS_COLS=['SS_Brand_Match','SS_Match_Confidence','SS_Category','SS_Subcategory','SS_Monthly_Revenue','SS_TTM_Revenue','SS_Total_Products','SS_Total_Reviews','SS_Avg_Rating','SS_Avg_Price','SS_Avg_Sellers','SS_Single_Seller_Name','SS_Amazon_1P_Pct','SS_MoM_Growth','SS_12M_MoM_Growth','SS_Has_Storefront','SS_Storefront_URL','SS_Top_Products','SS_Seller_Coverage','SS_Seller_Count','SS_Seller_Type','SS_Reseller_Share_Pct']
NEW_COLS=SS_COLS+['Angle','Angle_Data_Points','Subject','Email','QA_Flags','Processed_At']
BANNED=['strategic opportunity','drive meaningful value','unlock growth potential','leverage','synergy','elevate','i hope this email finds you well',"i'd love to",'game-changer','game changer','seamless','cutting-edge','cutting edge','i wanted to take a moment','smartscout','great meeting you','we met','following up on our conversation','quick question']

def load_input():
    return pd.read_excel(INPUT, sheet_name='Exhibitors')

def load_cache():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def save_cache(c):
    tmp=CACHE+'.tmp'; json.dump(c,open(tmp,'w'),indent=1); os.replace(tmp,CACHE)

def done_keys():
    if not os.path.exists(CKPT): return set()
    df=pd.read_csv(CKPT, usecols=['show','exhibitor'])
    return set(df['show'].astype(str)+'|'+df['exhibitor'].astype(str))

def norm(s): return re.sub(r'[^a-z0-9]','',str(s).lower())

def derive(brand_query, raw, brand_sellers=None, conf=None):
    """raw = {'profile':[row]|[], 'sellers':[rows], 'products':[rows]}"""
    out={c:None for c in SS_COLS}
    prof=(raw.get('profile') or [None])[0]
    if not prof or conf in ('not found','wrong match'):
        out['SS_Brand_Match']=prof['Brand Name'] if prof else None
        out['SS_Match_Confidence']=conf or 'not found'
        return out
    out['SS_Brand_Match']=prof['Brand Name']; out['SS_Match_Confidence']=conf or ('exact' if norm(prof['Brand Name'])==norm(brand_query) else 'close')
    out['SS_Category']=prof.get('Primary Category'); out['SS_Subcategory']=prof.get('Primary Subcategory')
    out['SS_Monthly_Revenue']=round(prof.get('Total Monthly Revenue') or 0,2); out['SS_TTM_Revenue']=round(prof.get('Trailing 12-Month Revenue') or 0,2)
    out['SS_Total_Products']=prof.get('Total Products'); out['SS_Total_Reviews']=prof.get('Total Reviews')
    out['SS_Avg_Rating']=prof.get('Average Rating'); out['SS_Avg_Price']=prof.get('Average Price'); out['SS_Avg_Sellers']=prof.get('Average Sellers')
    out['SS_Single_Seller_Name']=prof.get('Single Seller Name') or None
    out['SS_Amazon_1P_Pct']=round(100*(prof.get('Average Amazon Revenue %') or 0),1)
    out['SS_MoM_Growth']=prof.get('Average MoM Growth'); out['SS_12M_MoM_Growth']=prof.get('Average 12-Month MoM Growth')
    out['SS_Has_Storefront']=str(prof.get('Has Storefront')).lower()=='true'; out['SS_Storefront_URL']=prof.get('Storefront URL') or None
    prods=raw.get('products') or []
    out['SS_Top_Products']='; '.join(f"{p['Product Title'][:90]} | {p['ASIN']} | ${round(p['Monthly Revenue Estimate']):,}" for p in prods[:5]) or None
    sellers=raw.get('sellers') or []
    out['SS_Seller_Coverage']='; '.join(f"{s['Seller Name']}: {round(s['Estimated Brand Share'],1)}%" for s in sellers[:5]) or None
    out['SS_Seller_Count']=len(sellers)
    bq=norm(brand_query); bm=norm(prof['Brand Name']); bs=[norm(x) for x in (brand_sellers or [])]
    amz=sum(s['Estimated Brand Share'] for s in sellers if s['Seller Name']=='Amazon.com')
    def is_brand(s):
        n=norm(s['Seller Name'])
        if n in bs: return True
        return bool(n) and (bq in n or bm in n or (len(n)>=5 and (n in bq or n in bm)))
    brand=sum(s['Estimated Brand Share'] for s in sellers if s['Seller Name']!='Amazon.com' and is_brand(s))
    resell=sum(s['Estimated Brand Share'] for s in sellers if s['Seller Name']!='Amazon.com' and not is_brand(s))
    out['SS_Reseller_Share_Pct']=round(resell,1)
    if not sellers: out['SS_Seller_Type']=None
    elif amz>=70: out['SS_Seller_Type']='Amazon 1P'
    elif brand>=70: out['SS_Seller_Type']='Brand direct'
    elif resell>=70: out['SS_Seller_Type']='Third-party resellers'
    else: out['SS_Seller_Type']='Mixed'
    out['_brand_direct_pct']=round(brand,1)
    return out

def qa_email(subject, email):
    flags=[]
    if '—' in email or '–' in email or '—' in subject or '–' in subject: flags.append('em/en dash')
    if '!' in email or '!' in subject: flags.append('exclamation')
    low=email.lower()
    for b in BANNED:
        if b in low or b in subject.lower(): flags.append(f'banned:{b}')
    if not email.startswith('Hi '): flags.append('no greeting')
    if not email.rstrip().endswith('\nYoni'): flags.append('no Yoni signoff')
    body=email.split('\n',1)[1].rsplit('Yoni',1)[0] if '\n' in email else email
    body=body.replace('{{calendar_link}}','').replace('{{first_name}}','').replace('{{company}}','')
    body=re.sub(r'You can grab a time here:\s*','',body)
    wc=len(body.split())
    if wc<60 or wc>110: flags.append(f'wordcount:{wc}')
    qs=[l for l in email.split('\n') if l.strip().endswith('?')]
    if len(qs)!=1: flags.append(f'asks:{len(qs)}')
    # unrounded numbers: any $ figure with more than 2 significant digits, or plain numbers with commas
    for m in re.findall(r'\$[\d,\.]+[kKmM]?',email):
        digits=re.sub(r'[^\d]','',m.rstrip('kKmM'))
        if len(digits.rstrip('0'))>2 and not m.endswith(('k','K','M','m')): flags.append(f'unrounded:{m}')
        if len(re.sub(r'^0+','',digits).rstrip('0'))>2: flags.append(f'unrounded:{m}')
    for m in re.findall(r'(?<![\$\d])\d{1,3}(?:,\d{3})+(?!\d)',email):
        if len(re.sub(r'[^\d]','',m).rstrip('0'))>2: flags.append(f'unrounded:{m}')
    if '{{first_name}}' not in email and not re.match(r'Hi [A-Z][a-z]+,',email): flags.append('greeting name')
    sl=len(subject.split())
    if sl<3 or sl>7: flags.append(f'subject_len:{sl}')
    return flags, wc

def append_rows(finished, raw_by_brand):
    """finished: list of dicts with key,row,brand_query,conf,brand_sellers,angle,angle_points,subject,email,qa_flags"""
    cache=load_cache()
    for b,raw in raw_by_brand.items():
        if b not in cache: cache[b]=raw
    save_cache(cache)
    inp=load_input(); done=done_keys()
    orig_cols=list(inp.columns)
    exists=os.path.exists(CKPT)
    n=0
    with open(CKPT,'a',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        if not exists: w.writerow(orig_cols+NEW_COLS)
        for r in finished:
            if r['key'] in done: continue
            raw=cache.get(r['brand_query']) or {}
            d=derive(r['brand_query'],raw,r.get('brand_sellers'),r.get('conf'))
            flags,wc=qa_email(r['subject'],r['email'])
            qa=list(r.get('qa_flags') or [])
            if flags: qa.append('QA_AUTO:'+','.join(flags))
            orig=inp.iloc[r['row']]
            assert f"{orig['show']}|{orig['exhibitor']}"==r['key'], (r['key'], orig['exhibitor'])
            vals=[('' if pd.isna(v) else v) for v in orig.tolist()]
            vals+= [d[c] for c in SS_COLS]+[r['angle'],r['angle_points'],r['subject'],r['email'],'; '.join(qa),datetime.datetime.now().isoformat(timespec='seconds')]
            w.writerow(vals); f.flush(); n+=1; done.add(r['key'])
            if flags: print('QA', r['key'], flags, 'wc', wc)
            else: print('ok', r['key'], 'wc', wc, d['SS_Seller_Type'], d['SS_Match_Confidence'])
    return n

def status():
    done=done_keys(); q=json.load(open(QUEUE))
    nf=0
    if os.path.exists(CKPT):
        df=pd.read_csv(CKPT); nf=int((df['SS_Match_Confidence'].isin(['not found','wrong match'])).sum())
    return len(done), len(q), nf

def next_batch(n=25):
    done=done_keys(); q=json.load(open(QUEUE)); cache=load_cache()
    todo=[x for x in q if x['key'] not in done][:n]
    for x in todo:
        x['cached']=x['query'] in cache
    return todo

def update_rows(fixes):
    """fixes: {key: {'Subject':..., 'Email':..., 'QA_Flags_add': str}}"""
    df=pd.read_csv(CKPT, dtype=str, keep_default_na=False)
    keys=df['show']+'|'+df['exhibitor']
    n=0
    for k,f in fixes.items():
        idx=df.index[keys==k]
        assert len(idx)==1, k
        i=idx[0]
        for col in ('Subject','Email','Angle','Angle_Data_Points'):
            if col in f: df.at[i,col]=f[col]
        flags,wc=qa_email(df.at[i,'Subject'],df.at[i,'Email'])
        qa=[x for x in df.at[i,'QA_Flags'].split('; ') if x and not x.startswith('QA_AUTO:')]
        if f.get('QA_Flags_add'): qa.append(f['QA_Flags_add'])
        if flags: qa.append('QA_AUTO:'+','.join(flags))
        df.at[i,'QA_Flags']='; '.join(qa); n+=1
        print('fixed' if not flags else 'STILL', k, flags, 'wc', wc)
    df.to_csv(CKPT,index=False)
    return n

import pandas as pd, json, re, datetime
from helpers import load_input, CKPT, NEW_COLS, SS_COLS
inp=load_input()
ck=pd.read_csv(CKPT)
ck['key']=ck['show'].astype(str)+'|'+ck['exhibitor'].astype(str)
inp['key']=inp['show'].astype(str)+'|'+inp['exhibitor'].astype(str)
pri=inp['priority'].astype(str)
summ=inp['amazon_presence_summary'].astype(str)
inscope=pri.str.startswith('1') | (pri.str.startswith('2') & summ.str.startswith('LISTED'))
assert inscope.sum()==399, inscope.sum()
derived=[c for c in ck.columns if c not in inp.columns and c!='key']
enr=inp.merge(ck[['key']+derived],on='key',how='left')
enr['Scope']=['In scope' if s else f'Out of scope: {p}' for s,p in zip(inscope,pri)]
missing=enr[inscope & enr['Email'].isna()]
assert len(missing)==0, missing[['key']]
enr=enr.drop(columns=['key'])
orig=[c for c in inp.columns if c!='key']
enr=enr[orig+derived+['Scope']]
up=enr[enr['Email'].notna()][['show','exhibitor','SS_Brand_Match','Subject','Email','Angle']].copy()
up['first_name']=''; up['last_name']=''; up['email']=''
with pd.ExcelWriter('tradeshow_FINAL.xlsx',engine='openpyxl') as w:
    enr.to_excel(w,sheet_name='Enriched',index=False)
    up.to_excel(w,sheet_name='SmartLead_Upload',index=False)
print("Enriched",enr.shape,"Upload",up.shape)
# stats for run log
s=ck.copy()
out=[]
out.append("# Trade show enrichment run log\n")
out.append(f"Generated {datetime.date.today().isoformat()}. Input: tradeshow_exhibitors_amazon_check_verified.xlsx, sheet Exhibitors, {len(inp)} rows. Output: tradeshow_FINAL.xlsx (sheets Enriched and SmartLead_Upload). Checkpoint: tradeshow_checkpoint.csv. Cache: smartscout_cache.json.\n")
out.append("## Scope and counts per show\n")
out.append("| Show | Input rows | In scope | Emails written | Exact | Close | Not found | Wrong match |")
out.append("|---|---|---|---|---|---|---|---|")
for show,g in s.groupby('show'):
    vc=g['SS_Match_Confidence'].value_counts()
    out.append(f"| {show} | {(inp['show']==show).sum()} | {len(g)} | {g['Email'].notna().sum()} | {vc.get('exact',0)} | {vc.get('close',0)} | {vc.get('not found',0)} | {vc.get('wrong match',0)} |")
vc=s['SS_Match_Confidence'].value_counts()
out.append(f"| Total | {len(inp)} | {len(s)} | {s['Email'].notna().sum()} | {vc.get('exact',0)} | {vc.get('close',0)} | {vc.get('not found',0)} | {vc.get('wrong match',0)} |\n")
out.append(f"Out of scope rows: {(~inscope).sum()} (left untouched in Enriched, marked in the Scope column).\n")
out.append("## Angle distribution\n")
out.append("| Seller type (fresh data) | Rows |")
out.append("|---|---|")
for k,v in s['SS_Seller_Type'].fillna('n/a (not found / wrong match)').value_counts().items(): out.append(f"| {k} | {v} |")
out.append("")
out.append("## Method notes\n")
out.append("- Amazon presence was not re-checked for any row. Scope came only from the priority and amazon_presence_summary columns.")
out.append("- Every in-scope row got a fresh pull of three saved queries (brand profile, top sellers, top products). Results are cached by queried brand name in smartscout_cache.json; repeat brands were reused from cache (Simrad for the Kongsberg row, Teakdecking Systems for the Teak Deck Company row, Solara Suncare for the Solara Labs row).")
out.append("- Brand name order used for the query: smartscout_brand, else amazon_brand_name, else the store name in amazon_store_url, else the cleaned exhibitor name. Two attempts maximum per row; the second attempt used the exhibitor name or a variant.")
out.append("- Seller classification from fresh data: Amazon.com counted as 1P; a seller whose name matches the brand counted as brand direct; everything else, including Whole Foods Market and agency accounts such as Pattern, counted as third-party. Where the sheet's amazon_sold_by disagreed with the fresh data, the fresh data was used and the difference is noted in QA_Flags.")
out.append("- FNCE opener: the template line 'Saw that {{company}} exhibited at FNCE last year.' was written with the real brand name in place of {{company}} so the emails read correctly without a merge field. Las Vegas rows use 'next week', FLIBS rows use 'next month'.")
out.append("- Tool name is not mentioned in any email. Data is referred to as 'from what we can see' or 'looking at your listings'.")
out.append("- Saved query handles expired twice (during batch 5 and batch 11). Each time the three handles were renewed with query_analytics and the batch's pulls were rerun. Handles are stored in handles.json.")
out.append("- Fallbacks: one profile query errored with 'That query couldn't run' (Hooker, batch 11) and one earlier (My Arcade); the retry succeeded for My Arcade, Hooker was treated as not found after the second attempt. Yaza's seller query returned empty, so the seller came from the sheet and is flagged.")
out.append("- Business plan limits: no brand revenue history, so the 12-month trend uses the average 12-month month-over-month growth field. US marketplace only.")
out.append("- Word count discipline: emails that measured over 110 body words after the first draft were trimmed and remeasured; those rows carry 'trimmed for length' or a wordcount note in QA_Flags.\n")
out.append("## Not found (industry-level email written)\n")
for show,g in s[s['SS_Match_Confidence']=='not found'].groupby('show'):
    out.append(f"**{show}** ({len(g)}): "+"; ".join(g['exhibitor'].astype(str).tolist())+"\n")
out.append("## Wrong match (sheet brand mapping did not fit the exhibitor; industry-level email written)\n")
for show,g in s[s['SS_Match_Confidence']=='wrong match'].groupby('show'):
    out.append(f"**{show}** ({len(g)}):\n")
    for _,r in g.iterrows(): out.append(f"- {r['exhibitor']}: {r['QA_Flags']}")
    out.append("")
out.append("## Close matches (verify identity before sending)\n")
for _,r in s[s['SS_Match_Confidence']=='close'].iterrows(): out.append(f"- {r['show']} | {r['exhibitor']} -> {r['SS_Brand_Match']}: {r['QA_Flags']}")
out.append("")
out.append("## QA-flagged rows\n")
out.append("Rows where QA_Flags contains anything beyond a plain confirmation of the sheet's seller type. All emails passed the final QA pass (word count 60 to 110, no dashes, no exclamation marks, no banned phrases, no unrounded numbers, tool name absent, greeting present, exactly one ask, ends with Yoni, correct opener per show).\n")
q=s[s['QA_Flags'].notna() & ~s['QA_Flags'].astype(str).str.fullmatch(r'sheet [^;]* confirmed')]
out.append(f"{len(q)} rows flagged:\n")
for _,r in q.iterrows(): out.append(f"- {r['show']} | {r['exhibitor']} [{r['SS_Match_Confidence']}]: {r['QA_Flags']}")
open('tradeshow_run_log.md','w').write("\n".join(out)+"\n")
print("run log written", len(q), "flagged rows")

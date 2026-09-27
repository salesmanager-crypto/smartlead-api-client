import pandas as pd, json, re, datetime, os
st = json.load(open('run_state.json')); shows = st['shows']
P1 = pd.read_excel('phase2_domains_ALL.xlsx', sheet_name='All', dtype=str).fillna('')
B3 = pd.read_excel('phase3_brands_amazon_ALL.xlsx', sheet_name='Brands').fillna('')
R3 = pd.read_excel('phase3_brands_amazon_ALL.xlsx', sheet_name='Exhibitor Rollup').fillna('')
B4 = pd.read_excel('phase4_smartscout_ALL.xlsx', sheet_name='Brands')
R4 = pd.read_excel('phase4_smartscout_ALL.xlsx', sheet_name='Exhibitor Rollup')
slug = lambda s: re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')[:40]
lead4 = ['Monthly Revenue','Annual Revenue (TTM)','Dominant Seller','Dominant Seller Sales %','Dominant Seller Type','Top Subcategory 1','Sub 1 Market Share','Sub 1 Brand Rank',
         'Top Subcategory 2','Sub 2 Market Share','Sub 2 Brand Rank','Top Subcategory 3','Sub 3 Market Share','Sub 3 Brand Rank','Primary Category','Primary Subcategory','Total Products',
         'Total Reviews','Average Rating','Average Price','Seller Count','Reseller Share %','Amazon 1P %','MoM Growth','12-Month MoM Growth','Has Storefront','Storefront URL','Top 5 Sellers','Data Pulled At']
k4 = B4[['Exhibitor ID','Brand'] + lead4 + ['Notes']].rename(columns={'Notes': 'SmartScout Notes'})
BR = B3.merge(k4, on=['Exhibitor ID','Brand'], how='left')
BR['Notes'] = BR.apply(lambda r: '; '.join(dict.fromkeys(x for x in [str(r['Notes']), str(r['SmartScout Notes']) if pd.notna(r['SmartScout Notes']) else ''] if x and x != 'nan')), axis=1)
BR = BR.drop(columns=['SmartScout Notes'])
first = ['Exhibitor Name','Brand','On Amazon','Monthly Revenue','Annual Revenue (TTM)','Dominant Seller','Dominant Seller Sales %']
brand_cols = first + [c for c in BR.columns if c not in first]
ex_cols = ['Exhibitor ID','Exhibitor Name','Booth','Website','Domain','Domain Confidence','LinkedIn','LinkedIn (found by search)','Parent Company','Parent Domain','Parent Source','Exhibitor Type','Type Reason','Phase 3 Scope',
           'About Summary','Categories','City','State','Country','About','Detail URL','Source','List Status','Notes','Exhibitor Key','Show ID','Show Name']
summary, log = [], []
order = sorted(shows, key=lambda s: shows[s].get('dates', ''))  # S01..S20 are already in date order
for sid in sorted(shows):
    info = shows[sid]; name = info['name']
    ex = P1[P1['Show ID'] == sid]; real = ex[ex['Exhibitor Name'] != '']
    br = BR[BR['Show ID'] == sid].copy()
    br['_rev'] = pd.to_numeric(br['Monthly Revenue'], errors='coerce').fillna(-1)
    br = br.sort_values(['_rev', 'On Amazon', 'Exhibitor Name'], ascending=[False, True, True]).drop(columns=['_rev'])
    bb = br[br['Brand'] != '']
    yes = bb[bb['On Amazon'] == 'Yes']; pos = bb[bb['On Amazon'] == 'Possible']
    r4 = R4[R4['Show ID'] == sid]; r3 = R3[R3['Show ID'] == sid]
    combined = float(r4.drop_duplicates('Exhibitor ID')['Combined Monthly Revenue'].sum()) if len(r4) else 0.0
    researched = real[real['Phase 3 Scope'] == 'Research']
    targets = r3[r3['Any Brand On Amazon'].isin(['Yes', 'Possible'])]
    people = pd.DataFrame([{'Exhibitor ID': t['Exhibitor ID'], 'Exhibitor Name': t['Exhibitor Name'], 'Any Brand On Amazon': t['Any Brand On Amazon'], 'Company LinkedIn': P1.set_index('Exhibitor ID')['LinkedIn'].get(t['Exhibitor ID'], ''),
                            'Name': '', 'Title (as shown)': '', 'LinkedIn URL': '', 'Priority': '', 'Match Reason': '', 'Search Query': '', 'Confidence': 'unverified',
                            'Notes': 'Phase 5 not run in this session (web search cap reached); try Sales Navigator / Surfe or rerun phase 5'} for _, t in targets.iterrows()])
    fname = f'show_{sid}_{slug(name)}.xlsx'
    pend = int((bb['Amazon Confidence'] == 'Amazon check pending').sum())
    summ = pd.DataFrame([['Show', name], ['Show ID', sid], ['Dates', info['dates']], ['City', info['city']], ['Category', info['category']], ['Event Link', info['event_link']],
        ['List Status', info.get('list_status', '')], ['Exhibitor List URL', info.get('exhibitor_list_url', '')], ['Exhibitors Pulled', len(real)], ['Exhibitors Researched (phase 3)', len(researched)],
        ['Brands Found', bb['Brand'].str.lower().nunique()], ['Brands Selling on Amazon (Yes)', yes['Brand'].str.lower().nunique()], ['Brands Possible', pos['Brand'].str.lower().nunique()],
        ['Exhibitors with Amazon Brands', (r3['Any Brand On Amazon'] == 'Yes').sum()], ['Exhibitors Possible only', (r3['Any Brand On Amazon'] == 'Possible').sum()],
        ['Combined Monthly Amazon Revenue (SmartScout, sum over exhibitors)', round(combined, 2)], ['Brand rows pending amazon.com check', pend],
        ['Decision makers (phase 5)', 'not run in this session; People sheet lists the target exhibitors'], ['Built', datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')],
        ['Data notes', 'SmartScout Business plan, US only, no revenue history. Amazon check = SmartScout brand match with category fit; amazon.com direct check blocked from this environment. Domains for some exhibitors pending web search.']],
        columns=['Field', 'Value'])
    with pd.ExcelWriter(os.path.join('deliverables', fname), engine='openpyxl') as w:
        summ.to_excel(w, sheet_name='Summary', index=False)
        ex[[c for c in ex_cols if c in ex.columns]].to_excel(w, sheet_name='Exhibitors', index=False)
        br[brand_cols].to_excel(w, sheet_name='Brands', index=False)
        (people if len(people) else pd.DataFrame([{'Notes': 'No exhibitors with Amazon brands found; phase 5 not run'}])).to_excel(w, sheet_name='People', index=False)
    notes = []
    if info.get('list_status') != 'current list': notes.append(f"list status: {info.get('list_status')}")
    if sid == 'S01': notes.append('show renamed Greensboro Importers & Wholesalers Expo; event link 404; list is names only')
    if sid == 'S05': notes.append('only Dallas stop found; Atlanta and San Diego pages gone')
    if sid == 'S18': notes.append('no public exhibitor list; Cloudflare blocked; Map Your Show site empty')
    if pend: notes.append(f'{pend} brand rows await amazon.com check')
    dp = int((real['Notes'].str.contains('Domain search pending')).sum())
    if dp: notes.append(f'{dp} exhibitors await domain search')
    summary.append({'Show Name': name, 'Dates': info['dates'], 'Exhibitor List URL': info.get('exhibitor_list_url', ''), 'List Status': info.get('list_status', ''), 'Exhibitors Pulled': len(real),
        'Exhibitors Researched': len(researched), 'Brands Found': bb['Brand'].str.lower().nunique(), 'Brands Selling on Amazon': yes['Brand'].str.lower().nunique(),
        'Brands Possible': pos['Brand'].str.lower().nunique(), 'Exhibitors with Amazon Brands': int((r3['Any Brand On Amazon'] == 'Yes').sum()),
        'Combined Monthly Amazon Revenue': round(combined, 2), 'Brand File': fname, 'Drive Link': '', 'Notes': '; '.join(notes)})
S = pd.DataFrame(summary)
S.to_excel('deliverables/tradeshow_brand_summary.xlsx', index=False)
print(S[['Show Name','List Status','Exhibitors Pulled','Exhibitors Researched','Brands Found','Brands Selling on Amazon','Exhibitors with Amazon Brands','Combined Monthly Amazon Revenue']].to_string(index=False))

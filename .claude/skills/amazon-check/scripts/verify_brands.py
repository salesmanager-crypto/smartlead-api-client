#!/usr/bin/env python3
"""Verify brands on Amazon US: brand name as Amazon spells it, brand store URL, seller, evidence listing.

Input queue.json: [{key, company, link, ...}] (from build_queue.py). If link is a /dp/ or /stores/ URL it is used first;
otherwise the brand is searched. Every page loads in a fresh browser context (long-lived sessions get throttled).
Output out.json is written after every brand and the run is resumable: re-run with the same files to continue.

Usage: verify_brands.py queue.json out.json [--workers 2]
Then review: entries with name_match=False, or whose evidence title does not fit the company's line of business, are
wrong more often than right. Never write a brand you have not read against the product title.
"""
import sys,asyncio,json,os,re,urllib.parse
from playwright.async_api import async_playwright
import random
UAS=['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36']
PJS='''() => {let b=document.querySelector('#bylineInfo');
 let fb='';
 if(!b||!b.innerText.trim()){ const row=[...document.querySelectorAll('#productOverview_feature_div tr, #productDetails_techSpec_section_1 tr, #detailBullets_feature_div li')].find(r=>/^\s*Brand\b/i.test(r.innerText)); if(row){const td=row.querySelector('td, span:last-child'); fb='Brand: '+(td?td.innerText:row.innerText.replace(/^\s*Brand\s*:?/i,'')).trim();} }
 const byline=b&&b.innerText.trim()?b.innerText:fb;
 const s=document.querySelector('#sellerProfileTriggerId')||document.querySelector('[offer-display-feature-name="desktop-merchant-info"] .offer-display-feature-text')||document.querySelector('#merchantInfo, #merchant-info');
 return {title:(document.querySelector('#productTitle')||{}).innerText||'', byline:byline, byline_href:(b&&b.href)?b.href.split('?')[0].split('/ref=')[0]:'', sold_by:s?s.innerText.replace(/\\s+/g,' ').trim().slice(0,120):'', captcha:!!document.querySelector('form[action*="validateCaptcha"]'), dog:/Sorry! Something went wrong|Looking for something\\?|Page Not Found/i.test(document.body.innerText.slice(0,3000))}}'''
SJS='''() => {const items=[...document.querySelectorAll('div[data-component-type="s-search-result"]')].slice(0,12).map(d=>({asin:d.dataset.asin,title:((d.querySelector('[data-cy="title-recipe"]')||d.querySelector('h2')||{}).innerText||'').replace(/\\n/g,' | ').slice(0,160),sponsored:/Sponsored/.test(d.innerText.slice(0,200))}));
 return {items,captcha:!!document.querySelector('form[action*="validateCaptcha"]'),noresults:/No results for/.test(document.body.innerText)}}'''
STJS='''() => {const links=[...new Set([...document.querySelectorAll('a[href*="/dp/"]')].map(a=>(a.href.match(/\\/dp\\/([A-Z0-9]{10})/)||[])[1]).filter(Boolean))].slice(0,5);
 const h=document.querySelector('h1, [data-testid="store-name"], .store-name, meta[property="og:title"]');
 return {title:document.title, h1:h?(h.innerText||h.content||''):'', asins:links, captcha:!!document.querySelector('form[action*="validateCaptcha"]'), dog:/Sorry! Something went wrong|Looking for something\\?|Page Not Found/i.test(document.body.innerText.slice(0,3000))}}'''
def norm(s): return re.sub(r'[^a-z0-9]','',(s or '').lower())
def bname(by):
    by=(by or '').strip(); m=re.match(r'Visit the (.*) Store$',by,re.S)
    if m: return m.group(1).strip()
    if by.startswith('Brand:'): return by[6:].strip()
    return ''
async def load(b,url,js,wait_sel=None):
    ctx=await b.new_context(user_agent=random.choice(UAS),locale='en-US',viewport={'width':random.choice([1280,1366,1440,1536]),'height':random.choice([720,768,900])})
    await ctx.route('**/*',lambda r: r.abort() if r.request.resource_type in ('image','media','font') else r.continue_())
    pg=await ctx.new_page()
    try:
        resp=await pg.goto(url,timeout=45000,wait_until='domcontentloaded')
        if wait_sel:
            try: await pg.wait_for_selector(wait_sel,timeout=10000)
            except Exception: pass
        await pg.wait_for_timeout(2000)
        d=await pg.evaluate(js); d['status']=resp.status if resp else None; d['final_url']=pg.url
    except Exception as e: d={'error':str(e)[:150]}
    await ctx.close(); await asyncio.sleep(3)
    return d
async def dp(b,asin):
    for a in range(3):
        d=await load(b,'https://www.amazon.com/dp/'+asin,PJS,'#productTitle')
        if d.get('title') or d.get('dog'): break
        await asyncio.sleep(4*(a+1))
    d['url']='https://www.amazon.com/dp/'+asin; return d
def keys_for(company,key):
    ws_=[w for w in re.split(r'[^A-Za-z0-9]+',company) if len(w)>=3 and w.lower() not in ('inc','llc','the','and','co','ltd','corp','group','brands','brand','company','international','usa','designs','design','apparel','clothing','wholesale','products','sales','swimwear','swim','wear','com')]
    ks={norm(company)[:5],norm(key.split('.')[0])[:5]}|{norm(w)[:5] for w in ws_[:3]}
    return {k for k in ks if len(k)>=3}
def matches(name,ks): 
    n=norm(name); return bool(n) and any(k in n for k in ks)
async def search_pick(b,q,ks):
    for a in range(3):
        d=await load(b,'https://www.amazon.com/s?k='+urllib.parse.quote_plus(q),SJS,'div[data-component-type="s-search-result"]')
        if d.get('items') or d.get('noresults'): break
        await asyncio.sleep(6*(a+1))
    items=d.get('items',[])
    cand=[i for i in items if matches(i['title'].split('|')[0],ks)] or [i for i in items if matches(i['title'],ks)]
    return cand[:2], items
async def work(b,item):
    key,comp,link=item['key'],item['company'],item['link']
    ks=keys_for(comp,key); out={'key':key,'company':comp,'link':link,'steps':[]}
    def rec(d,how): out['steps'].append({'how':how,**{k:d.get(k) for k in ('url','title','byline','byline_href','sold_by','status','dog','error','captcha')}})
    found=None
    m=re.search(r'/dp/([A-Z0-9]{10})',link or '')
    if m:
        d=await dp(b,m.group(1)); rec(d,'link_dp')
        if bname(d.get('byline')): found=d
    elif link and '/stores/' in link:
        st=await load(b,link,STJS); out['store_page']={k:st.get(k) for k in ('title','h1','status','dog','error','asins','final_url')}
        for asin in (st.get('asins') or [])[:2]:
            d=await dp(b,asin); rec(d,'store_dp')
            if bname(d.get('byline')) and matches(bname(d['byline']),ks|{norm(st.get('h1') or '')[:5]}-{''}): found=d; break
            if bname(d.get('byline')) and not found: found=d  # keep first as fallback
        if found and not found.get('byline_href'): found['byline_href']=link.split('?')[0].split('/ref=')[0]
    elif link:
        d=await load(b,link,SJS,'div[data-component-type="s-search-result"]'); items=d.get('items',[])
        cand=[i for i in items if matches(i['title'].split('|')[0],ks)][:2]
        for i in cand:
            dd=await dp(b,i['asin']); rec(dd,'link_search_dp')
            if bname(dd.get('byline')): found=dd; break
    if not found:
        cand,items=await search_pick(b,comp or key.split('.')[0],ks); out['search_titles']=[i['title'][:80] for i in items[:6]]
        for i in cand:
            dd=await dp(b,i['asin']); rec(dd,'search_dp')
            if bname(dd.get('byline')) and matches(bname(dd['byline']),ks): found=dd; break
        if not found and cand: pass
    if found:
        out['brand']=bname(found['byline']); out['store_url']=found.get('byline_href') if '/stores/' in (found.get('byline_href') or '') else ''
        out['evidence']=found.get('url'); out['sold_by']=found.get('sold_by'); out['name_match']=matches(out['brand'],ks)
    print(key,'=>',out.get('brand'),'|',out.get('store_url','')[:50],flush=True)
    return out
async def main(inp,outp,n=2):
    items=json.load(open(inp)); done=json.load(open(outp)) if os.path.exists(outp) else {}
    queue=[i for i in items if i['key'] not in done]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium',args=['--no-sandbox'],proxy={'server':os.environ['HTTPS_PROXY']})
        async def worker():
            while queue:
                it=queue.pop(0)
                try: done[it['key']]=await work(b,it)
                except Exception as e: done[it['key']]={'key':it['key'],'error':str(e)[:200]}; print('ERR',it['key'],e,flush=True)
                json.dump(done,open(outp,'w'),indent=1,ensure_ascii=False)
        await asyncio.gather(*[worker() for _ in range(n)])
        await b.close()
    print('done',len(done))
if __name__=='__main__':
    args=[x for x in sys.argv[1:] if not x.startswith('--')]
    n=int(sys.argv[sys.argv.index('--workers')+1]) if '--workers' in sys.argv else 2
    asyncio.run(main(args[0],args[1],n))

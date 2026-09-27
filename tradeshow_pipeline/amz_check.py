"""Phase 3 step 2b: amazon.com check for brands not found in SmartScout.
Input phase3_work/amz_queue.csv (Brand, Variants). Output phase3_work/amz_results.jsonl (append, resumable).
One browser, one request at a time, 3-5 s between requests. Captcha -> pause 10 min, retry once, else mark pending."""
import asyncio, sys, re, json, os, random, time, hashlib
import pandas as pd
from playwright.async_api import async_playwright
sys.path.insert(0, '.')
from browser import LAUNCH, UA
OUT = 'phase3_work/amz_results.jsonl'; CACHE = 'cache/amazon'; os.makedirs(CACHE, exist_ok=True)
def nz(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower().replace('&', 'and'))
async def polite(): await asyncio.sleep(random.uniform(4, 7))
async def get(pg, url):
    for attempt in range(2):
        await pg.goto(url, timeout=60000); await pg.wait_for_timeout(1500)
        html = await pg.content(); t = await pg.title()
        blocked = ('validatecaptcha' in html.lower() or 'enter the characters you see below' in html.lower() or 'robot check' in t.lower()
                   or ('something went wrong' in html.lower() and 'dogsofamazon' in html.lower()) or len(html) < 3000)
        if blocked:
            open(os.path.join(CACHE, 'blocked_%d.html' % int(time.time())), 'w').write(html)
            print('captcha/block on', url, '(title: %s) -> pause 600s' % t, flush=True); await asyncio.sleep(600); continue
        open(os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + '.html'), 'w').write(html)
        return html
    return None
async def check(pg, brand, variants):
    rec = {'Brand': brand, 'checked_at': time.strftime('%Y-%m-%dT%H:%M:%S')}
    for q in [brand] + [v for v in variants if v][:2]:
        url = 'https://www.amazon.com/s?k=' + re.sub(r'\s+', '+', q.strip())
        html = await get(pg, url); await polite()
        if html is None: rec['status'] = 'Amazon check pending'; return rec
        res = await pg.eval_on_selector_all('div[data-component-type="s-search-result"]', '''els=>els.slice(0,10).map(e=>({asin:e.dataset.asin, h2:[...e.querySelectorAll("h2")].map(h=>h.innerText.trim())}))''')
        facet = await pg.eval_on_selector_all('#brandsRefinements li, div[id*="p_123"] li, div[id*="p_89"] li', 'els=>els.map(e=>e.innerText.trim()).filter(Boolean)')
        n = nz(q)
        in_facet = any(nz(f) == n for f in facet)
        cand = [r for r in res if r['asin'] and any(nz(h) == n or nz(h).startswith(n) for h in r['h2'])]
        rec.update({'query': q, 'search_url': url, 'in_brand_filter': in_facet, 'title_matches': len(cand), 'results': len(res)})
        if not cand and not in_facet: continue
        if cand:
            purl = 'https://www.amazon.com/dp/' + cand[0]['asin']
            ph = await get(pg, purl); await polite()
            if ph:
                g = lambda sel: pg.eval_on_selector(sel, 'e=>e.innerText.trim()') if True else None
                async def txt(sel):
                    try: return await pg.eval_on_selector(sel, 'e=>e.innerText.trim()')
                    except Exception: return ''
                rec.update({'Amazon URL': purl, 'byline': await txt('#bylineInfo'), 'title': (await txt('#productTitle'))[:200],
                            'breadcrumbs': re.sub(r'\s+', ' ', await txt('#wayfinding-breadcrumbs_feature_div'))[:200],
                            'merchant': re.sub(r'\s+', ' ', (await txt('#merchantInfoFeature_feature_div')) or (await txt('#sellerProfileTriggerId')) or (await txt('#tabular-buybox')))[:200]})
                rec['byline_match'] = n in nz(rec['byline'])
        else:
            rec['Amazon URL'] = url
        rec['status'] = 'hit'
        return rec
    rec['status'] = rec.get('status', 'not found')
    return rec
async def main():
    q = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else 'phase3_work/amz_queue.csv', dtype=str).fillna('')
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            r = json.loads(l)
            if r.get('status') != 'Amazon check pending': done.add(r['Brand'])
    todo = q[~q['Brand'].isin(done)]
    print('queue', len(q), 'todo', len(todo), flush=True)
    async with async_playwright() as p:
        async def fresh():
            b = await p.chromium.launch(headless=False, **LAUNCH)
            ctx = await b.new_context(user_agent=UA, viewport={'width': 1400, 'height': 1000}, locale='en-US')
            pg = await ctx.new_page(); await pg.goto('https://www.amazon.com/', timeout=60000); await asyncio.sleep(random.uniform(4, 6))
            return b, ctx, pg
        b, ctx, pg = await fresh()
        for i, r in enumerate(todo.itertuples()):
            try: rec = await check(pg, r.Brand, [v.strip() for v in r.Variants.split(';')])
            except Exception as e: rec = {'Brand': r.Brand, 'status': 'Amazon check pending', 'error': str(e)[:200]}
            with open(OUT, 'a') as f: f.write(json.dumps(rec) + '\n')
            if rec.get('status') == 'Amazon check pending':
                print('still blocked after 10 min pause; stopping run so it can resume later', flush=True); break
            if (i + 1) % 50 == 0: print(f'phase 3 amazon: {i+1} of {len(todo)}', flush=True)
            if (i + 1) % 300 == 0:
                await b.close(); b, ctx, pg = await fresh()
        await b.close()
    print('DONE', flush=True)
asyncio.run(main())

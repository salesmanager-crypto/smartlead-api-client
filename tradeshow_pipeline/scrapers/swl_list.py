import sys, asyncio, re, os, json, random, urllib.parse
sys.path.insert(0, '/home/user/smartlead-api-client/tradeshow_pipeline')
from playwright.async_api import async_playwright
from browser import new_browser
SID, HOST = sys.argv[1], sys.argv[2]
CD = f'/home/user/smartlead-api-client/tradeshow_pipeline/cache/pages/{SID}'; os.makedirs(CD, exist_ok=True)
async def main():
    url = f'https://{HOST}/exhibitors'
    async with async_playwright() as p:
        b, ctx = await new_browser(p); page = await ctx.new_page()
        reqs = []
        page.on('request', lambda r: reqs.append(r.post_data) if r.method == 'POST' and 'index.php' in r.url else None)
        await page.goto(url, wait_until='domcontentloaded'); await page.wait_for_timeout(5000)
        html0 = await page.content(); open(f'{CD}/list_0.html', 'w').write(html0)
        loc = page.locator('.pagination a, .pagination button, [class*=paginat] a').filter(has_text=re.compile('Next|^2$'))
        if not await loc.count(): print('no pagination'); await b.close(); return
        await loc.first.click(); await page.wait_for_timeout(5000)
        pd = dict(urllib.parse.parse_qsl(reqs[0])); print(pd)
        seen = set(re.findall(r'href="(/co/[^"]+)"', html0)); print('page0', len(seen))
        off = int(pd['limit'])
        while True:
            pd['offset'] = str(off)
            body = urllib.parse.urlencode(pd)
            await asyncio.sleep(random.uniform(1.0, 2.0))
            t = await page.evaluate("""async (body)=>{const r=await fetch('/index.php',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','X-Requested-With':'XMLHttpRequest'},body}); return r.text();}""", body)
            open(f'{CD}/list_{off}.html', 'w').write(t)
            try:
                j = json.loads(t); t2 = urllib.parse.unquote(j.get('data') or '')
                if j.get('formToken'): pd['tk'] = j['formToken']; pd['tm'] = j['formTime']
                print('total', j.get('total'))
            except Exception as e: print('json err', e); t2 = t
            links = set(re.findall(r'href="(/co/[^"]+)"', t2))
            new = links - seen; print('offset', off, len(links), 'new', len(new), len(t))
            if not new: break
            seen |= links; off += int(pd['limit'])
        print('TOTAL', len(seen))
        await b.close()
asyncio.run(main())

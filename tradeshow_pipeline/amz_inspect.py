import asyncio, sys
sys.path.insert(0,'.')
from playwright.async_api import async_playwright
from browser import new_browser
async def m():
    async with async_playwright() as p:
        b, ctx = await new_browser(p); pg = await ctx.new_page()
        await pg.goto('https://www.amazon.com/dp/B0042LB778', timeout=60000); await pg.wait_for_timeout(2000)
        h = await pg.content(); print(await pg.title()); low = h.lower()
        i = low.find('captcha'); print('captcha idx', i, repr(h[max(0,i-150):i+80]) if i>=0 else '')
        print('robot' in low[:20000], 'something went wrong' in low[:5000])
        for s in ['#bylineInfo','#productTitle','#merchantInfoFeature_feature_div','#wayfinding-breadcrumbs_feature_div']:
            try: print(s, (await pg.eval_on_selector(s,'e=>e.innerText.trim()'))[:120].replace('\n',' '))
            except Exception as e: print(s, 'none')
        await b.close()
asyncio.run(m())

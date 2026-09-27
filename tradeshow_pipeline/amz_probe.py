import asyncio, sys, re, json
from playwright.async_api import async_playwright
sys.path.insert(0, '.')
from browser import new_browser
async def m(brands):
    async with async_playwright() as p:
        b, ctx = await new_browser(p); pg = await ctx.new_page()
        for br in brands:
            await pg.goto('https://www.amazon.com/s?k=' + br.replace(' ', '+'), timeout=60000); await pg.wait_for_timeout(2500)
            res = await pg.eval_on_selector_all('div[data-component-type="s-search-result"]', '''els=>els.slice(0,8).map(e=>({asin:e.dataset.asin, title:(e.querySelector("h2")||{}).innerText, brandline:(e.querySelector("h2")&&e.querySelector("h2").previousElementSibling||{}).innerText||"", sub:(e.querySelector(".a-row.a-size-base.a-color-secondary")||{}).innerText||""}))''')
            facet = await pg.eval_on_selector_all('#brandsRefinements li, div[id*="p_123"] li, div[id*="p_89"] li', 'els=>els.map(e=>e.innerText.trim()).filter(Boolean).slice(0,15)')
            print(br, 'facet:', facet); [print('  ', r) for r in res[:5]]
            await asyncio.sleep(4)
        await b.close()
asyncio.run(m(sys.argv[1:]))

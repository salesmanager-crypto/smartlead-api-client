import asyncio, sys
sys.path.insert(0,'/home/user/smartlead-api-client/tradeshow_pipeline')
from browser import new_browser
from playwright.async_api import async_playwright
async def main(url):
    async with async_playwright() as p:
        b, ctx = await new_browser(p); page = await ctx.new_page()
        r = await page.goto(url, wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(3000)
        h = await page.content(); print(r.status, len(h), h.count('section-heading'))
        print((await page.inner_text('body'))[:800])
        await b.close()
asyncio.run(main(sys.argv[1]))

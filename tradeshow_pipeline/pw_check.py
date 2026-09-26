import asyncio, sys
from playwright.async_api import async_playwright
async def main(urls):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--no-sandbox','--ignore-certificate-errors-spki-list='+open('/home/user/smartlead-api-client/tradeshow_pipeline/.proxy_spki').read().strip()])
        ctx = await b.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36', ignore_https_errors=False)
        for u in urls:
            pg = await ctx.new_page()
            try:
                r = await pg.goto(u, timeout=60000, wait_until='domcontentloaded')
                await pg.wait_for_timeout(8000)
                print(u, r.status if r else None, await pg.title())
                links = await pg.eval_on_selector_all('a', 'els=>els.map(e=>[e.innerText.trim().slice(0,40), e.href]).filter(x=>/exhib|vendor|floor|brand|directory|artist/i.test(x.join(" ")))')
                for l in links[:25]: print('   ', l)
            except Exception as e: print(u, 'ERR', e)
            await pg.close()
        await b.close()
asyncio.run(main(sys.argv[1:]))

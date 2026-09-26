import asyncio, sys, json, os, random
sys.path.insert(0,'/home/user/smartlead-api-client/tradeshow_pipeline'); os.chdir('/home/user/smartlead-api-client/tradeshow_pipeline')
from common import fetch
from browser import new_browser
from playwright.async_api import async_playwright
G='https://cofdfw1026.mapyourshow.com/8_0/ajax/remote-proxy.cfm?action=search&searchtype=exhibitorgallery&searchsize=500'
hits=json.loads(fetch(G, headers={'X-Requested-With':'XMLHttpRequest','Referer':'https://cofdfw1026.mapyourshow.com/8_0/explore/exhibitor-gallery.cfm?featured=false'}))['DATA']['results']['exhibitor']['hit']
json.dump(hits, open('cache/pages/S09/gallery_hits.json','w'))
print('hits', len(hits), flush=True)
os.makedirs('cache/pages/S09/details', exist_ok=True)
async def main():
    async with async_playwright() as p:
        b, ctx = await new_browser(p); page = await ctx.new_page()
        for i,h in enumerate(hits):
            exhid = h['fields']['exhid_l']
            fp = f'cache/pages/S09/details/{exhid}.html'
            if os.path.exists(fp) and os.path.getsize(fp) > 5000: continue
            url = f'https://cofdfw1026.mapyourshow.com/8_0/exhibitor/exhibitor-details.cfm?exhid={exhid}'
            for attempt in range(3):
                try:
                    await page.goto(url, wait_until='networkidle', timeout=60000)
                    await page.wait_for_timeout(2500)
                    await page.wait_for_timeout(800)
                    html = await page.content()
                    if 'section-heading' in html or ('Booths' in html and 'Exhibitor List' in html):
                        open(fp,'w').write(html); break
                except Exception as e:
                    print('err', exhid, e, flush=True); await page.wait_for_timeout(5000*(attempt+1))
            if i % 10 == 0: print(i, h['fields']['exhname_t'], flush=True)
            await page.wait_for_timeout(random.uniform(1000,2000))
        await b.close()
asyncio.run(main())
print('DONE', flush=True)

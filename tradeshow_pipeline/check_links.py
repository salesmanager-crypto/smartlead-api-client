from common import fetch
import sys
links = {
'S01':'https://www.gtshows.com/greensboro-gift-jewelry-show-2/','S02':'https://www.whitelabelexpo.com/','S03':'https://lvsouvenirshow.com',
'S04':'http://www.newyorkcomiccon.com/','S05':'https://www.electrifyexpo.com','S06':'https://premierecolumbusshow.biz','S07':'http://nasgwexpo.org/',
'S08':'https://www.jisshow.com/fall/en-us.html','S09':'https://www.coffeefest.com/dallas-fortworth/attend','S10':'https://www.highpointmarket.org/',
'S11':'https://ja-newyork.com','S12':'https://www.iges.us','S13':'https://www.demashow.com/','S14':'https://www.smokymtngiftshow.com',
'S15':'https://snowboundexpo.com','S16':'https://www.oceancitygiftshow.com','S17':'https://www.therunningevent.com/','S18':'https://animefrontier.com',
'S19':'https://www.grandstrandgiftshow.com/welcome','S20':'https://www.performanceracing.com/tradeshow/'}
import requests
from common import S
for k,u in links.items():
    try:
        r = S.get(u, timeout=30)
        import re
        t = re.search(r'<title[^>]*>(.*?)</title>', r.text, re.S|re.I)
        print(k, r.status_code, r.url, '|', (t.group(1).strip()[:70] if t else ''))
    except Exception as e:
        print(k, 'ERR', str(e)[:100])

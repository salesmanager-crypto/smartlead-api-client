# Setup and lessons (Surf Expo 2026 run, Sept 2026)

## Browser through the session proxy

Amazon returns 503 to curl and to WebFetch. Headless Chromium works, but only after it trusts the proxy CA:

```
apt-get install -y libnss3-tools
certutil -A -d sql:$HOME/.pki/nssdb -n ccr-agent-proxy -t "C,," -i /root/.ccr/agent-proxy-ca.crt
pip install playwright openpyxl
```

Chromium lives at `/opt/pw-browsers/chromium` (do not run `playwright install`). Pass `proxy={'server': os.environ['HTTPS_PROXY']}` to `chromium.launch`; the port changes when the container restarts, so never hard-code it (a run once died on `ERR_PROXY_CONNECTION_FAILED` because of that).

## What made the scrape reliable

- A **fresh browser context per page load**. Long-lived sessions got throttled after ~15 pages: search pages came back with zero results and no captcha.
- **Product pages opened in the same context as the search page came back blank**; opening them in their own context fixed it.
- Byline fallback: some Amazon-sold listings (Cressi, vineyard vines) have no `#bylineInfo`; read the "Brand" row from the product overview table, or fall back to the brand label Amazon prints in search results.
- Dead store links are common. Several `/stores/...` URLs redirected to an unrelated Duracell page. A store page whose products carry a different brand is a dead link, not a rename.
- Backoffs: 4/8/12 s on blank product pages, 6/12 s on empty search. The original 15/30/45 and 20/40/60 s backoffs quietly added ~2 minutes per throttled brand.

## Throughput measured

| concurrent workers | brands/min | blank-page rate | verdict |
|---|---|---|---|
| 2 | ~2.5 | ~0 | safe, slow |
| 4 | ~4 | low | fine |
| 8 | ~4.5 | ~15% | the practical cap |
| 32 | ~11 | ~75% | useless; 23 of 29 results empty |

About 3 page loads per brand on average (store page + 1-2 product pages; fallback search for ~half).

## Other sources

- **SmartScout MCP**: Business plan, $50/month AI allowance; it was already spent before the run and every query was refused. Product history capped at 30 days; no Ad Spy / SoV / brand revenue history / non-US on that plan.
- **WebSearch**: hard cap of 200 calls per session (`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`). Ten parallel agents burned it in minutes.
- **Bing via curl**: mostly junk results (first word only, unrelated pages). Google via curl: blocked.

## Review rules that caught wrong names

Every accepted name was wrong at least once when matched on a prefix: Haggard Pirate -> THE PIRATE KING, Lizton Sign Shop -> SmartSign, Tribal -> Tribal Chimp, 7 Diamonds -> a playing-card costume, JMP Fashions -> a random "JMP" t-shirt, L2 Brands -> LEGACY RECORDINGS. Read the product title against the company's line of business before accepting. When in doubt: NOT FOUND, and list it for Yoni.

Accepted spellings that differ from the company and were right: DRGINGER'S -> Doctor Ginger's, speargun.com -> Riffe, Toyosity -> Surfer Dudes, World Famous Sports -> WFS, Florida Glow -> Florida Salt Scrubs, Anchor Works -> ANCHORWORKS.COOL.

## Process hygiene

`pkill -f <pattern>` matches the calling shell's own command line and kills it (exit 144). Kill by PID from `ps -eo pid,args | grep ... | grep -v grep`. Stop every watcher when its run is replaced; Yoni saw four stale wait loops as "4 running tasks".

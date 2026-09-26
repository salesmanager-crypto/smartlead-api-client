"""Shared Playwright helper. Chromium is preinstalled; TLS goes through the session proxy (pinned by SPKI)."""
import os, json, hashlib, asyncio
from playwright.async_api import async_playwright
BASE = os.path.dirname(os.path.abspath(__file__))
SPKI = open(os.path.join(BASE, '.proxy_spki')).read().strip()
LAUNCH = dict(executable_path='/opt/pw-browsers/chromium',
              args=['--no-sandbox', '--ignore-certificate-errors-spki-list=' + SPKI, '--disable-blink-features=AutomationControlled'])
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36'
async def new_browser(p):
    b = await p.chromium.launch(**LAUNCH)
    ctx = await b.new_context(user_agent=UA, viewport={'width': 1400, 'height': 1000}, locale='en-US')
    return b, ctx
# usage:
#   async with async_playwright() as p:
#       b, ctx = await new_browser(p); page = await ctx.new_page()
#       page.on('response', handler)  # capture JSON

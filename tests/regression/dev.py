import asyncio, sys
import os as _os, tempfile as _tf
_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')   # QA F3
from playwright.async_api import async_playwright
from helpers import *
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1500,'height':1000}); pg=await ctx.new_page()
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(500)
        await import_files(pg,['NFPA318-Fab-Ceiling.pl','Example Project.pl']); await fill_addresses(pg)
        for lv in ['summary','standard','full']:
            html=await pg.evaluate(f"v2BuildPrintHtml({{level:'{lv}'}})"); open(_OUT+f'/p-{lv}.html','w').write(html)
            print(lv, await render_pdf(b, html, _OUT+f'/p-{lv}.pdf'))
        await pg.screenshot(path=_OUT+'/v2.png'); print(errs)
asyncio.run(main())

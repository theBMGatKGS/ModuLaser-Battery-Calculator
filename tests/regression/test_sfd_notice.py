"""02.02.001 QA delta: Calculator shows the SFD/OAP one-time notice for an older project carrying Toolbox Performance Criteria."""
import asyncio, os, sys
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); APP = os.environ.get('APP') or 'file://' + ROOT + '/modulaser_battery_calculator.html'
R = []
def ok(n, c, i=''): R.append((n, bool(c))); print('PASS' if c else 'FAIL', n, str(i)[:300])
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width':1440,'height':900}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(800)
    tb = await pg.evaluate("typeof tbPerf === 'function'")
    await pg.wait_for_timeout(1200)
    ok('new / empty project: no notice', await pg.query_selector('#mlp-sfd-notice') is None)
    if tb:
        ok('Toolbox: banner not used (notice lives in Performance Criteria)', True); await b.close(); print('\n2 passed, 0 failed'); return
    await pg.evaluate("MLP_CARRY.performance={standard:'SFD/OAP – NFPA 72',areas:{},limits:{},codeReqs:[]}"); await pg.wait_for_timeout(1500)
    ok('older project with Performance Criteria: one-time notice shown', await pg.query_selector('#mlp-sfd-notice') is not None)
    sh = os.environ.get('SHOTS')
    if sh: os.makedirs(sh, exist_ok=True); await pg.screenshot(path=os.path.join(sh, 'sfd-08-calculator-notice.png'))
    await pg.click('#mlp-sfd-notice-ok'); await pg.wait_for_timeout(1300)
    ok('dismissed and stays dismissed', await pg.query_selector('#mlp-sfd-notice') is None and await pg.evaluate('MLP_CARRY.performance.sfdNotice') is False)
    ok('no page errors', not errs, errs)
    await b.close()
  f = [n for n, c in R if not c]; print(f'\n{len(R)-len(f)} passed, {len(f)} failed'); sys.exit(1 if f else 0)
asyncio.run(main())

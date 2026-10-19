"""02.02.000 (Brent 10-19 12:35 PM CT): View menu shows a check on Project Settings bar / Sheet sidebar / Results panel when on,
synced from menu, quick-row buttons, close button and restored state. Run: python3 tests/regression/test_view_checks.py (APP=<file url> for the Toolbox)"""
import asyncio, os
from playwright.async_api import async_playwright
APP = os.environ.get('APP', 'file://' + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'modulaser_battery_calculator.html')))
R = []
def ok(n, c, i=''): R.append(bool(c)); print('PASS' if c else 'FAIL', n, str(i)[:200])
ST = """()=>{ const g=id=>document.getElementById(id).getAttribute('aria-checked'); const B=document.body.classList;
  return { s:g('view-settings-btn'), sb:g('view-sidebar-btn'), rp:g('view-results-btn'),
    sOpen:String(!document.getElementById('proj-settings').classList.contains('collapsed')), sbOpen:String(!B.contains('sidebar-closed')), rpOpen:String(!B.contains('results-closed')),
    role:document.getElementById('view-results-btn').getAttribute('role'), vis:getComputedStyle(document.getElementById('view-results-btn'),'::before').visibility }; }"""
def synced(x): return x['s']==x['sOpen'] and x['sb']==x['sbOpen'] and x['rp']==x['rpOpen']
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width':1400,'height':900}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(700)
    x = await pg.evaluate(ST); ok('defaults: all three checked, menuitemcheckbox', x['s']==x['sb']==x['rp']=='true' and x['role']=='menuitemcheckbox' and x['vis']=='visible', x)
    await pg.click('#menu-view-btn'); await pg.click('#view-results-btn'); x = await pg.evaluate(ST)
    ok('menu toggles results off -> unchecked, check hidden', x['rp']=='false' and synced(x) and x['vis']=='hidden', x)
    await pg.click('#rp-toggle-btn'); x = await pg.evaluate(ST); ok('quick-row button back on -> checked', x['rp']=='true' and synced(x), x)
    await pg.click('#rp-close-btn'); x = await pg.evaluate(ST); ok('panel close button -> unchecked', x['rp']=='false' and synced(x), x)
    await pg.click('#menu-view-btn'); await pg.click('#view-sidebar-btn'); x = await pg.evaluate(ST); ok('menu sidebar off -> unchecked', x['sb']=='false' and synced(x), x)
    await pg.evaluate("document.getElementById('sb-toggle-btn') && document.getElementById('sb-toggle-btn').click()"); x = await pg.evaluate(ST); ok('sidebar toggle button -> synced', synced(x), x)
    await pg.click('#menu-view-btn'); await pg.click('#view-settings-btn'); x = await pg.evaluate(ST); ok('menu settings collapse -> unchecked', x['s']=='false' and synced(x), x)
    await pg.click('#proj-settings-toggle'); x = await pg.evaluate(ST); ok('settings bar own toggle -> checked', x['s']=='true' and synced(x), x)
    await pg.click('#proj-settings-toggle'); await pg.evaluate("v2SetPanel('sidebar', false)")
    await pg.reload(); await pg.wait_for_timeout(700); x = await pg.evaluate(ST)
    ok('restored on load: settings + results + sidebar off -> unchecked', x['s']=='false' and x['rp']=='false' and x['sb']=='false' and synced(x), x)
    ok('no page errors', not errs, errs); await b.close()
  print(f"{sum(R)}/{len(R)} passed"); raise SystemExit(0 if all(R) else 1)
asyncio.run(main())

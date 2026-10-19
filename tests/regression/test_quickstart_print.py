"""02.02.000: Help screenshots (headless, example data, dark UI) + Help ▸ Print Quick Start (standalone 2-page, KGS print palette, no Help chrome)."""
import asyncio, os, sys, re
from playwright.async_api import async_playwright
APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:300])
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1440,'height':1000}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(800)
    TB='Toolbox' in APP
    ok('Help menu has Print Quick Start', await pg.evaluate("!!document.querySelector('[aria-labelledby=menu-help-btn] #qs-print-btn') && document.getElementById('qs-print-btn').textContent==='Print Quick Start'"))
    if TB:
      qh=open(os.path.join(os.path.dirname(APP.replace('file://','')),'quickstart.html')).read()
      ok('Toolbox quickstart.html: 02.02.000 screenshots, 00.03.000, new AUX/ribbon rule', qh.count('data-shot="02.02.000"')>=2 and '00.03.000' in qh and '4 detectors + 1 display per ribbon run' in qh)
      ok('Toolbox in-app Quick Start has the screenshots', await pg.evaluate("document.querySelectorAll('#help-tb-quickstart img.tbq-shot').length")>=2)
    if not TB:
      shots=await pg.evaluate("[...document.querySelectorAll('img[data-qs-slot]')].filter(i=>(i.getAttribute('src')||'').startsWith('data:image/jpeg')).map(i=>i.dataset.qsSlot)")
      ok('Help screenshots embedded: all 15 slots incl. View menu, ribbon rule, 9 arrangements, 11 Confirm defaults, 13 Import Calc', len(shots)==15 and all(k in shots for k in ['view-menu','ribbon-rule','9-arrangements','11-confirm-defaults','13-import-calc']), shots)
      ok('no legacy wireframe left in Help', await pg.evaluate("document.querySelectorAll('.qs-figure-wire, .qs-figure-placeholder').length")==0)
      ok('screenshots tagged 02.02.000 with example-data caption', await pg.evaluate("[...document.querySelectorAll('img[data-shot]')].every(i=>i.dataset.shot==='02.02.000' && /Example data/.test(i.nextElementSibling.textContent))"))
      ok('FAQ no longer says 2-segment/4-follower', await pg.evaluate("!document.body.innerHTML.includes('2-segment/4-follower')"))
      ok('How Do I has brand, ASD-160, Print Quick Start', await pg.evaluate("['brand','asd160','print-quickstart'].every(id=>HOWDOI_COMMON.some(h=>h.id===id))"))
    html=await pg.evaluate("qsQuickStartHtml()")
    ok('Quick Start: 2 pages', html.count('<div class="page">')==2, html.count('<div class="page">'))
    NS=5 if TB else 10
    ok(f'Quick Start: {NS} numbered steps', len(re.findall(r'<span class="n">\d+</span>',html))==NS)
    if TB: ok('Toolbox Quick Start: Toolbox title + screenshots', 'MASD Engineering Toolbox — Quick Start' in html and html.count('<img src="data:image/jpeg')>=2, html.count('<img src="data:image/jpeg'))
    ok('Quick Start: KGS print palette', '#102645' in html and '#0c77bc' in html and '@page{size:letter' in html)
    ok('Quick Start: no Help chrome', not any(x in html for x in ['help-overlay','menubar','help-nav','howdoi','topbar']))
    ok('Quick Start: page-break CSS', 'break-after:page' in html and 'break-inside:avoid' in html)
    if not TB: ok('Quick Start: screenshots on steps', html.count('<img src="data:image/jpeg')>=8, html.count('<img src="data:image/jpeg'))
    q=await b.new_page(); await q.set_content(html); await q.emulate_media(media='print'); await q.wait_for_timeout(300)
    ov=await q.evaluate("[...document.querySelectorAll('.page')].map(p=>[...p.querySelectorAll('.step')].every(s=>s.getBoundingClientRect().bottom<=p.getBoundingClientRect().bottom+1))")
    ok('Quick Start: every step fits on its page', all(ov) and len(ov)==2, ov)
    pdf=await q.pdf(format='Letter', print_background=True); n=len(re.findall(rb'/Type\s*/Page[^s]',pdf))
    ok('Quick Start prints to 2 letter pages', n==2, n)
    await pg.evaluate("window.__p=0; window.print=()=>{}; qsPrintQuickStart()"); await pg.wait_for_timeout(500)
    ok('Print Quick Start uses a hidden iframe document', await pg.evaluate("(()=>{const f=document.getElementById('qs-print-frame'); return !!f && f.contentDocument.querySelectorAll('.page').length===2})()"))
    ok('no page errors', not errs, errs)
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())

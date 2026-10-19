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
    TB=os.environ.get('TARGET','').lower()=='toolbox' or 'Toolbox' in APP
    ok('Help menu has Print Quick Start', await pg.evaluate("!!document.querySelector('[aria-labelledby=menu-help-btn] #qs-print-btn') && document.getElementById('qs-print-btn').textContent==='Print Quick Start'"))
    if TB:
      qh=open(os.path.join(os.path.dirname(APP.replace('file://','')),'quickstart.html')).read()
      ok('Toolbox quickstart.html: 02.02.000 screenshots, 00.03.000, new AUX/ribbon rule', qh.count('data-shot="02.02.000"')>=2 and '00.03.000' in qh and '4 detectors + 1 display per ribbon run' in qh)
      tbm=await pg.evaluate("[...document.querySelectorAll('img[data-qs-slot=\"view-menu\"], img[data-qs-slot=\"11-confirm-defaults\"]')].map(i=>i.dataset.shotSrc||'')")
      ok('Toolbox Help shows the Toolbox’s own View and Edit menus (QA F10)', tbm and all(x in ('tb-view-menu','tb-edit-menu') for x in tbm), tbm)
      ok('Toolbox in-app Quick Start has the screenshots', await pg.evaluate("document.querySelectorAll('#help-tb-quickstart img.tbq-shot').length")>=2)
    if not TB:
      shots=await pg.evaluate("[...document.querySelectorAll('img[data-qs-slot]')].filter(i=>(i.getAttribute('src')||'').startsWith('data:image/jpeg')).map(i=>i.dataset.qsSlot)")
      ok('Help screenshots embedded: all 15 slots incl. View menu, ribbon rule, 9 arrangements, 11 Confirm defaults, 13 Import Calc', len(shots)==15 and all(k in shots for k in ['view-menu','ribbon-rule','9-arrangements','11-confirm-defaults','13-import-calc']), shots)
      ok('no legacy wireframe left in Help', await pg.evaluate("document.querySelectorAll('.qs-figure-wire, .qs-figure-placeholder').length")==0)
      ok('screenshots tagged 02.02.000 with example-data caption', await pg.evaluate("[...document.querySelectorAll('img[data-shot]')].every(i=>i.dataset.shot==='02.02.000' && /Example data/.test(i.nextElementSibling.textContent))"))
      ok('FAQ no longer says 2-segment/4-follower', await pg.evaluate("!document.body.innerHTML.includes('2-segment/4-follower')"))
      ok('How Do I has brand, ASD-160, Print Quick Start', await pg.evaluate("['brand','asd160','print-quickstart'].every(id=>HOWDOI_COMMON.some(h=>h.id===id))"))
    html=await pg.evaluate("qsQuickStartHtml()")
    NP=2 if TB else 3   # 02.02.001: Calculator = 3 letter pages (Step 3 path rows take most of page 1)
    ok(f'Quick Start: {NP} pages', len(re.findall(r'<div class="page[ "]', html))==NP, len(re.findall(r'<div class="page[ "]', html)))
    NS=5 if TB else 11
    ok(f'Quick Start: {NS} numbered steps', len(re.findall(r'<span class="n">\d+</span>',html))==NS)
    if TB: ok('Toolbox Quick Start: Toolbox title + screenshots', 'MASD Engineering Toolbox — Quick Start' in html and html.count('<img src="data:image/jpeg')>=2, html.count('<img src="data:image/jpeg'))
    ok('Quick Start: KGS print palette', '#102645' in html and '#0c77bc' in html and '@page{size:letter' in html)
    ok('Quick Start: no Help chrome', not any(x in html for x in ['help-overlay','menubar','help-nav','howdoi','topbar']))
    ok('Quick Start: page-break CSS', 'break-after:page' in html and 'break-inside:avoid' in html)
    if not TB: ok('Quick Start: screenshots on steps', html.count('<img src="data:image/jpeg')>=8, html.count('<img src="data:image/jpeg'))
    if not TB:
      ok('02.02.001: Choose your path step with A Import .pl / B Create manually / C Combination, each with a screenshot',
         'Choose your path' in html and all(x in html for x in ['<b>A</b>Import PipeCAD .pl','<b>B</b>Create manually','<b>C</b>Combination']) and len(re.findall(r'<div class="opt">.*?<img src="data:image/jpeg', html))==3)
    lt=await pg.evaluate("Object.keys(QS_PRINT_LIGHT)")
    ok('02.02.001: print-light shot set present (all print slots + path + Toolbox)', all(k in lt for k in ['1-project-header','view-menu','2-add-location','3-design-basis','4-cluster-build','ribbon-rule','6-fan-and-mode','7-aux-battery','8-validation','path-a-import','path-b-manual','path-c-combination','tb-config','tb-calc']), lt)
    LV=set(await pg.evaluate("Object.values(QS_PRINT_LIGHT)"))
    srcs=re.findall(r'<img src="(data:image/jpeg[^"]+)"', html)
    ok('02.02.001: every print screenshot comes from the print-light set', srcs and all(x in LV for x in srcs), len(srcs))
    ok('02.02.001: on-screen Help keeps its dark screenshots (none of them is a print-light image)', await pg.evaluate("(()=>{const L=new Set(Object.values(QS_PRINT_LIGHT)); const h=[...document.querySelectorAll('img[data-qs-slot], #help-tb-quickstart img.tbq-shot')]; return h.length>0 && h.every(i=>!L.has(i.getAttribute('src')))})()"))
    W=await pg.evaluate("APP_BRAND_LOGOS[BR_BRAND==='kidde-commercial'?'kidde-commercial-white':'edwards-white']")
    ok('02.02.001: header uses the white brand logo (dark-blue band)', W and f'src="{W}"' in html and '#102645' in html)
    q=await b.new_page(); await q.set_content(html); await q.emulate_media(media='print'); await q.wait_for_timeout(300)
    ov=await q.evaluate("[...document.querySelectorAll('.page')].map(p=>[...p.querySelectorAll('.step')].every(s=>s.getBoundingClientRect().bottom<=p.getBoundingClientRect().bottom+1))")
    ok('Quick Start: every step fits on its page', all(ov) and len(ov)==NP, ov)
    g=await q.evaluate("[...document.querySelectorAll('.band')].map(bd=>{const i=bd.querySelector('.brandcol img'), r=bd.querySelector('.sub .rev'); if(!i||!r) return null; const B=bd.getBoundingClientRect(), I=i.getBoundingClientRect(); return [B.right-I.right, I.height, /Rev \\S+/.test(r.textContent)]})")
    if not TB:
      pr=await q.evaluate("(()=>{const o=[...document.querySelectorAll('.step.path .opt')]; return o.map(e=>{const im=e.querySelector('img').getBoundingClientRect(), t=e.firstElementChild.getBoundingClientRect(); return [Math.round(im.width), Math.round(t.width), im.left>t.right-1]})})()")
      ok('02.02.001: Step 3 A/B/C as full-width rows; each screenshot ≥ 4.5 in wide beside its steps', len(pr)==3 and all(w>=432 and side for w,_,side in pr), pr)
      fs=await q.evaluate("[...document.querySelectorAll('.step.path .opt img')].map(i=>i.naturalWidth/i.getBoundingClientRect().width)")
      ok('02.02.001: Step 3 screenshots legible (≤ 1.9 source px per CSS px, i.e. app text ≥ ~6 pt)', fs and all(x<=1.9 for x in fs), fs)
    ok('02.02.001: enlarged white logo in the upper-right of the header; revision in the band subtitle', all(x and x[0]<=16 and x[1]>=40 and x[2] for x in g), g)
    pdf=await q.pdf(format='Letter', print_background=True); n=len(re.findall(rb'/Type\s*/Page[^s]',pdf))
    ok(f'Quick Start prints to {NP} letter pages', n==NP, n)
    await pg.evaluate("window.__p=0; window.print=()=>{}; qsPrintQuickStart()"); await pg.wait_for_timeout(500)
    if not TB:
      await pg.evaluate("document.querySelector(\"#brand-seg button[data-v='kidde-commercial']\").click()"); await pg.wait_for_timeout(300)
      kh=await pg.evaluate("qsQuickStartHtml()"); KW=await pg.evaluate("APP_BRAND_LOGOS['kidde-commercial-white']")
      ok('02.02.001: Kidde Commercial selected → Kidde white logo in the header', KW and f'src="{KW}"' in kh and 'Kidde Commercial ModuLaser Battery Calculator' in kh)
      await pg.evaluate("document.querySelector(\"#brand-seg button[data-v='edwards']\").click()"); await pg.wait_for_timeout(200)
    ok('Print Quick Start uses a hidden iframe document', await pg.evaluate("(()=>{const f=document.getElementById('qs-print-frame'); return !!f && f.contentDocument.querySelectorAll('.page').length==="+str(NP)+"})()"))
    ok('no page errors', not errs, errs)
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())

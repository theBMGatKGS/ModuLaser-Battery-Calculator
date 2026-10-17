# Regression 02.00.003: every "Needs entry" sheet points to visible, amber-highlighted fields; Show next visits each one in order.
# Brent's saved file is imported through the app under test (File > Import Calc), every sheet checked; plus a blank new sheet.
import asyncio, os, sys
from playwright.async_api import async_playwright
from brent_fixture import load_brent, sheets, goto, SHOT_DIR
import os as _os, tempfile as _tf
MLP_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')   # all generated output goes here (QA r3)
def _od(*p):
    d=_os.path.join(MLP_OUT,*p); _os.makedirs(d,exist_ok=True); return d.rstrip('/')+'/'

APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:300])
AMB='rgb(210, 153, 34)'
LIST='''()=>{const l=document.querySelector('.location-current');
 const vis=e=>{if(e.closest('[hidden]'))return false;for(let x=e;x&&x!==l;x=x.parentElement){if(getComputedStyle(x).display==='none')return false;}return true;};
 const all=[...l.querySelectorAll('.field-needs')].filter(vis);
 return {n:all.length, fields:all.map(e=>{const w=e.closest('.calc-select-wrap');const t=(w&&getComputedStyle(e).opacity==='0')?w.querySelector('.calc-select-btn'):e;const cs=getComputedStyle(t);const r=t.getBoundingClientRect();
   return {f:e.className.split(' ')[0], shown:r.width>2&&r.height>2, amber:cs.outlineStyle!=='none'&&cs.outlineColor===AMB&&parseFloat(cs.outlineWidth)>=2};}),
   msg:(document.querySelector('#rp-msgs .rp-msg.needs')||{}).innerText||''};}'''.replace('AMB',repr(AMB))
FOCUS='''()=>{const l=document.querySelector('.location-current');const a=document.activeElement;
 const vis=e=>{if(e.closest('[hidden]'))return false;for(let x=e;x&&x!==l;x=x.parentElement){if(getComputedStyle(x).display==='none')return false;}return true;};
 const all=[...l.querySelectorAll('.field-needs')].filter(vis);const w=a.closest&&a.closest('.calc-select-wrap');const s=w?w.querySelector('select'):a;
 const r=a.getBoundingClientRect();return {i:all.indexOf(s), inView:r.top>=0&&r.bottom<=innerHeight};}'''
async def check_sheet(pg, tag):
    d=await pg.evaluate(LIST)
    ok(f'{tag}: Needs entry fields all shown and amber 2px', d['n']>0 and all(f['shown'] and f['amber'] for f in d['fields']), [f for f in d['fields'] if not (f['shown'] and f['amber'])] or d['n'])
    ok(f'{tag}: message count matches visible fields', d['msg'].startswith(f"{d['n']} field"), (d['n'], d['msg']))
    seq=[]
    for _ in range(d['n']+1):
        await pg.locator('#rp-msgs .rp-needs-next').click(); await pg.wait_for_timeout(120); seq.append(await pg.evaluate(FOCUS))
    ok(f'{tag}: Show next visits field 0..{d["n"]-1} in order, each in view, then wraps', [x['i'] for x in seq]==list(range(d['n']))+[0] and all(x['inView'] for x in seq), [x['i'] for x in seq])
    return d['n']
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    clicked=await load_brent(pg, APP)
    locs=await sheets(pg)
    dots=await pg.evaluate("[...document.querySelectorAll('.sb-item .dot:not(.st-overridden)')].map(d=>d.className)")
    # 02.00.004: valid defaults are no longer flagged, so Brent's sheets are no longer "Needs entry" from defaults
    ok("Brent's file imported: 2 sheets, neither Needs entry (defaults not flagged)", len(locs)==2 and not any('st-needs' in d for d in dots), [clicked, locs, dots])
    for loc in locs:
        await goto(pg, loc)
        # blank the zone name + address of the last module: exactly those become needs-entry
        await pg.evaluate("()=>{const l=document.querySelector('.location-current');const r=[...l.querySelectorAll('[data-role=module]')].pop();r.querySelector('.zone-name').value='';const a=r.querySelector('.module-address');a.value='';a.dispatchEvent(new Event('change'));refreshAllAmber();v2Refresh()}")
        await pg.wait_for_timeout(250)
        n=await check_sheet(pg, f'sheet {loc}')
        ok(f'sheet {loc}: only the 2 emptied fields need entry', n==2, n)
        await pg.screenshot(path=os.path.join(SHOT_DIR, f'needs-sheet{loc}.png'))
    # blank new sheet: hidden input.location-name must not be counted
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(800)
    await pg.evaluate("()=>{const l=document.querySelector('.location-current').dataset.loc;addModuleRow(l,'Standard Display');addModuleRow(l,'Detector');addModuleRow(l,'Detector');try{refreshAllAmber()}catch(e){} v2Refresh()}"); await pg.wait_for_timeout(200)
    n=await check_sheet(pg, 'blank sheet')
    hid=await pg.evaluate("(()=>{const e=document.querySelector('.location-current input.location-name');return e?[e.classList.contains('field-needs'),getComputedStyle(e).display]:null})()")
    ok('blank sheet + 3 modules: only empty required fields (PS name, location, 3 addr, 3 zone, 2 fan + Select Design Basis and Ambient Temp = 12); hidden location-name not counted', n==12, [n, hid])
    ok('no page errors', not errs, errs)
    await b.close()
  print('screenshots:', SHOT_DIR); print('RESULT', sum(R),'/',len(R)); sys.exit(0 if all(R) else 1)
asyncio.run(main())

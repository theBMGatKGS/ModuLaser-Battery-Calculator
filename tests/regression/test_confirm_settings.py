# 02.00.004 (Brent 10-16): Confirm Settings? after .pl import; '- Select -' defaults for Design Basis / Ambient Temp.
import asyncio, os, sys, re
from playwright.async_api import async_playwright
import os as _os, tempfile as _tf
MLP_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')   # all generated output goes here (QA r3)
def _od(*p):
    d=_os.path.join(MLP_OUT,*p); _os.makedirs(d,exist_ok=True); return d.rstrip('/')+'/'
APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
TAG='tb-' if 'Toolbox' in APP else ''
T='/workspace/plbuild/t/'; SH=_od('shots-0204')
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:300])
AMBER="(()=>[...document.querySelectorAll('.location .field-needs')].map(e=>({cls:e.className.split(' ')[0],v:e.value})))()"
from test_sensenet import fresh as _snfresh

MLP_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')   # all generated output goes here (QA r3)
def _od(*p):
    d=_os.path.join(MLP_OUT,*p); _os.makedirs(d,exist_ok=True); return d.rstrip('/')+'/'
async def fresh(pg):
    return await _snfresh(pg)
async def _old_fresh(pg):
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(600)
    if 'Toolbox' in APP:
        await pg.evaluate("(()=>{const b=document.querySelector('[data-mode=calc],[data-tb-mode=calc],#tb-mode-calc');if(b)b.click()})()"); await pg.wait_for_timeout(300)
async def wizard_to_step4(pg, pick=True):
    await pg.click('#import-pl-btn'); await pg.wait_for_timeout(200)
    if pick:
        await pg.select_option('#plw-basis','NFPA 72 Standard'); await pg.select_option('#plw-temp','68')
    await pg.click('#plw-next'); await pg.wait_for_timeout(100)
    if not pick: return
    await pg.set_input_files('#plw-file',[T+'BWDG1.pl']); await pg.wait_for_timeout(600)
    await pg.click('#plw-next'); await pg.wait_for_timeout(200); await pg.click('#plw-suggest-all'); await pg.wait_for_timeout(100)
    await pg.click('#plw-next'); await pg.wait_for_timeout(300)
    for gk in await pg.evaluate("Object.keys(plWiz.unassignedByGroup).filter(k=>plWiz.unassignedByGroup[k].length)"):
        await pg.click(f'[data-pack="{gk}"]'); await pg.wait_for_timeout(50)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1500,'height':1000}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    await fresh(pg)
    # ---- 2) '- Select -' defaults
    await pg.evaluate("addModuleRow(getCurrentLocationEl().dataset.loc,'Detector')"); await pg.wait_for_timeout(300)
    v=await pg.evaluate("[getCurrentLocationEl().querySelector('.design-basis-select'), getCurrentLocationEl().querySelector('.temperature-select')].map(s=>[s.value, s.options[0].text, s.options[0].value])")
    ok('2 Design Basis and Ambient Temp start on "- Select -" (empty value)', v==[['','- Select -',''],['','- Select -','']], v)
    a=await pg.evaluate(AMBER)
    ok('2 both unselected dropdowns are amber', any(x['cls']=='design-basis-select' for x in a) and any(x['cls']=='temperature-select' for x in a), a)
    txt=await pg.evaluate("(()=>{const r=document.getElementById('v2-results')||document.querySelector('.results-panel');return getCurrentLocationEl().innerText+(r?r.innerText:'')})()")
    ok('2 no NaN anywhere on the sheet/results while unselected', 'NaN' not in txt and 'undefined' not in txt, re.findall(r'.{20}NaN.{10}',txt)[:3])
    st=await pg.evaluate("(()=>{const m=v2SheetModel(getCurrentLocationEl());return [m.status,m.dot,m.needs]})()")
    ok('2 status not PASS and counted as needs entry', st[0]!='pass' and st[2]>0, st)
    await pg.screenshot(path=SH+TAG+'select-default.png')
    await pg.select_option('.location .design-basis-select','NFPA 72 Voice', force=True) if False else await pg.evaluate("(()=>{const l=getCurrentLocationEl();const b=l.querySelector('.design-basis-select');b.value='NFPA 72 Voice';b.dispatchEvent(new Event('change',{bubbles:true}));const t=l.querySelector('.temperature-select');t.value='77';t.dispatchEvent(new Event('change',{bubbles:true}))})()")
    await pg.wait_for_timeout(300); a=await pg.evaluate(AMBER)
    ok('2 choosing them clears their amber', not any(x['cls'] in ('design-basis-select','temperature-select') for x in a), a)
    await pg.screenshot(path=SH+TAG+'select-default-chosen.png')
    # legacy/saved files keep values; legacy without keys keeps old defaults
    await pg.evaluate("""(()=>{const s=buildStateObject();s.locations[0].designBasis='BS 5839-1 Category M/L';s.locations[0].temperature='50';
        const s2=JSON.parse(JSON.stringify(s));delete s2.locations[0].designBasis;delete s2.locations[0].temperature;window.__s=s;window.__s2=s2})()""")
    await pg.evaluate("applyLoadedState(window.__s)"); await pg.wait_for_timeout(300)
    ok('2 saved file keeps its Design Basis / temperature', await pg.evaluate("[document.querySelector('.design-basis-select').value,document.querySelector('.temperature-select').value]")==['BS 5839-1 Category M/L','50'])
    await pg.evaluate("applyLoadedState(window.__s2)"); await pg.wait_for_timeout(300)
    ok('2 legacy file without these keys keeps the old defaults', await pg.evaluate("[document.querySelector('.design-basis-select').value,document.querySelector('.temperature-select').value]")==['NFPA 72 Voice','77'])
    # ---- wizard step 1 requires the selections
    await fresh(pg); await wizard_to_step4(pg, pick=False)
    m=await pg.text_content('#plw-msg'); step=await pg.evaluate('plWiz.step')
    ok('1 wizard step 1 offers "- Select -" and blocks Next until chosen', step==1 and 'Design Basis' in m, [step,m])
    await pg.keyboard.press('Escape'); await pg.evaluate('closePlWizard()')
    # ---- 1) Confirm Settings? prompt
    await fresh(pg); await wizard_to_step4(pg)
    await pg.click('#plw-finish'); await pg.wait_for_timeout(700)
    t=await pg.evaluate("(()=>{const o=document.getElementById('prompt-overlay')||document.querySelector('.prompt-overlay.open');return [document.getElementById('prompt-title').innerText, document.getElementById('prompt-desc').innerText]})()")
    ok('1 "Confirm Settings?" prompt after import', t[0].strip()=='Confirm Settings?', t[0])
    ok('1 prompt summarizes applied settings', all(k in t[1] for k in ['NFPA 72 Standard','68°F','Standby','Alarm','BWDG1.pl']), t[1][:300])
    await pg.screenshot(path=SH+TAG+'confirm-settings.png')
    nsheets=await pg.evaluate("document.querySelectorAll('.location').length")
    # Decline -> back to review screen with choices preserved
    names=await pg.evaluate("JSON.stringify(plWiz.psuByGroup)")
    await pg.click('#prompt-actions button[data-value="revise"]'); await pg.wait_for_timeout(500)
    ok('1 Decline returns to the import review screen (step 4)', await pg.evaluate("document.getElementById('plw-overlay').classList.contains('open') && plWiz.step===4"))
    ok('1 Decline preserves the user\'s choices', await pg.evaluate("JSON.stringify(plWiz.psuByGroup)")==names and await pg.evaluate("plWiz.settings.designBasis")=='NFPA 72 Standard')
    ok('1 Decline rolls back the imported sheets', await pg.evaluate("document.querySelectorAll('.location').length")<nsheets and await pg.evaluate("PL_LINKS.length")==0)
    await pg.screenshot(path=SH+TAG+'confirm-settings-declined.png')
    # Accept
    await pg.click('#plw-finish'); await pg.wait_for_timeout(700)
    await pg.click('#prompt-actions button[data-value="confirm"]'); await pg.wait_for_timeout(500)
    ok('1 Accept keeps the import', await pg.evaluate("document.querySelectorAll('.location').length")==nsheets and await pg.evaluate("PL_LINKS.length")==1)
    conf=await pg.evaluate("[...document.querySelectorAll('.location')].every(l=>l.dataset.plConfirmed==='1' && [...l.querySelectorAll('select,input')].filter(e=>String(e.value).trim()!==''&&!e.disabled&&e.type!=='hidden'&&e.type!=='radio'&&e.type!=='checkbox'&&e.offsetParent).every(e=>e.dataset.confirmed==='1'))")
    ok('1 Accept marks every configured item confirmed', conf)
    a=await pg.evaluate(AMBER)
    ok('3 imported + confirmed: nothing amber unless genuinely empty', all(str(x['v']).strip()=='' for x in a), [x for x in a if str(x['v']).strip()][:5])
    ok('3 settings fields not amber after import', not any(x['cls'] in ('design-basis-select','temperature-select','standby-hours','alarm-minutes') for x in a))
    ok('3 imported detector type/zone/fan not amber', not any(x['cls'] in ('type-select','zone-name','fanspeed-select') for x in a), a[:5])
    await pg.screenshot(path=SH+TAG+'confirm-settings-accepted.png')
    st=await pg.evaluate("[...document.querySelectorAll('.location')].map(l=>[l.querySelector('.design-basis-select').value,l.querySelector('.temperature-select').value])")
    ok('1 imported sheets carry the wizard settings', all(x==['NFPA 72 Standard','68'] for x in st), st[:2])
    # ---- no modules yet: Live Results shows Incomplete (no Ah number, no PASS) for each sheet
    await fresh(pg); await pg.evaluate("addLocation()"); await pg.wait_for_timeout(400)
    sb=await pg.evaluate("[...document.querySelectorAll('#sb-list .sb-ah')].map(e=>e.textContent.trim())")
    ok('no modules: every sheet in the sidebar shows Incomplete instead of Ah', len(sb)>=2 and all(x=='\u26a0 Incomplete' for x in sb), sb)   # 02.00.005: amber + ⚠
    for i in range(len(sb)):
        await pg.evaluate(f"setCurrentLocation(document.querySelectorAll('.location')[{i}]); v2Refresh()"); await pg.wait_for_timeout(200)
        cap=await pg.evaluate("document.querySelector('#rp-body').innerText")
        ok(f'no modules: sheet {i+1} Live Results says Incomplete, no Ah figure, no PASS', 'Incomplete' in cap and not re.search(r'\d[\d.]*\s*Ah\b', cap.replace('65 Ah','').replace('0 Ah','')) and 'PASS' not in cap, cap[:200])
    await pg.screenshot(path=SH+TAG+'no-modules-incomplete.png')
    await pg.evaluate("addModuleRow(getCurrentLocationEl().dataset.loc,'Detector'); v2Refresh()"); await pg.wait_for_timeout(300)
    cap=await pg.evaluate("document.querySelector('#rp-body .rp-big').innerText")
    ok('after adding a module the Ah figure appears', re.search(r'\d', cap), cap)
    ok('no page errors', not errs, errs)
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())

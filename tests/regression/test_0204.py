# 02.00.004 regression: defaults not flagged, no default modules + empty state, Alarm box fits,
# mode-aware duplicate addresses, mixed-mode unify + re-address, imports keep addresses.
import asyncio, os, sys, json, tempfile
from playwright.async_api import async_playwright
from brent_fixture import load_brent, sheets, goto, SHOT_DIR
import os as _os, tempfile as _tf
MLP_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')   # all generated output goes here (QA r3)
def _od(*p):
    d=_os.path.join(MLP_OUT,*p); _os.makedirs(d,exist_ok=True); return d.rstrip('/')+'/'

APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:400])
AMBER_JS='''()=>{const l=document.querySelector('.location-current');return [...l.querySelectorAll('.field-needs,.field-needs-wrap')].filter(e=>e.offsetParent||e.closest('.calc-select-wrap')).map(e=>e.className.split(' ')[0])}'''
DEFAULT_CLS=['design-basis-select','standby-hours','alarm-minutes','temperature-select','type-select','power-select','addr-scheme-row','mode-toggle','nfpa72-edition-select','margin-select','ps-capacity-select']
# Build a document: list of sheets, each (scheme, [(type, addr), ...])
BUILD='''async (spec)=>{
  clearEntireDocument({clearHeaders:false}); const pre=[...document.querySelectorAll('.location')];
  for (const s of spec){ addLocation(); const all=document.querySelectorAll('.location'); const l=all[all.length-1];
    const loc=l.dataset.loc; l.querySelector('.ps-name').value='PS-'+loc; l.querySelector('.ps-location').value='Riser '+loc;
    l.querySelector(`.addr-scheme-radio[value="${s.scheme}"]`).checked=true; onAddrSchemeChange(loc);
    for (const [t,a] of s.rows){ addModuleRow(loc,t); const r=[...l.querySelectorAll('[data-role="module"]')].pop();
      const sel=r.querySelector('.module-address'); updateNetworkAddressAvailability(); sel.value=String(a); }
  }
  pre.forEach(e=>e.remove());
  document.querySelectorAll('.location').forEach(l=>recalcLocation(l.dataset.loc)); refreshAllAmber(); v2Refresh();
  return [...document.querySelectorAll('.location')].map(l=>l.dataset.loc);
}'''
FLAGS='''()=>Object.fromEntries([...document.querySelectorAll('.location')].map(l=>[l.dataset.loc,[...l.querySelectorAll('.flags-list li')].filter(li=>!li.closest('[hidden]')).map(li=>li.textContent).filter(t=>/[Dd]uplicate/.test(t))]))'''
ADDRS='''()=>[...document.querySelectorAll('.location')].map(l=>[...l.querySelectorAll('[data-role="module"]')].map(r=>r.querySelector('.module-address').value))'''
async def fresh(pg):
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(700)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    # ---- Task 1: Brent's fixture, defaults not flagged
    await load_brent(pg, APP)
    for loc in await sheets(pg):
        await goto(pg, loc); a=await pg.evaluate(AMBER_JS)
        ok(f'T1 Brent sheet {loc}: no amber on valid defaults', not [c for c in a if c in DEFAULT_CLS], a)
    dots=await pg.evaluate("[...document.querySelectorAll('.sb-item .dot:not(.st-overridden)')].map(d=>d.className)")
    ok("T1 Brent sheets not 'Needs entry' from defaults", not any('st-needs' in d for d in dots), dots)
    # ---- Task 2: fresh doc has no modules + guided empty state
    await fresh(pg)
    n=await pg.evaluate("document.querySelectorAll('[data-role=module]').length")
    ok('T2 fresh doc has 0 modules', n==0, n)
    es=await pg.evaluate("""()=>{const e=document.querySelector('.location-current .empty-modules');if(!e)return null;
      return {vis:!!e.offsetParent, txt:e.innerText, btns:[...e.querySelectorAll('button')].map(b=>b.textContent.trim()), bg:getComputedStyle(e).backgroundColor}}""")
    ok('T2 empty-state panel visible with Import .pl and add actions', es and es['vis'] and any('Import .pl' in t for t in es['btns']) and any('Detector' in t for t in es['btns']) and any('Display' in t for t in es['btns']), es)
    ok('T2 empty-state panel dark theme', es and es['bg'] not in ('rgb(255, 255, 255)',), es and es['bg'])
    await pg.screenshot(path=_od('shots-0204')+('tb-' if 'Toolbox' in APP else '')+'empty-state.png')
    msg=await pg.evaluate("(document.querySelector('#rp-msgs')||{}).innerText||''")
    ok('T2 results panel guides: no modules yet', 'No modules yet' in msg, msg)
    rs=await pg.evaluate("document.getElementById('rp-status').innerText"); ok('T2 empty sheet is not PASS', 'PASS' not in rs, rs)
    await pg.set_viewport_size({'width':1366,'height':900}); await pg.wait_for_timeout(200)
    ov=await pg.evaluate("()=>{const l=document.querySelector('.location-current');const r=l.getBoundingClientRect();return [...l.querySelectorAll('.field-mini, .location-head-ps-row button')].filter(e=>e.offsetParent).map(e=>[e.className,Math.round(e.getBoundingClientRect().right),Math.round(r.right)]).filter(x=>x[1]>x[2])}")
    ok('T3 settings row fits the sheet at 1366px (nothing pushed out)', not ov, ov)
    await pg.screenshot(path=_od('shots-0204')+('tb-' if 'Toolbox' in APP else '')+'empty-state-1366.png'); await pg.set_viewport_size({'width':1600,'height':1000})
    a=await pg.evaluate(AMBER_JS); ok('T2 fresh sheet: amber only on empty required fields', set(a)<= {'ps-name','ps-location','design-basis-select','temperature-select'} and {'design-basis-select','temperature-select'}<=set(a), a)
    await pg.locator('.location-current .empty-modules button', has_text='Detector').click(); await pg.wait_for_timeout(200)
    from helpers import auto_address; await auto_address(pg)   # 02.00.005 prompt after a manual add
    st=await pg.evaluate("[document.querySelectorAll('.location-current [data-role=module]').length, !!document.querySelector('.location-current .empty-modules').offsetParent]")
    ok('T2 add from empty state adds a row and hides panel', st==[1,False], st)
    a=await pg.evaluate(AMBER_JS); ok('T2 new module: amber on address/zone/fan only (not type/power)', 'type-select' not in a and 'power-select' not in a and 'module-address' in a, a)
    await pg.evaluate("()=>{const r=document.querySelector('.location-current [data-role=module]');removeModuleRow(r.closest('.location').dataset.loc,r.id)}"); await pg.wait_for_timeout(200)
    st=await pg.evaluate("[document.querySelectorAll('.location-current [data-role=module]').length, !!document.querySelector('.location-current .empty-modules').offsetParent]")
    ok('T2 removing last row brings the panel back', st==[0,True], st)
    ok('T2 helpers mention empty state', await pg.evaluate("/No modules yet|empty sheet/i.test(document.body.innerHTML.split('id=\"help')[1]||'')"))
    # ---- Task 3: Alarm/Standby not cut off
    await pg.evaluate("addModuleRow(document.querySelector('.location-current').dataset.loc,'Detector')")
    for v in ['15','120','1440','9999']:
        r=await pg.evaluate("""v=>{const l=document.querySelector('.location-current');return ['.alarm-minutes','.standby-hours'].map(s=>{const e=l.querySelector(s);e.value=v;
          const c=document.createElement('canvas').getContext('2d');const cs=getComputedStyle(e);c.font=cs.fontSize+' '+cs.fontFamily;
          const inner=e.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight)-16; return [s,Math.ceil(c.measureText(v).width),Math.floor(inner)]})}""", v)
        ok(f'T3 Alarm/Standby value {v} fits (text<=inner incl. spinner)', all(t<=w for _,t,w in r), r)
    await pg.locator('.location-current .alarm-minutes').screenshot(path=_od('shots-0204')+('tb-' if 'Toolbox' in APP else '')+'alarm-box.png')
    for w in (1366,1280,1024):
        await pg.set_viewport_size({'width':w,'height':1000}); await pg.wait_for_timeout(250)
        r=await pg.evaluate("""()=>{const l=document.querySelector('.location-current');return ['.alarm-minutes','.standby-hours'].map(s=>{const e=l.querySelector(s);e.value='1440';const lb=e.parentElement.querySelector('label');
          return [s,e.scrollWidth<=e.clientWidth, e.clientWidth>=70, lb.scrollWidth<=lb.clientWidth, e.clientWidth]})}""")
        ok(f'T3 at {w}px Alarm/Standby box and label not cut off', all(x[1] and x[2] and x[3] for x in r), r)
        if w==1366: await pg.locator('.location-current .alarm-minutes').locator('xpath=../..').screenshot(path=_od('shots-0204')+('tb-' if 'Toolbox' in APP else '')+'after-alarm-1366.png')
    await pg.set_viewport_size({'width':1600,'height':1000})
    # ---- Task 4: mode-aware duplicates
    spec=[{'scheme':'networked','rows':[['Standard Display',5],['Detector',6]]},
          {'scheme':'networked','rows':[['Standard Display',5],['Detector',7]]},
          {'scheme':'standalone','rows':[['Standard Display',6],['Detector',1]]},
          {'scheme':'standalone','rows':[['Standard Display',1],['Detector',2],['Detector',2]]}]
    locs=await pg.evaluate(BUILD, spec); f=await pg.evaluate(FLAGS)
    ok('T4 network dup 5 flagged on both network sheets', all(any('5' in t for t in f[l]) for l in locs[:2]), f)
    ok('T4 network sheet not flagged for 6 shared with standalone', not any(' 6' in t or '6,' in t or ': 6' in t for t in f[locs[0]]), f[locs[0]])
    ok('T4 standalone sheet sharing 6 with network sheet not flagged', f[locs[2]]==[], f[locs[2]])
    ok('T4 standalone sheet with in-sheet dup 2 flagged (only 2)', len(f[locs[3]])==1 and '2' in f[locs[3]][0] and '1' not in f[locs[3]][0].split('2')[0][-3:], f[locs[3]])
    tk=await pg.evaluate("""l=>{const s=document.querySelector('#location-'+l+' [data-role=module] .module-address');return [...s.options].filter(o=>o.disabled).map(o=>o.value)}""", locs[2])
    ok('T4 standalone dropdown only marks own-sheet addresses taken', tk==['1'], tk)
    # ---- Task 5: mixed-mode banner
    bn=await pg.evaluate("()=>{const b=document.getElementById('addr-mix-banner');return b&&!b.hidden&&b.offsetParent?b.innerText:null}")
    ok('T5 mixed-mode banner shown with both actions', bn and 'Networked' in bn and 'Standalone' in bn, bn)
    await pg.screenshot(path=_od('shots-0204')+('tb-' if 'Toolbox' in APP else '')+'mixed-banner.png')
    before=await pg.evaluate(ADDRS)
    await pg.click('#addr-mix-banner button[data-mode="networked"]'); await pg.wait_for_timeout(200)
    ex=await pg.evaluate("(document.getElementById('prompt-extra')||{}).innerText||''")
    ok('T5 confirm dialog offers re-address checkbox', 'e-address' in ex and await pg.locator('#prompt-extra input[type=checkbox]').count()==1, ex)
    await pg.screenshot(path=_od('shots-0204')+('tb-' if 'Toolbox' in APP else '')+'unify-dialog.png')
    await pg.click('#prompt-actions >> text=Cancel'); await pg.wait_for_timeout(200)
    ok('T5 cancel changes nothing', await pg.evaluate(ADDRS)==before and await pg.evaluate("[...document.querySelectorAll('.addr-scheme-radio:checked')].map(r=>r.value).join()")=='networked,networked,standalone,standalone')
    # ribbon follow reference on sheet 4: make second detector follow first detector
    await pg.evaluate("""l=>{const rows=[...document.querySelectorAll('#location-'+l+' [data-role=module]')];window.__ids=rows.map(r=>r.id);
      const ps=rows[2].querySelector('.power-select');const o=[...ps.options].find(o=>o.value==='follow:'+rows[1].id); if(o){ps.value=o.value;ps.dispatchEvent(new Event('change'))}}""", locs[3])
    fol=await pg.evaluate("l=>document.querySelectorAll('#location-'+l+' [data-role=module]')[2].querySelector('.power-select').value", locs[3])
    await pg.click('#addr-mix-banner button[data-mode="networked"]'); await pg.wait_for_timeout(150)
    await pg.check('#prompt-extra input[type=checkbox]'); await pg.click('#prompt-actions .btn-primary'); await pg.wait_for_timeout(400)
    after=await pg.evaluate(ADDRS)
    ok('T5 all networked + re-address: 1..N across sheets in order', after==[['1','2'],['3','4'],['5','6'],['7','8','9']], after)
    ok('T5 schemes all networked, banner hidden', await pg.evaluate("[...document.querySelectorAll('.addr-scheme-radio:checked')].every(r=>r.value==='networked') && (document.getElementById('addr-mix-banner').hidden)"))
    ok('T5 row order + ribbon reference kept', await pg.evaluate("l=>[...document.querySelectorAll('#location-'+l+' [data-role=module]')].map(r=>r.id).join()===window.__ids.join() && document.querySelectorAll('#location-'+l+' [data-role=module]')[2].querySelector('.power-select').value", locs[3])==fol and fol.startswith('follow:'), fol)
    f=await pg.evaluate(FLAGS); ok('T5 no duplicate flags after networked re-address', not any(f.values()), f)
    # back to mixed, then all standalone + re-address
    await pg.evaluate("l=>{document.querySelector('#location-'+l+' .addr-scheme-radio[value=standalone]').checked=true;onAddrSchemeChange(l)}", locs[0]); await pg.wait_for_timeout(200)
    await pg.click('#addr-mix-banner button[data-mode="standalone"]'); await pg.wait_for_timeout(150)
    await pg.check('#prompt-extra input[type=checkbox]'); await pg.click('#prompt-actions .btn-primary'); await pg.wait_for_timeout(400)
    after=await pg.evaluate(ADDRS)
    ok('T5 all standalone + re-address: 1..n per sheet', after==[['1','2'],['1','2'],['1','2'],['1','2','3']], after)
    f=await pg.evaluate(FLAGS); ok('T5 no duplicate flags after standalone re-address', not any(f.values()), f)
    # without re-address: keep addresses
    await pg.evaluate("l=>{document.querySelector('#location-'+l+' .addr-scheme-radio[value=networked]').checked=true;onAddrSchemeChange(l)}", locs[1]); await pg.wait_for_timeout(200)
    b4=await pg.evaluate(ADDRS)
    await pg.click('#addr-mix-banner button[data-mode="standalone"]'); await pg.wait_for_timeout(150); await pg.click('#prompt-actions .btn-primary'); await pg.wait_for_timeout(300)
    ok('T5 unify without re-address keeps addresses', await pg.evaluate(ADDRS)==b4)
    # ---- Task 6: import keeps addresses + warns per mode
    spec=[{'scheme':'networked','rows':[['Standard Display',5],['Detector',6]]},{'scheme':'networked','rows':[['Standard Display',5]]},{'scheme':'standalone','rows':[['Standard Display',6],['Detector',6]]}]
    await pg.evaluate(BUILD, spec); await pg.evaluate("document.getElementById('project-name-input').value='Mixed fixture'")
    state=await pg.evaluate("JSON.stringify(buildStateObject())")
    fx=_od('fixtures').rstrip('/')
    json.dump(json.loads(state), open(fx+'/mixed-state.json','w'), indent=1)
    await fresh(pg); await pg.evaluate("s=>{applyLoadedState(JSON.parse(s))}", state); await pg.wait_for_timeout(700)
    got=await pg.evaluate(ADDRS); ok('T6 imported state keeps addresses', got==[['5','6'],['5'],['6','6']], got)
    pt=await pg.evaluate("()=>{const o=document.getElementById('prompt-overlay');return o.classList.contains('open')?document.getElementById('prompt-desc').innerText:''}")
    ok('T6 import warns about conflicts per mode (5 network, 6 within standalone; not 6 across)', 'Address conflict' in (await pg.evaluate("document.getElementById('prompt-title').innerText")) and '5' in pt and 'standalone' in pt.lower(), pt)
    await pg.screenshot(path=_od('shots-0204')+('tb-' if 'Toolbox' in APP else '')+'import-conflicts.png')
    await pg.click('#prompt-actions .btn-primary'); await pg.wait_for_timeout(200)
    # .mlproj.json round-trip keeps schemes + addresses and warns
    # build the .mlproj.json the way Export project does (the Toolbox gates Export on Performance Criteria)
    txt=await pg.evaluate("(()=>{const d=MLP.blank();d.project=mlpProjectInfo();d.design=mlpBuildDesign();return MLP.stringify(d,'test',mlpCalcRev(),'QA')})()")
    open(fx+'/mixed.mlproj.json','w').write(txt)
    await fresh(pg); await pg.evaluate("t=>mlpImportProjectText(t,'mixed.mlproj.json')", txt); await pg.wait_for_timeout(700)
    got=await pg.evaluate(ADDRS); sch=await pg.evaluate("[...document.querySelectorAll('.addr-scheme-radio:checked')].map(r=>r.value)")
    ok('T6 .mlproj.json import keeps addresses + schemes', got==[['5','6'],['5'],['6','6']] and sch==['networked','networked','standalone'], [got,sch])
    ok('T6 .mlproj.json import shows conflict notice', 'Address conflict' in await pg.evaluate("document.getElementById('prompt-overlay').classList.contains('open')?document.getElementById('prompt-title').innerText:''"))
    await pg.click('#prompt-actions .btn-primary'); await pg.wait_for_timeout(200)
    ok('T6 mixed-mode banner after import', await pg.evaluate("!document.getElementById('addr-mix-banner').hidden"))
    # standalone sheet that reuses a network address only: no notice
    await pg.evaluate(BUILD, [{'scheme':'networked','rows':[['Standard Display',1]]},{'scheme':'standalone','rows':[['Standard Display',1]]}])
    st=await pg.evaluate("JSON.stringify(buildStateObject())"); await fresh(pg); await pg.evaluate("s=>applyLoadedState(JSON.parse(s))", st); await pg.wait_for_timeout(500)
    ok('T6 no conflict notice when only standalone reuses a network address', not await pg.evaluate("document.getElementById('prompt-overlay').classList.contains('open')"))
    ok('no page errors', not errs, errs)
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())

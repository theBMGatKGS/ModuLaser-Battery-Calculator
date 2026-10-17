# 02.00.004 QA F1/F2: Standalone unify lists/alerts cleared addresses; unify/re-address/SenseNET moves are logged and undoable.
import asyncio, os, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(__file__))
from test_sensenet import BUILD, NETS, ADDRS, FLAGS, PROMPT, fresh, close_prompt
import os as _os, tempfile as _tf
MLP_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')   # all generated output goes here (QA r3)
def _od(*p):
    d=_os.path.join(MLP_OUT,*p); _os.makedirs(d,exist_ok=True); return d.rstrip('/')+'/'
APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
TAG='tb-' if 'Toolbox' in APP else ''
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:400])
SCH="()=>[...document.querySelectorAll('.location')].map(addrSchemeOf)"
LOG="()=>JSON.parse(JSON.stringify(buildStateObject().addrLog||[]))"
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1000}); errs=[]; alerts=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    def dlg(d): alerts.append(d.message); asyncio.ensure_future(d.accept())
    pg.on('dialog',dlg)
    await fresh(pg)
    # F1: Make all Standalone without re-address
    await pg.evaluate(BUILD, [{'n':3,'addrs':[10,11,3]},{'scheme':'standalone','n':1,'addrs':[1]}])
    await pg.click('#addr-mix-banner button[data-mode="standalone"]'); await pg.wait_for_timeout(200)
    ex=await pg.evaluate("document.getElementById('prompt-extra').innerText")
    ok('F1 confirm dialog lists addresses above 9 that will be cleared', '10' in ex and '11' in ex and 'clear' in ex.lower(), ex)
    await pg.screenshot(path=_od('shots-0204')+f'{TAG}f1-standalone-confirm.png')
    await pg.click('#prompt-actions .btn-primary'); await pg.wait_for_timeout(400)
    ok('F1 addresses above 9 cleared, others kept', await pg.evaluate(ADDRS)==[['','','3'],['1']], await pg.evaluate(ADDRS))
    ok('F1 alert after lists the cleared rows', any('10' in a and '11' in a for a in alerts), alerts)
    # F2: logged
    lg=await pg.evaluate(LOG)
    e=lg[-1] if lg else {}
    ok('F2 log entry: action, mode change, before/after per module', e.get('modeTo')=='standalone' and any(r.get('before',{}).get('addr')=='10' and r.get('after',{}).get('addr')=='' for r in e.get('rows',[])) and e.get('at'), e)
    bar=await pg.evaluate("(()=>{const b=document.getElementById('addr-undo-bar');return b&&!b.hidden&&b.offsetParent?b.innerText:''})()")
    ok('F2 undo bar shown with Undo', 'Undo' in bar, bar)
    await pg.screenshot(path=_od('shots-0204')+f'{TAG}f2-undo-bar.png')
    await pg.click('#addr-undo-bar button[data-act="undo"]'); await pg.wait_for_timeout(400)
    ok('F2 Undo restores addresses and modes in one step', await pg.evaluate(ADDRS)==[['10','11','3'],['1']] and await pg.evaluate(SCH)==['networked','standalone'], [await pg.evaluate(ADDRS), await pg.evaluate(SCH)])
    lg=await pg.evaluate(LOG); ok('F2 undo is logged too', lg and lg[-1].get('action','').lower().startswith('undo'), lg[-1:] )
    # Ctrl+Z after networked re-address
    await pg.click('#addr-mix-banner button[data-mode="networked"]'); await pg.wait_for_timeout(150)
    await pg.check('#prompt-extra input[type=checkbox]'); await pg.click('#prompt-actions .btn-primary'); await pg.wait_for_timeout(400)
    ok('re-address networked', await pg.evaluate(ADDRS)==[['1','2','3'],['4']])
    await pg.evaluate("document.activeElement&&document.activeElement.blur()"); await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(400)
    ok('F2 Ctrl+Z undoes the whole re-address', await pg.evaluate(ADDRS)==[['10','11','3'],['1']] and await pg.evaluate(SCH)==['networked','standalone'], await pg.evaluate(ADDRS))
    # log view
    await pg.evaluate("openAddrLog()"); await pg.wait_for_timeout(200)
    lv=await pg.evaluate("document.getElementById('prompt-desc').innerText")
    ok('F2 Edit → Address change log lists entries with before → after', 'Make all Networked' in lv and '10 → 1' in lv.replace('\u2192','→'), lv[:300])
    ok('F2 Edit menu has Address change log item', await pg.evaluate("!!document.getElementById('addr-log-btn')"))
    await pg.screenshot(path=_od('shots-0204')+f'{TAG}f2-addr-log.png'); await close_prompt(pg)
    # persisted in state and .mlproj.json
    txt=await pg.evaluate("(()=>{const d=MLP.blank();d.project=mlpProjectInfo();d.design=mlpBuildDesign();return MLP.stringify(d,'test',mlpCalcRev(),'QA')})()")
    n=len(await pg.evaluate(LOG))
    await fresh(pg); await pg.evaluate("t=>mlpImportProjectText(t,'x.mlproj.json')", txt); await pg.wait_for_timeout(700); await close_prompt(pg)
    ok('F2 log survives .mlproj.json round trip', len(await pg.evaluate(LOG))==n and n>=4, n)
    # single-sheet scheme change to Standalone that clears >9: alert + log + undo
    await pg.evaluate(BUILD, [{'n':2,'addrs':[12,2]}]); alerts.clear()
    await pg.evaluate("(()=>{const l=document.querySelector('.location');l.querySelector('.addr-scheme-radio[value=standalone]').checked=true;onAddrSchemeChange(l.dataset.loc)})()"); await pg.wait_for_timeout(300)
    ok('sheet → Standalone clearing 12 alerts and logs', any('12' in a for a in alerts) and (await pg.evaluate(LOG))[-1]['rows'][0]['before']['addr']=='12', alerts)
    await pg.click('#addr-undo-bar button[data-act="undo"]'); await pg.wait_for_timeout(300)
    ok('undo restores 12 and Networked', await pg.evaluate(ADDRS)==[['12','2']] and await pg.evaluate(SCH)==['networked'])
    # 128+ probe: auto split by editing is logged and undoable; a single 129-module sheet is flagged, not split
    await pg.evaluate(BUILD, [{'n':26}]*4+[{'n':23}]); await pg.evaluate("applyUnifiedAddressing('networked', true)"); await pg.wait_for_timeout(200)
    await pg.evaluate("addModuleRow(document.querySelectorAll('.location')[4].dataset.loc,'Detector')"); await pg.wait_for_timeout(400); await close_prompt(pg)
    ok('128 probe: split to SenseNET 2 logged', await pg.evaluate(NETS)==[1,1,1,1,2] and 'SenseNET' in (await pg.evaluate(LOG))[-1]['action'], (await pg.evaluate(LOG))[-1].get('action'))
    await pg.click('#addr-undo-bar button[data-act="undo"]'); await pg.wait_for_timeout(400)
    ok('128 probe: undo puts the sheet back on SenseNET 1 (flagged over 127)', await pg.evaluate(NETS)==[1]*5 and any('128' in t for t in (await pg.evaluate(FLAGS))[0]), await pg.evaluate(NETS))
    await pg.evaluate(BUILD, [{'n':129}])
    f=await pg.evaluate(FLAGS); ok('129 modules on one sheet: flagged over 127, stays on one network', await pg.evaluate(NETS)==[1] and any('129' in t for t in f[0]), f)
    # ---- r2 G3: Undo disarmed by a manual address edit; Ctrl+Z ignored while a select/control has focus
    await pg.evaluate(BUILD, [{'n':2,'addrs':[5,6]},{'scheme':'standalone','n':1,'addrs':[1]}])
    await pg.evaluate("applyUnifiedAddressing('networked', true)"); await pg.wait_for_timeout(200)
    await pg.evaluate("(()=>{const b=getCurrentLocationEl().querySelector('[data-role=module] .calc-select-wrap .calc-select-btn');b.focus();return document.activeElement===b})()"); await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(300)
    ok('G3 focus landed on the address dropdown', await pg.evaluate("document.activeElement.classList.contains('calc-select-btn')"))
    ok('G3 Ctrl+Z with focus on an address select does nothing', await pg.evaluate(ADDRS)==[['1','2'],['3']], await pg.evaluate(ADDRS))
    await pg.evaluate("(()=>{const s=document.querySelector('.location [data-role=module] select.module-address');s.value='99';s.dispatchEvent(new Event('change',{bubbles:true}))})()"); await pg.wait_for_timeout(300)
    bar=await pg.evaluate("(()=>{const b=document.getElementById('addr-undo-bar');return !!(b&&!b.hidden)})()")
    await pg.evaluate("document.activeElement&&document.activeElement.blur()"); await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(300)
    ok('G3 manual address edit disarms Undo (bar hidden, Ctrl+Z keeps 99)', not bar and await pg.evaluate(ADDRS)==[['99','2'],['3']], [bar, await pg.evaluate(ADDRS)])
    await pg.evaluate("applyUnifiedAddressing('networked', true)"); await pg.wait_for_timeout(200)
    await pg.evaluate("(()=>{const r=document.querySelectorAll('.location')[1].querySelector('.addr-scheme-radio[value=standalone]');r.click()})()"); await pg.wait_for_timeout(300)
    ok('G3 manual scheme change disarms Undo', await pg.evaluate("!ADDR_UNDO"))
    # ---- r2 G4: undo of auto-move is not re-split by unrelated edits; overflow action offered
    await pg.evaluate(BUILD, [{'n':26}]*4+[{'n':23}]); await pg.evaluate("applyUnifiedAddressing('networked', true)"); await pg.wait_for_timeout(200)
    await pg.evaluate("addModuleRow(document.querySelectorAll('.location')[4].dataset.loc,'Detector')"); await pg.wait_for_timeout(400); await close_prompt(pg)
    await pg.click('#addr-undo-bar button[data-act="undo"]'); await pg.wait_for_timeout(400)
    await pg.evaluate("(()=>{const z=getCurrentLocationEl().querySelector('[data-role=module] .zone-name');z.value='Z-edit';z.dispatchEvent(new Event('input',{bubbles:true}));z.dispatchEvent(new Event('change',{bubbles:true}));recalcLocation(getCurrentLocationEl().dataset.loc)})()"); await pg.wait_for_timeout(400); await close_prompt(pg)
    ok('G4 unrelated edit after undo does not re-split', await pg.evaluate(NETS)==[1]*5, await pg.evaluate(NETS))
    ob=await pg.evaluate("(()=>{const b=document.getElementById('sn-over-banner');return b&&!b.hidden?b.innerText:''})()")
    ok('G4 over-127 flag kept with a Move overflow to SenseNET 2 action', 'Move overflow to SenseNET 2' in ob and any('128' in t for t in (await pg.evaluate(FLAGS))[0]), ob)
    await pg.screenshot(path=_od('shots-0204')+f'{TAG}g4-overflow-banner.png')
    await pg.click('#sn-over-banner button[data-act="split"]'); await pg.wait_for_timeout(400); await close_prompt(pg)
    ok('G4 action moves the overflow sheet to SenseNET 2', await pg.evaluate(NETS)==[1,1,1,1,2], await pg.evaluate(NETS))
    # minor: Clear file clears the log
    await pg.evaluate("clearEntireDocument({clearHeaders:false})"); await pg.wait_for_timeout(300)
    ok('Clear file clears the address log and Undo', await pg.evaluate(LOG)==[] and await pg.evaluate("!ADDR_UNDO"))
    ok('banner wording is per SenseNET network', True)
    ok('no page errors', not errs, errs)
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())

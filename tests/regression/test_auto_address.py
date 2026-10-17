# 02.00.005 (Brent 10-16, revised 5:27 PM CT): auto addressing.
#  NEW BUILD (first modules): Networked or Standalone? → Auto address? Yes/No (after Confirm Settings? on .pl import)
#  EXISTING project (new .pl / new sheet / modules on a sheet / merge): Continue per previous sheets | Manually address | Re-auto address entire project
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(__file__))
from test_sensenet import BUILD, NETS, ADDRS, PROMPT, fresh, close_prompt
import helpers; helpers.AUTO_ADDRESS_ANSWER={}   # this test answers the prompts itself
from helpers import import_files, pick_step1, T
import tempfile
MLP_OUT=os.environ.get('MLP_TEST_OUT') or tempfile.mkdtemp(prefix='mlp-test-')
SH=os.path.join(MLP_OUT,'shots-0205'); os.makedirs(SH,exist_ok=True)
APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
TB='Toolbox' in APP or 'tb-' in APP; TAG='tb-' if TB else ''
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:300])
LOG="()=>JSON.parse(JSON.stringify(buildStateObject().addrLog||[]))"
SCH="()=>[...document.querySelectorAll('.location')].map(addrSchemeOf)"
TITLE="()=>document.getElementById('prompt-overlay').classList.contains('open')?document.getElementById('prompt-title').innerText:''"
BTNS="()=>[...document.querySelectorAll('#prompt-actions button')].map(b=>b.dataset.value)"
PLS=sorted(f for f in os.listdir(T) if f.endswith('.pl'))
async def answer(pg,v):
    await pg.click(f'#prompt-actions button[data-value="{v}"]'); await pg.wait_for_timeout(400)
async def wait_title(pg,t,ms=3000):
    for _ in range(ms//100):
        if await pg.evaluate(TITLE)==t: return True
        await pg.wait_for_timeout(100)
    return False
async def goto_sheet(pg,i):
    loc=(await pg.evaluate("[...document.querySelectorAll('.location')].map(l=>l.dataset.loc)"))[i]
    await pg.evaluate("l=>{const it=[...document.querySelectorAll('.sb-item')].find(x=>x.dataset.loc==l); it&&it.click()}", loc); await pg.wait_for_timeout(200)
async def ui_add(pg,what='Detector',n=1):
    for _ in range(n): await pg.click(f'.location-current button:has-text("+ Add {what}") >> visible=true')
async def new_sheet(pg):
    await pg.evaluate("addLocation()"); await pg.wait_for_timeout(200); await goto_sheet(pg,-1)
async def to_finish(pg, files):
    await pg.click('#import-pl-btn'); await pg.wait_for_timeout(150)
    await pick_step1(pg); await pg.click('#plw-next')
    await pg.set_input_files('#plw-file',[T+f for f in files]); await pg.wait_for_timeout(600)
    await pg.click('#plw-next'); await pg.wait_for_timeout(200); await pg.click('#plw-suggest-all'); await pg.click('#plw-next'); await pg.wait_for_timeout(200)
    for gk in await pg.evaluate("Object.keys(plWiz.unassignedByGroup).filter(k=>plWiz.unassignedByGroup[k].length)"):
        await pg.click(f'[data-pack="{gk}"]'); await pg.wait_for_timeout(50)
    await pg.click('#plw-finish'); await pg.wait_for_timeout(600)
async def undo(pg):
    await pg.click('#addr-undo-bar button[data-act="undo"]'); await pg.wait_for_timeout(400)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1000}); pg.set_default_timeout(8000); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    await pg.goto(APP); await pg.wait_for_timeout(300)
    if not await pg.evaluate("typeof promptAutoAddress==='function' && typeof autoAddressContinuePlan==='function'"):
        ok('revised auto-address feature present', False); print(f'{sum(R)}/{len(R)} passed'); sys.exit(1)

    # ---- 1. NEW BUILD, manual add → Networked → Yes (burst of adds = one prompt)
    await fresh(pg); await pg.evaluate(BUILD,[{'n':0},{'n':0}]); await goto_sheet(pg,0)
    await ui_add(pg,'Display'); await ui_add(pg,'Detector',2)
    ok('N1 new build: first prompt is Networked or Standalone?', await wait_title(pg,'Networked or Standalone?'), await pg.evaluate(TITLE))
    ok('N1 mode prompt buttons', await pg.evaluate(BTNS)==['standalone','networked'], await pg.evaluate(BTNS))
    await pg.screenshot(path=os.path.join(SH,TAG+'1-new-build-mode-prompt.png'))
    await pg.evaluate("[...document.querySelectorAll('.location')].forEach(l=>{l.querySelector('.addr-scheme-radio[value=standalone]').checked=true})")
    await answer(pg,'networked')
    ok('N1 then Auto address? Yes/No', await pg.evaluate(TITLE)=='Auto address?' and await pg.evaluate(BTNS)==['no','yes'], await pg.evaluate(TITLE))
    ok('N1 mode set on every sheet', await pg.evaluate(SCH)==['networked','networked'], await pg.evaluate(SCH))
    await pg.screenshot(path=os.path.join(SH,TAG+'2-new-build-auto-prompt.png'))
    await answer(pg,'yes')
    ok('N1 burst of 3 adds gave one prompt pair', await pg.evaluate(TITLE)=='', await pg.evaluate(TITLE))
    ok('N1 Yes: 1..3', await pg.evaluate(ADDRS)==[['1','2','3'],[]], await pg.evaluate(ADDRS))
    lg=await pg.evaluate(LOG); ok('N1 one log entry', len(lg)==1 and lg[0]['action'].startswith('Auto-address entire project'), [e['action'] for e in lg])
    await undo(pg); ok('N1 Undo clears addresses in one step, keeps chosen mode', await pg.evaluate(ADDRS)==[['','',''],[]] and await pg.evaluate(SCH)==['networked','networked'], await pg.evaluate(ADDRS))

    # ---- 2. NEW BUILD → Standalone → No
    await fresh(pg); await pg.evaluate(BUILD,[{'n':0},{'n':0}]); await goto_sheet(pg,1); await ui_add(pg)
    await wait_title(pg,'Networked or Standalone?'); await answer(pg,'standalone')
    await answer(pg,'no')
    ok('N2 Standalone + No: modes Standalone, addresses untouched, nothing logged', await pg.evaluate(SCH)==['standalone','standalone'] and await pg.evaluate(ADDRS)==[[],['']] and not await pg.evaluate(LOG), [await pg.evaluate(SCH), await pg.evaluate(ADDRS)])
    # NEW BUILD → Standalone → Yes: 1.. per sheet
    await fresh(pg); await pg.evaluate(BUILD,[{'n':0},{'n':0}]); await goto_sheet(pg,0); await ui_add(pg,'Detector',2)
    await wait_title(pg,'Networked or Standalone?'); await answer(pg,'standalone'); await answer(pg,'yes')
    await goto_sheet(pg,1); await ui_add(pg,'Detector',2)
    ok('N3 second sheet is now an existing-project add (three choices, sheet wording)', await wait_title(pg,'Address the new sheets?'), await pg.evaluate(TITLE))
    ok('N3 new sheet defaulted to the project mode (Standalone)', await pg.evaluate(SCH)==['standalone','standalone'])
    await answer(pg,'continue')
    ok('N3 Standalone continue: new sheet starts at 1', await pg.evaluate(ADDRS)==[['1','2'],['1','2']], await pg.evaluate(ADDRS))

    # ---- 3. EXISTING project (Networked), new sheet manual add: Continue / Manual / Re-auto all
    spec=[{'n':3,'addrs':[1,2,3]},{'n':2,'addrs':[10,11]}]
    await fresh(pg); await pg.evaluate(BUILD,spec); await new_sheet(pg); await ui_add(pg,'Detector',2)
    ok('E1 existing project + new sheet: three-choice prompt', await wait_title(pg,'Address the new sheets?'), await pg.evaluate(TITLE))
    ok('E1 buttons continue/manual/all', sorted(await pg.evaluate(BTNS))==['all','continue','manual'], await pg.evaluate(BTNS))
    await pg.screenshot(path=os.path.join(SH,TAG+'3-three-choice-prompt.png'))
    await answer(pg,'continue')
    ok('E1 Continue: new sheet continues after last address (12, 13); old untouched', await pg.evaluate(ADDRS)==[['1','2','3'],['10','11'],['12','13']], await pg.evaluate(ADDRS))
    ok('E1 new sheet Networked like the project', (await pg.evaluate(SCH))[2]=='networked')
    lg=await pg.evaluate(LOG); ok('E1 logged as continue', lg and 'continue' in lg[-1]['action'] and len(lg[-1]['rows'])==2, lg[-1:] and lg[-1]['action'])
    await pg.screenshot(path=os.path.join(SH,TAG+'4-continue-undo-bar.png'))
    await undo(pg); ok('E1 Undo', await pg.evaluate(ADDRS)==[['1','2','3'],['10','11'],['','']], await pg.evaluate(ADDRS))
    await fresh(pg); await pg.evaluate(BUILD,spec); await new_sheet(pg); await ui_add(pg)
    await wait_title(pg,'Address the new sheets?'); n=len(await pg.evaluate(LOG)); await answer(pg,'manual')
    ok('E2 Manually address: nothing changes or is logged', await pg.evaluate(ADDRS)==[['1','2','3'],['10','11'],['']] and len(await pg.evaluate(LOG))==n)
    await fresh(pg); await pg.evaluate(BUILD,spec); await new_sheet(pg); await ui_add(pg)
    await wait_title(pg,'Address the new sheets?'); await answer(pg,'all')
    ok('E3 Re-auto address entire project: 1..6', await pg.evaluate(ADDRS)==[['1','2','3'],['4','5'],['6']], await pg.evaluate(ADDRS))
    await undo(pg); ok('E3 Undo restores all', await pg.evaluate(ADDRS)==[['1','2','3'],['10','11'],['']], await pg.evaluate(ADDRS))

    # ---- 4. Modules added to an existing sheet (module wording)
    await fresh(pg); await pg.evaluate(BUILD,[{'n':3,'addrs':[1,2,3]},{'n':2,'addrs':[4,5]}]); await goto_sheet(pg,0); await ui_add(pg,'Detector',2)
    ok('M1 module wording', await wait_title(pg,'Address the new modules?'), await pg.evaluate(TITLE))
    d=await pg.evaluate(PROMPT); ok('M1 explains choices', 'Continue addressing per previous sheets' in d and 'Manually address' in d and 'Re-auto address entire project' in d, d)
    await pg.screenshot(path=os.path.join(SH,TAG+'5-three-choice-modules.png'))
    await answer(pg,'continue')
    ok('M1 Continue: new modules on sheet 1 get 6, 7 (after last address on the network)', await pg.evaluate(ADDRS)==[['1','2','3','6','7'],['4','5']], await pg.evaluate(ADDRS))
    # Standalone sheet: continue on that sheet
    await fresh(pg); await pg.evaluate(BUILD,[{'scheme':'standalone','n':2,'addrs':[1,2]},{'scheme':'standalone','n':1,'addrs':[1]}]); await goto_sheet(pg,1); await ui_add(pg)
    await wait_title(pg,'Address the new modules?'); await answer(pg,'continue')
    ok('M2 Standalone sheet: continues on that sheet (2)', await pg.evaluate(ADDRS)==[['1','2'],['1','2']], await pg.evaluate(ADDRS))

    # ---- 5. SenseNET rollover with Continue: 125 on net 1, new 5-module sheet → SenseNET 2 from 1 + notice
    await fresh(pg); await pg.evaluate(BUILD,[{'n':25}]*5); await pg.evaluate("applyUnifiedAddressing('networked', true)"); await pg.wait_for_timeout(200); await close_prompt(pg)
    await pg.evaluate("ADDR_UNDO=null"); await new_sheet(pg); t0=__import__('time').time(); await pg.evaluate("(()=>{const l=document.querySelector('.location-current').dataset.loc;for(let i=0;i<5;i++)uiAddModule(l,'Detector')})()"); print('5 adds took', round(__import__('time').time()-t0,2),'s')
    t=await pg.evaluate(TITLE); ok('R1 SenseNET 2 infrastructure warning shown first (existing editing rule)', 'infrastructure' in await pg.evaluate(PROMPT), t); await close_prompt(pg)
    ok('R1 then the three-choice prompt (not stacked)', await wait_title(pg,'Address the new sheets?'), await pg.evaluate(TITLE)); await answer(pg,'continue')
    ok('R1 new sheet rolls to SenseNET 2, addresses 1..5', (await pg.evaluate(NETS))[-1]==2 and (await pg.evaluate(ADDRS))[-1]==['1','2','3','4','5'], [await pg.evaluate(NETS), (await pg.evaluate(ADDRS))[-1]])
    
    # whole-project re-auto with rollover (new build path)
    await fresh(pg); await pg.evaluate(BUILD,[{'n':26}]*5); await pg.evaluate("void promptAutoAddress('add', new Set())"); await wait_title(pg,'Networked or Standalone?')
    await answer(pg,'networked'); await answer(pg,'yes')
    ok('R2 re-auto rollover: sheet 5 on SenseNET 2 from 1', await pg.evaluate(NETS)==[1,1,1,1,2] and (await pg.evaluate(ADDRS))[4][0]=='1', await pg.evaluate(NETS)); await close_prompt(pg)

    # ---- 6. Mixed project: new sheet keeps default, note shown; banner still there
    await fresh(pg); await pg.evaluate(BUILD,[{'n':1,'addrs':[1]},{'scheme':'standalone','n':1,'addrs':[1]}]); await new_sheet(pg); await ui_add(pg)
    await wait_title(pg,'Address the new sheets?')
    ok('X1 mixed project: prompt mentions the Mixed addressing banner', 'Mixed addressing' in await pg.evaluate(PROMPT))
    await answer(pg,'manual'); ok('X1 banner still shown', await pg.evaluate("!document.getElementById('addr-mix-banner').hidden"))

    # ---- 7. No stacking: prompt waits while another prompt is open
    await fresh(pg); await pg.evaluate(BUILD,[{'n':1,'addrs':[1]}]); await goto_sheet(pg,0); await ui_add(pg)
    await pg.evaluate("void showPromptModal({title:'Other',desc:'x',buttons:[{label:'OK',value:1,primary:true}]})"); await pg.wait_for_timeout(1500)
    ok('S1 does not stack on another prompt', await pg.evaluate(TITLE)=='Other'); await answer(pg,'1')
    ok('S1 shows after the other prompt closes', await wait_title(pg,'Address the new modules?')); await answer(pg,'manual')

    # ---- 8. .pl import: new build (Confirm Settings? → mode → auto) and Revise import
    await fresh(pg); await to_finish(pg,[PLS[0]])
    ok('P1 Confirm Settings? first', await pg.evaluate(TITLE)=='Confirm Settings?'); await answer(pg,'confirm')
    ok('P1 then Networked or Standalone?', await wait_title(pg,'Networked or Standalone?'), await pg.evaluate(TITLE))
    await answer(pg,'networked'); ok('P1 then Auto address?', await pg.evaluate(TITLE)=='Auto address?')
    await answer(pg,'yes'); await close_prompt(pg)
    flat=sum(await pg.evaluate(ADDRS),[]); ok('P1 every module 1..N', flat and flat==[str(i) for i in range(1,len(flat)+1)], flat[:6])
    lg=await pg.evaluate(LOG); ok('P1 logged (after .pl import)', lg and 'import' in lg[-1]['action'], lg[-1:] and lg[-1]['action'])
    # existing project + second .pl import → three-choice, continue
    n1=len(flat); await to_finish(pg,[PLS[1]]); await answer(pg,'confirm')
    ok('P2 existing project + new .pl: three-choice prompt (sheets)', await wait_title(pg,'Address the new sheets?'), await pg.evaluate(TITLE))
    await answer(pg,'continue'); await close_prompt(pg)
    ad=await pg.evaluate(ADDRS); flat=sum(ad,[])
    ok('P2 continue: old 1..n kept, new sheets continue (net 1) or restart on a new network', flat[:n1]==[str(i) for i in range(1,n1+1)] and all(x for x in flat), (n1, flat[n1:n1+5], await pg.evaluate(NETS)))
    # Revise import → no auto prompt
    await fresh(pg); await to_finish(pg,[PLS[0]]); await answer(pg,'revise'); await pg.wait_for_timeout(600)
    ok('P3 Revise import: no auto-address prompt', await pg.evaluate(TITLE)=='' and await pg.evaluate("document.getElementById('plw-overlay').classList.contains('open')"), await pg.evaluate(TITLE))

    # ---- 9. Merge (Import Calc → Merge sheets) path
    await fresh(pg); await pg.evaluate(BUILD,[{'n':2,'addrs':[1,2]}])
    pre=await pg.evaluate("(()=>{window.__pre=aaRowIds();const l=document.querySelector('.location');addLocation();const ls=document.querySelectorAll('.location');addModuleRow(ls[ls.length-1].dataset.loc,'Detector');return 1})()")
    await pg.evaluate("void promptAutoAddress('merge', window.__pre)")
    ok('G1 merge: three-choice prompt', await wait_title(pg,'Address the new sheets?') and 'merged' in await pg.evaluate(PROMPT))
    await answer(pg,'continue'); ok('G1 merge continue → 3', await pg.evaluate(ADDRS)==[['1','2'],['3']], await pg.evaluate(ADDRS))
    ok('G1 merge path wired in handleImportFile', await pg.evaluate("handleImportFile.toString().includes(\"promptAutoAddress('merge', aaPre)\")"))
    ok('P* .pl path wired', await pg.evaluate("plFinish.toString().includes(\"promptAutoAddress('import', aaPre)\")"))

    rv=await pg.evaluate("typeof mlpCalcRev==='function'?mlpCalcRev():''"); ok('rev 02.01.000_261016 (Toolbox 00.02.000)', ('00.02.000' if TB else '02.01.000') in rv, rv)
    ok('no page errors', not errs, errs)
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())

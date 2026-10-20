# G1 (Brent, MLP 1.4.0): per-device SenseNET network Calc -> .mlproj -> Report; duplicates per network; >127 total OK if each network <= 127.
import asyncio, os, sys, json
from playwright.async_api import async_playwright
import os as _os, tempfile as _tf
MLP_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')
def _od(*p):
    d=_os.path.join(MLP_OUT,*p); _os.makedirs(d,exist_ok=True); return d.rstrip('/')+'/'
from test_sensenet import fresh, BUILD, NETS
APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
RPT=os.environ.get('RPT_URL','file:///workspace/ModuLaser-Commisioning-Report/index.html')
TAG='tb-' if 'Toolbox' in APP else ''; OUT=_od('g1'); SH=_od('shots-0204')
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:300])
EXPORT="(()=>{const d=MLP.blank();d.project=mlpProjectInfo();d.design=mlpBuildDesign();return MLP.stringify(d,'test',mlpCalcRev(),'QA')})()"
async def report_import(b, path):
    rp=await b.new_page(viewport={'width':1440,'height':900}); errs=[]; rp.on('pageerror',lambda e: errs.append(str(e))); rp.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    await rp.goto(RPT); await rp.evaluate('localStorage.clear()'); await rp.reload(); await rp.wait_for_function('typeof saveProject==="function"')
    await rp.evaluate("sessionStorage.setItem('mfr-technician','QA Tech')")
    await rp.set_input_files('#importProj', path); await rp.wait_for_selector('#dlg.show', timeout=15000)
    dlg=await rp.evaluate("document.getElementById('dlg').innerText"); dis=await rp.evaluate("document.getElementById('dlgApply').disabled")
    return rp, errs, dlg, dis
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1500,'height':1000}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    await fresh(pg)
    await pg.evaluate(BUILD, [{'n':26}]*5); await pg.evaluate("applyUnifiedAddressing('networked', true)"); await pg.wait_for_timeout(300)
    await pg.evaluate("document.getElementById('prompt-overlay').classList.remove('open')")
    ok('calc: 130 modules → SenseNET 1 + 2', await pg.evaluate(NETS)==[1,1,1,1,2], await pg.evaluate(NETS))
    txt=await pg.evaluate(EXPORT); doc=json.loads(txt); devs=doc['design']['devices']
    nets=[d.get('network') for d in devs]
    ok('.mlproj devices carry network (104 on 1, 26 on 2)', nets.count(1)==104 and nets.count(2)==26, (nets.count(1),nets.count(2)))
    ok('shared validator: no duplicate errors across networks', not await pg.evaluate("MLP.validateDesign(mlpBuildDesign()).length"), await pg.evaluate("MLP.validateDesign(mlpBuildDesign()).slice(0,2)"))
    ok('MLP 1.6.2 in the app', await pg.evaluate("MLP.VERSION")=='1.6.2')
    fp=OUT+TAG+'two-net.mlproj.json'; open(fp,'w').write(txt)
    rp,rerr,dlg,dis=await report_import(b, fp)
    ok('Report: 130-module 2-network design is not blocked', not dis and 'Import is blocked' not in dlg, dlg[:300])
    await rp.click('#dlgApply'); await rp.wait_for_timeout(1200)
    st=await rp.evaluate("JSON.parse(JSON.stringify(state.modules.map(m=>[m.net,m.sn])))")
    ok('Report: each module keeps its network', sum(1 for x in st if str(x[0])=='2')==26 and sum(1 for x in st if str(x[0])=='1')==104, st[:3])
    nd=await rp.evaluate("state.modules.filter(m=>evalIssues? false:false).length") if False else 0
    await rp.evaluate("state.ui.view='sec:C'; renderAll()"); await rp.wait_for_timeout(300)
    await rp.evaluate('renderIndex()'); idx=await rp.evaluate("[...document.querySelectorAll('table.idx')].map(t=>t.innerText).join(' ')+' rows:'+document.querySelectorAll('table.idx tbody tr').length")
    ok('Report Device Index shows the network per device', 'SN2' in idx and 'SN1' in idx and 'NET' in idx.upper(), idx[-250:])
    await rp.screenshot(path=SH+TAG+'report-network-index.png')
    dup=await rp.evaluate("(()=>{const m=state.modules.find(x=>String(x.net)==='2'&&x.sn==='1');return m?dupMsg(m):'nomod'})()")
    ok('Report: address 1 on SN1 and SN2 is not a duplicate', dup=='', dup)
    await rp.evaluate("(()=>{const a=state.modules.filter(x=>String(x.net)==='2');a[1].sn=a[0].sn})()")
    dup=await rp.evaluate("(()=>{const a=state.modules.filter(x=>String(x.net)==='2');return dupMsg(a[1])})()")
    ok('Report: same address twice on SN2 is a duplicate (names network)', 'SenseNET 2' in dup, dup)
    ok('Report: no page errors', not rerr, rerr); await rp.close()
    # single network over 127 still blocks
    d2=json.loads(txt); [d.__setitem__('network',1) for d in d2['design']['devices']]
    for i,d in enumerate(d2['design']['devices']): d['address']=str(i%127+1)
    fp2=OUT+TAG+'one-net-130.mlproj.json'; open(fp2,'w').write(json.dumps(d2))
    rp,rerr,dlg,dis=await report_import(b, fp2)
    ok('Report: 130 on one network is blocked (names SenseNET 1)', dis and 'SenseNET 1' in dlg, dlg[:300]); await rp.close()
    # older file (no network) → network 1
    d3=json.loads(txt); d3['design']['devices']=d3['design']['devices'][:5]
    for d in d3['design']['devices']: d.pop('network',None)
    fp3=OUT+TAG+'old.mlproj.json'; open(fp3,'w').write(json.dumps(d3))
    rp,rerr,dlg,dis=await report_import(b, fp3); await rp.click('#dlgApply'); await rp.wait_for_timeout(600)
    ok('Report: older file without network → SenseNET 1', all(str(x)=='1' for x in await rp.evaluate("state.modules.map(m=>m.net)")), await rp.evaluate("state.modules.map(m=>m.net)")); await rp.close()
    ok('calc: no page errors', not errs, errs)
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())

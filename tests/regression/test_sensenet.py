# 02.00.004 (Brent, decision #4 change): SenseNET networks of up to 127 modules; overflow starts network 2, 3...
import asyncio, os, sys, json
from playwright.async_api import async_playwright
import os as _os, tempfile as _tf
MLP_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')   # all generated output goes here (QA r3)
def _od(*p):
    d=_os.path.join(MLP_OUT,*p); _os.makedirs(d,exist_ok=True); return d.rstrip('/')+'/'
APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
TAG='tb-' if 'Toolbox' in APP else ''
SH=_od('shots-0204')+TAG
FX=_od('fixtures-0204')
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:400])
# spec: list of {scheme, n (module count), net?, addrs?}; rows: 1 Standard Display + (n-1) detectors
BUILD='''async (spec)=>{
  clearEntireDocument({clearHeaders:false}); const pre=[...document.querySelectorAll('.location')];
  for (const s of spec){ addLocation(); const all=document.querySelectorAll('.location'); const l=all[all.length-1]; const loc=l.dataset.loc;
    l.querySelector('.ps-name').value='PS-'+loc; l.querySelector('.ps-location').value='Riser '+loc;
    l.querySelector(`.addr-scheme-radio[value="${s.scheme||'networked'}"]`).checked=true;
    if (s.net) l.dataset.senseNet=String(s.net);
    const tb=l.querySelector('.devices-body'); let uid=0; const w=document.createElement('tbody');
    for (let i=0;i<s.n;i++){ uid++; w.innerHTML=buildModuleRow(loc,uid,i===0?'Standard Display':'Detector','',''); const r=w.firstElementChild; tb.appendChild(r);
      if (s.addrs) r.querySelector('.module-address').dataset.desiredValue=String(s.addrs[i]); }
    l.setAttribute('data-module-uid', uid);
  }
  pre.forEach(e=>e.remove()); window.__ambRe=false;
  updateNetworkAddressAvailability(); document.querySelectorAll('.location').forEach(l=>recalcLocationInner(l.dataset.loc)); refreshAllAmber(); v2Refresh();
  return [...document.querySelectorAll('.location')].map(l=>l.dataset.loc);
}'''
NETS="()=>[...document.querySelectorAll('.location')].map(l=>sheetSenseNet(l))"
ADDRS="()=>[...document.querySelectorAll('.location')].map(l=>[...l.querySelectorAll('[data-role=module] .module-address')].map(s=>s.value))"
FLAGS="()=>[...document.querySelectorAll('.location')].map(l=>[...l.querySelectorAll('.flags-list li')].filter(li=>!li.closest('[hidden]')).map(li=>li.textContent).filter(t=>/SenseNET|[Dd]uplicate|network limit/.test(t)))"
PROMPT="()=>document.getElementById('prompt-overlay').classList.contains('open')?document.getElementById('prompt-title').innerText+' | '+document.getElementById('prompt-desc').innerText:''"
async def fresh(pg):
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(700)
async def close_prompt(pg):
    if await pg.evaluate("document.getElementById('prompt-overlay').classList.contains('open')"):
        await pg.click('#prompt-actions .btn-primary'); await pg.wait_for_timeout(150)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    await fresh(pg)
    # 1) re-address 130 modules (5 sheets x 26) networked: net 1 = sheets 1-4 (104), net 2 = sheet 5 (sheet kept on one network)
    await pg.evaluate(BUILD, [{'n':26}]*5)
    ok('130-module fixture built', await pg.evaluate("document.querySelectorAll('[data-role=module]').length")==130)
    await pg.evaluate("applyUnifiedAddressing('networked', true)"); await pg.wait_for_timeout(300)
    nets=await pg.evaluate(NETS); ad=await pg.evaluate(ADDRS)
    ok('re-address: sheets 1-4 on SenseNET 1, sheet 5 on SenseNET 2', nets==[1,1,1,1,2], nets)
    ok('re-address: 1..104 on network 1, restarts 1..26 on network 2', sum(ad[:4],[])==[str(i) for i in range(1,105)] and ad[4]==[str(i) for i in range(1,27)], [ad[3][-1], ad[4][:3]])
    pt=await pg.evaluate(PROMPT)
    ok('user told a new network was added + infrastructure', 'SenseNET network 2' in pt and 'infrastructure' in pt, pt)
    await pg.screenshot(path=SH+'sensenet-added.png'); await close_prompt(pg)
    f=await pg.evaluate(FLAGS); ok('no duplicate/limit flags after re-address (same addresses on different networks allowed)', not any(f), f)
    # shown on the sheet + sidebar + print/Word settings
    await pg.evaluate("l=>{const it=[...document.querySelectorAll('.sb-item')].find(x=>x.dataset.loc==l); it&&it.click()}", (await pg.evaluate("[...document.querySelectorAll('.location')].map(l=>l.dataset.loc)"))[4]); await pg.wait_for_timeout(300)
    sv=await pg.evaluate("(()=>{const l=document.querySelector('.location-current');const s=l.querySelector('.sensenet-select');const w=s.closest('.sn-wrap');return [s.value, !!w.offsetParent, w.scrollWidth<=w.clientWidth+1 && (!w.querySelector('.calc-select-btn') || w.querySelector('.calc-select-btn').scrollWidth<=w.querySelector('.calc-select-btn').clientWidth), w.scrollWidth, w.clientWidth]})()")
    ok('sheet shows SenseNET network 2 (visible, not truncated)', sv[0]=='2' and sv[1] and sv[2], sv)
    sb=await pg.evaluate("[...document.querySelectorAll('.sb-item')].map(i=>i.innerText.replace(/\\s+/g,' '))")
    ok('sidebar tags sheets with their SenseNET network', all('SN1' in x for x in sb[:4]) and 'SN2' in sb[4], sb)
    await pg.screenshot(path=SH+'sensenet-sheet.png')
    st=await pg.evaluate("v2SheetModel(document.querySelector('.location-current')).settings")
    ok('print/Word settings: Addressing Networked · SenseNET 2', ['Addressing','Networked · SenseNET 2'] in st, st)
    ph=await pg.evaluate("v2BuildPrintHtml({scope:'all'})") if await pg.evaluate("typeof v2BuildPrintHtml==='function'") else ''
    ok('print output names SenseNET 2', 'SenseNET 2' in (ph if isinstance(ph,str) else json.dumps(ph)), '')
    import base64, zipfile, io
    for fn,part in [('v2BuildDocx','word/document.xml'),('v2BuildXlsx',None)]:
        b64=await pg.evaluate("(async(f)=>{const b=await window[f]({scope:'all',level:'standard'});const a=new Uint8Array(await b.arrayBuffer());let s='';for(const x of a)s+=String.fromCharCode(x);return btoa(s)})", fn)
        z=zipfile.ZipFile(io.BytesIO(base64.b64decode(b64))); txt=''.join(z.read(n).decode('utf8','ignore') for n in z.namelist() if n.endswith('.xml') and (part is None or n==part))
        ok(f'{fn} names SenseNET 2', 'SenseNET 2' in txt and 'SenseNET 1' in txt)
    # module table column rules unchanged (no new column)
    ok('module table still 9 columns', await pg.evaluate("document.querySelector('.location-current .devtable thead tr').children.length")==9)
    # 2) duplicates per network
    await pg.evaluate("()=>{const ls=[...document.querySelectorAll('.location')];const a=ls[4].querySelectorAll('[data-role=module] .module-address');a[1].value='';a[1].dataset.desiredValue='1';updateNetworkAddressAvailability();ls.forEach(l=>recalcLocationInner(l.dataset.loc))}")
    f=await pg.evaluate(FLAGS); ok('duplicate within SenseNET 2 flagged; network 1 sheets not flagged', f[4] and '1' in f[4][0] and 'SenseNET 2' in f[4][0] and not any(f[:4]), f)
    tk=await pg.evaluate("(()=>{const ls=[...document.querySelectorAll('.location')];const s=ls[4].querySelector('[data-role=module] .module-address');return [...s.options].filter(o=>o.disabled).map(o=>+o.value)})()")
    ok('SenseNET 2 dropdown: only network-2 addresses taken', 30 not in tk and 100 not in tk and 3 in tk, tk[:10])
    # 3) auto-split while editing: 127 on network 1, add one more module
    await pg.evaluate(BUILD, [{'n':26}]*4+[{'n':23}]); await pg.evaluate("applyUnifiedAddressing('networked', true)"); await pg.wait_for_timeout(200)
    ok('127 modules fit SenseNET 1', await pg.evaluate(NETS)==[1]*5 and not await pg.evaluate(PROMPT))
    await pg.evaluate("addModuleRow(document.querySelectorAll('.location')[4].dataset.loc,'Detector')"); await pg.wait_for_timeout(400)
    nets=await pg.evaluate(NETS); ad=await pg.evaluate(ADDRS); pt=await pg.evaluate(PROMPT)
    ok('128th module: last sheet moves to SenseNET 2 and is re-addressed 1..24', nets==[1,1,1,1,2] and ad[4]==[str(i) for i in range(1,25)], [nets, ad[4][:3], ad[4][-1:]])
    ok('notice: new network added, check infrastructure', 'SenseNET network 2' in pt and 'infrastructure' in pt, pt)
    await close_prompt(pg)
    # 4) persistence: state + .mlproj.json keep the network; older files default to 1
    st=await pg.evaluate("JSON.stringify(buildStateObject())")
    ok('state saves senseNet per sheet', [l.get('senseNet') for l in json.loads(st)['locations']]==[1,1,1,1,2])
    txt=await pg.evaluate("(()=>{const d=MLP.blank();d.project=mlpProjectInfo();d.design=mlpBuildDesign();return MLP.stringify(d,'test',mlpCalcRev(),'QA')})()")
    open(FX+'sensenet-128.mlproj.json','w').write(txt)
    await fresh(pg); await pg.evaluate("t=>mlpImportProjectText(t,'sensenet-128.mlproj.json')", txt); await pg.wait_for_timeout(800)
    ok('.mlproj.json import keeps SenseNET networks and addresses', await pg.evaluate(NETS)==[1,1,1,1,2] and (await pg.evaluate(ADDRS))[4][:2]==['1','2'])
    ok('no conflict notice for a valid 2-network import', not await pg.evaluate(PROMPT), await pg.evaluate(PROMPT))
    old=json.loads(st); [l.pop('senseNet',None) for l in old['locations']]
    await fresh(pg); await pg.evaluate("s=>applyLoadedState(JSON.parse(s))", json.dumps(old)); await pg.wait_for_timeout(800)
    ok('older file without senseNet: every sheet on network 1, addresses kept (no auto move on import)', await pg.evaluate(NETS)==[1]*5 and (await pg.evaluate(ADDRS))[4][:2]==['1','2'])
    pt=await pg.evaluate(PROMPT)
    ok('import notice: SenseNET 1 over 127 + duplicates, offers moving overflow', '128' in pt and 'SenseNET' in pt, pt)
    await pg.screenshot(path=SH+'sensenet-import-overflow.png')
    btn=await pg.evaluate("[...document.querySelectorAll('#prompt-actions button')].map(b=>b.textContent)")
    ok('import notice has a "Move overflow to a new SenseNET network" action', any('new SenseNET' in t for t in btn), btn)
    f=await pg.evaluate(FLAGS); ok('over-limit flag on network-1 sheets', all(any('128' in t for t in x) for x in f), f[0])
    await pg.locator('#prompt-actions button', has_text='new SenseNET').click(); await pg.wait_for_timeout(400)
    ok('move overflow: last sheet to SenseNET 2, re-addressed', await pg.evaluate(NETS)==[1,1,1,1,2] and (await pg.evaluate(ADDRS))[4]==[str(i) for i in range(1,25)])
    await close_prompt(pg)
    f=await pg.evaluate(FLAGS); ok('no flags after moving overflow', not any(f), f)
    # 5) standalone unchanged; manual network change re-validates
    await pg.evaluate(BUILD, [{'n':2,'addrs':[1,2]},{'n':2,'addrs':[1,2]},{'scheme':'standalone','n':2,'addrs':[1,2]}])
    f=await pg.evaluate(FLAGS); ok('two network-1 sheets sharing 1,2 flagged; standalone not', f[0] and f[1] and not f[2], f)
    await pg.evaluate("(()=>{const l=document.querySelectorAll('.location')[1];const s=l.querySelector('.sensenet-select');s.value='2';s.dispatchEvent(new Event('change'))})()"); await pg.wait_for_timeout(300)
    f=await pg.evaluate(FLAGS); ok('moving sheet 2 to SenseNET 2 by hand clears the duplicate', not any(f), f)
    ok('standalone sheet has no SenseNET selector shown', not await pg.evaluate("!!document.querySelectorAll('.location')[2].querySelector('.sn-wrap').offsetParent"))
    ok('no page errors', not errs, errs)
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
if __name__=="__main__": asyncio.run(main())

# QA r3 H1: an empty (no-module) sheet shows Incomplete for battery Ah everywhere; no battery/PSU recommendation; .mlproj requiredAh null + incomplete.
import asyncio, os, sys, re, json, base64, zipfile, io, tempfile
from playwright.async_api import async_playwright
from test_sensenet import fresh
import os as _os, tempfile as _tf
MLP_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')   # all generated output goes here (QA r3)
def _od(*p):
    d=_os.path.join(MLP_OUT,*p); _os.makedirs(d,exist_ok=True); return d.rstrip('/')+'/'

APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
TAG='tb-' if 'Toolbox' in APP else ''
OUT=_od('empty-incomplete')
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:300])
AHRE=re.compile(r'\b\d+\.\d+\s*Ah\b')
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1500,'height':1000}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    await fresh(pg)
    await pg.evaluate("(()=>{const l=getCurrentLocationEl();const b=l.querySelector('.design-basis-select');b.value='NFPA 72 Voice';applyDesignBasis(l.dataset.loc);l.querySelector('.temperature-select').value='77';recalcLocation(l.dataset.loc);v2Refresh()})()"); await pg.wait_for_timeout(300)
    card=await pg.evaluate("(()=>{const l=getCurrentLocationEl();return ['.standby-ah','.alarm-ah','.initial-ah','.required-ah'].map(s=>{const e=l.querySelector(s);return e?e.textContent.trim():null})})()")
    ok('sheet results card: Ah cells say Incomplete', all(c is None or c=='\u26a0 Incomplete' for c in card) and '\u26a0 Incomplete' in card, card)   # 02.00.005: amber + ⚠
    rec=await pg.evaluate("(()=>{const l=getCurrentLocationEl();return [l.classList.contains('recommendations-withheld'), (l.querySelector('.cd-battery-model-detail')||{}).textContent||'']})()")
    ok('no battery/PSU recommendation for an empty sheet', rec[0] and not re.search(r'12V|\d+\s*Ah', rec[1]), rec)
    m=await pg.evaluate("(()=>{const m=v2SheetModel(getCurrentLocationEl());return [m.status,m.requiredAh,m.batteryAh,m.batteryLabel]})()")
    ok('model: status INCOMPLETE, no Ah, battery label Incomplete', m[0]=='incomplete' and (m[1] is None or m[1]!=m[1]) and not m[2] and 'Incomplete' in m[3], m)
    ph=await pg.evaluate("(()=>{const h=v2BuildPrintHtml({scope:'all',level:'full'});return typeof h==='string'?h:JSON.stringify(h)})()")
    pt=re.sub('<[^>]+>',' ',ph)
    ok('print: Incomplete, no Ah figure for the sheet, no PASS', 'Incomplete' in pt and not AHRE.search(pt.replace('65 Ah','')) and 'PASS ' not in pt.split('PASS:')[0], AHRE.findall(pt)[:4])
    open(os.path.join(OUT,TAG+'empty-print.html'),'w').write(ph)
    for fn,part in [('v2BuildDocx','word/document.xml'),('v2BuildXlsx',None)]:
        for lvl in ['summary','standard','full']:
            b64=await pg.evaluate("(async([f,l])=>{const b=await window[f]({scope:'all',level:l});const a=new Uint8Array(await b.arrayBuffer());let s='';for(const x of a)s+=String.fromCharCode(x);return btoa(s)})", [fn,lvl])
            z=zipfile.ZipFile(io.BytesIO(base64.b64decode(b64))); txt=' '.join(re.sub('<[^>]+>',' ',z.read(n).decode('utf8','ignore')) for n in z.namelist() if n.endswith('.xml') and (part is None or n==part))
            ok(f'{fn} {lvl}: Incomplete, no 2.12 / Ah figure', 'Incomplete' in txt and '2.12' not in txt and not AHRE.search(txt.replace('65 Ah','')), AHRE.findall(txt)[:3])
    d=json.loads(await pg.evaluate("JSON.stringify(mlpBuildDesign().psus)"))
    ok('.mlproj: empty sheet PSU model and enclosure blank (no "Incomplete" text)', d[0]['model']=='' and d[0]['enclosure']=='', [d[0]['model'], d[0]['enclosure']])
    ok('.mlproj: requiredAh null, incomplete flag, no battery', d and d[0]['requiredAh'] is None and d[0].get('incomplete') is True and not d[0]['battery']['ah'] and not d[0]['battery']['model'], d[0])
    # Report import handles it (shared helper)
    r=await pg.evaluate("(()=>{const doc=MLP.blank();doc.project=mlpProjectInfo();doc.design=mlpBuildDesign();const v=MLP.validateDesign?MLP.validateDesign(doc.design):null;return {v:v, row: MLP.psuRow?MLP.psuRow(doc.design.psus[0]):null}})()")
    ok('shared MLP.validateDesign accepts it without errors about Ah', r['v'] is None or not any('Ah' in str(x) for x in (r['v'].get('errors',[]) if isinstance(r['v'],dict) else r['v'])), r)
    # real Report import of a file with one empty sheet + one populated sheet
    await pg.evaluate("addLocation()"); await pg.wait_for_timeout(300)
    await pg.evaluate("(()=>{const l=document.querySelectorAll('.location')[1];addModuleRow(l.dataset.loc,'Detector');const r=l.querySelector('[data-role=module]');r.querySelector('.zone-name').value='Z1';const a=r.querySelector('.module-address');a.dataset.desiredValue='1';updateNetworkAddressAvailability();recalcLocation(l.dataset.loc)})()"); await pg.wait_for_timeout(300)
    txt=await pg.evaluate("(()=>{const d=MLP.blank();d.project=mlpProjectInfo();d.design=mlpBuildDesign();return MLP.stringify(d,'test',mlpCalcRev(),'QA')})()")
    fp=os.path.join(OUT,TAG+'empty-sheet.mlproj.json'); open(fp,'w').write(txt)
    rp=await b.new_page(); rerr=[]; rp.on('pageerror',lambda e: rerr.append(str(e))); ral=[]; rp.on('dialog',lambda d: (ral.append(d.message), asyncio.ensure_future(d.accept())))
    await rp.goto(os.environ.get('RPT_URL','file:///workspace/ModuLaser-Commisioning-Report/index.html')); await rp.evaluate('localStorage.clear()'); await rp.reload(); await rp.wait_for_function('typeof saveProject==="function"'); await rp.evaluate("sessionStorage.setItem('mfr-technician','QA Tech')")
    await rp.set_input_files('#importProj', fp); await rp.wait_for_timeout(1500); print('report alerts', ral, rerr)
    await rp.wait_for_selector('#dlg.show', timeout=10000)
    dlg=await rp.evaluate("document.getElementById('dlg').innerText"); await rp.click('#dlgApply'); await rp.wait_for_timeout(800)
    ps=await rp.evaluate("JSON.parse(JSON.stringify(state.psus.map(p=>({n:p.label||p.name,req:p.reqAh==null?'':String(p.reqAh),model:p.model||''}))))")
    ok('Report: empty sheet PSU model field is blank', ps and ps[0]['model']=='', ps[:1])
    ok('Report imports the empty-sheet file gracefully (no errors, empty sheet has no required Ah)', not rerr and 'NaN' not in dlg and len(ps)>=2 and ps[0]['req']=='' and not any(x['req'] in ('NaN','null') for x in ps), [rerr, ps, dlg[:150]])
    await rp.close()
    # adding a module brings the figure back
    await pg.evaluate("addModuleRow(getCurrentLocationEl().dataset.loc,'Detector');v2Refresh()"); await pg.wait_for_timeout(300)
    ok('with a module the Ah figure returns', re.search(r'\d', await pg.evaluate("getCurrentLocationEl().querySelector('.required-ah').textContent")))
    ok('no page errors', not errs, errs)
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())

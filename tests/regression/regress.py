# Same manual scenario on main (01.05.009) and the branch build: results must match.
import asyncio, json, subprocess
from playwright.async_api import async_playwright
import os as _os, tempfile as _tf
MLP_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')   # all generated output goes here (QA r3)
def _od(*p):
    d=_os.path.join(MLP_OUT,*p); _os.makedirs(d,exist_ok=True); return d.rstrip('/')+'/'

subprocess.run('cd /workspace/ModuLaser-Battery-Calculator && git show main:modulaser_battery_calculator.html > '+_od('plbuild')+'base.html',shell=True,check=True)
URLS={'base':'file://'+_od('plbuild')+'base.html','new':'file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html'}
SCEN=[('NFPA 72 Voice','77','0.25',[5,9]),('BS 5839-1 Category M/L','50','0.25',[16,16,3]),('UFC 3-600-01 FA/MNS','32','0.30',[12])]
JS='''async ([basis,temp,margin,fans])=>{
 const loc=document.querySelector('.location'); const id=loc.dataset.loc;
 const bs=loc.querySelector('.design-basis-select'); bs.value=basis; applyDesignBasis(id);
 loc.querySelector('.temperature-select').value=temp; loc.querySelector('.margin-select').value=margin;
 if(!loc.querySelector('[data-role=module]')){ addModuleRow(id,'Standard Display'); addModuleRow(id,'Detector'); addModuleRow(id,'Detector'); } // 02.00.004: sheets start empty; seed the old starter rows
 const rows=[...loc.querySelectorAll('[data-role=module]')]; while(rows.length-1<fans.length){ addModuleRow(id,'Detector'); rows.length=0; rows.push(...loc.querySelectorAll('[data-role=module]')); }
 fans.forEach((f,i)=>{const r=rows[i+1]; r.querySelector('.fanspeed-select').value=String(f);});
 rows[0].querySelector('.module-address').value='1'; rows.slice(1).forEach((r,i)=>{r.querySelector('.module-address').value=String(i+2)});
 recalcLocation(id); recalcLocationInner(id);
 const t=s=>{const e=loc.querySelector(s); return e?e.textContent.trim():null};
 return {standby:t('.standby-ah'),alarm:t('.alarm-ah'),initial:t('.initial-ah'),required:t('.required-ah'),flags:t('.flags-list'),bom:buildBOM(loc).map(r=>r.partNumber+'x'+r.qty).join(',')};}'''
async def main():
    out={}
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for k,u in URLS.items():
            out[k]=[]
            for sc in SCEN:
                pg=await b.new_page(); await pg.goto(u); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(300)
                out[k].append(await pg.evaluate(JS,list(sc))); await pg.close()
        await b.close()
    for i,sc in enumerate(SCEN):
        same=out['base'][i]==out['new'][i]
        print('PASS' if same else 'FAIL','regression',sc[0],json.dumps(out['new'][i])[:220])
        if not same: print(' base',out['base'][i])
asyncio.run(main())

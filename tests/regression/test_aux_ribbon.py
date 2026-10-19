"""02.01.001 (Brent 10-19 12:23 / 12:53 PM CT): modules on their own AUX circuit (no ribbon) are never ribbon runs; each ribbon run is
max 4 Detector Modules + 1 display; no per-cluster run cap (old '2 ribbon portions' rule removed). Run: python3 tests/regression/test_aux_ribbon.py (APP=<file url> for the Toolbox)"""
import asyncio, os
from playwright.async_api import async_playwright
APP = os.environ.get('APP', 'file://' + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'modulaser_battery_calculator.html')))
# plan: list of power choices per detector: 'own' or index of entry (-1 = display, k = detector k)
JS = r'''async ([plan, auto, n])=>{ clearEntireDocument({clearHeaders:false}); const pre=[...document.querySelectorAll('.location')]; addLocation();
  const l=[...document.querySelectorAll('.location')].pop(), loc=l.dataset.loc; pre.forEach(e=>e.remove()); l.querySelector('.ps-name').value='PS-1';
  const set=(el,v)=>{ el.value=v; el.dispatchEvent(new Event('change',{bubbles:true})); };
  const ram=l.querySelector('.ribbon-assign-mode'); if(ram){ ram.value= auto?'auto':'off'; }
  const cnt = plan ? plan.length : n;
  addModuleRow(loc,'Standard Display'); for(let i=0;i<cnt;i++) addModuleRow(loc,'Detector'); recalcLocationInner(loc);
  const R=()=>[...l.querySelectorAll('[data-role=module]')]; const D=R().find(r=>r.querySelector('.type-select').value!=='Detector'); const T=R().filter(r=>r.querySelector('.type-select').value==='Detector');
  set(D.querySelector('.cluster-select'),'1'); set(D.querySelector('.module-address'),'1'); D.querySelector('.zone-name').value='D1'; recalcLocationInner(loc);
  T.forEach((t,i)=>{ set(t.querySelector('.cluster-select'),'1'); set(t.querySelector('.module-address'),String(i+2)); t.querySelector('.zone-name').value='T'+(i+1); set(t.querySelector('.fanspeed-select'),'16'); });
  recalcLocationInner(loc);
  if(plan){ for(let pass=0;pass<2;pass++){ T.forEach((t,i)=>{ const p=plan[i]; const ps=t.querySelector('.power-select'); const v = p==='own' ? 'own' : 'follow:'+(p===-1?D.id:T[p].id); if([...ps.options].some(o=>o.value===v)) set(ps,v); }); recalcLocationInner(loc); } }
  recalcLocation(loc); await new Promise(r=>setTimeout(r,300));
  const flags=[...l.querySelectorAll('.flags-list li')].filter(x=>!x.closest('[hidden]')).map(x=>x.textContent);
  return { flags, power: T.map(t=>t.querySelector('.power-select').value.replace(/follow:.*/,'f')), aux: T.map(t=>t.querySelector('.aux-circuit-num').value) }; }'''
R = []
def ok(n, c, i=''): R.append(bool(c)); print('PASS' if c else 'FAIL', n, str(i)[:300])
def over(f): return [x for x in f if 'exceeds 2' in x or 'non-distributed' in x]
def run(f): return [x for x in f if x.startswith('Ribbon run exceeds')]
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(700)
    A = await pg.evaluate(JS, [['own','own','own'], False, 0])
    ok('A: display + 3 detectors each on own AUX -> no ribbon error', not over(A['flags']) and not run(A['flags']) and A['power']==['own']*3, A)
    B = await pg.evaluate(JS, [[-1,'own',1,'own'], False, 0])
    ok('B: hybrid (display+follower, D2+follower, D4 own AUX) -> no error', not over(B['flags']) and not run(B['flags']), B)
    C = await pg.evaluate(JS, [[-1,'own',1,'own',3], False, 0])
    ok('C: 3 ribbon runs in one cluster -> allowed now (no 2-portion error)', not over(C['flags']) and not run(C['flags']), C)
    F = await pg.evaluate(JS, [[-1,-1,-1,-1], False, 0])
    ok('F: display + 4 detectors on one run -> OK', not run(F['flags']), F)
    H = await pg.evaluate(JS, [[-1,-1,-1,-1,-1], False, 0])
    ok('H: display + 5 detectors on one run -> run error', len(run(H['flags']))==1 and '5 Detector Modules + 1 display' in run(H['flags'])[0], H['flags'])
    G = await pg.evaluate(JS, [['own',0,0,0,0], False, 0])
    ok('G: detector-led run of 5 detectors -> run error', len(run(G['flags']))==1 and '(5 Detector Modules)' in run(G['flags'])[0], G['flags'])
    G2 = await pg.evaluate(JS, [['own',0,0,0], False, 0])
    ok('G2: detector-led run of 4 detectors -> OK', not run(G2['flags']), G2['flags'])
    Dd = await pg.evaluate(JS, [None, True, 8])
    ok('D: Auto, 8 detectors -> runs of <=4 detectors, no ribbon error', not over(Dd['flags']) and not run(Dd['flags']) and Dd['power'].count('own')==1, Dd)
    E = await pg.evaluate(JS, [['own','own','own','own'], False, 0])
    ok('E: 5th entry point on a 4-AUX supply still gets no circuit', E['aux'][-1]=='' and E['aux'][:3]==['2','3','4'], E['aux'])
    K = await pg.evaluate(JS, [None, True, 9])
    ok('K: 9 detectors on 1 display -> cluster-total check still fires', any('maximum number of detectors' in x for x in K['flags']), K['flags'])
    ok('no page errors', not errs, errs)
    await b.close()
  print(f"{sum(R)}/{len(R)} passed"); raise SystemExit(0 if all(R) else 1)
asyncio.run(main())

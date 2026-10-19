"""02.01.001 (Brent 10-19 12:23 PM CT): modules on their own AUX circuit (no ribbon followers) are not ribbon portions; the
2-ribbon-portion cap counts only ribbon-connected portions. Run: python3 tests/regression/test_aux_ribbon.py (APP=<file url> for the Toolbox)"""
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
def over(f): return [x for x in f if 'exceeds 2' in x and ('ribbon' in x)]
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(700)
    A = await pg.evaluate(JS, [['own','own','own'], False, 0])
    ok('A: display + 3 detectors each on own AUX -> no 2-ribbon-portion error', not over(A['flags']) and A['power']==['own']*3, A)
    B = await pg.evaluate(JS, [[-1,'own',1,'own'], False, 0])
    ok('B: hybrid (display+follower, D2+follower, D4 own AUX) -> no error', not over(B['flags']), B)
    C = await pg.evaluate(JS, [[-1,'own',1,'own',3], False, 0])
    ok('C: 3 real ribbon portions -> error still shown', len(over(C['flags']))==1, C)
    ok('C: error text no longer calls them "distributed"/"non-distributed"', over(C['flags']) and 'distributed' not in over(C['flags'])[0], over(C['flags']))
    Dd = await pg.evaluate(JS, [None, True, 8])
    ok('D: Auto, 8 detectors -> no ribbon-portion error, max 4 followers per entry', not over(Dd['flags']), Dd)
    E = await pg.evaluate(JS, [['own','own','own','own'], False, 0])
    ok('E: 5th entry point on a 4-AUX supply still gets no circuit', E['aux'][-1]=='' and E['aux'][:3]==['2','3','4'], E['aux'])
    ok('no page errors', not errs, errs)
    await b.close()
  print(f"{sum(R)}/{len(R)} passed"); raise SystemExit(0 if all(R) else 1)
asyncio.run(main())

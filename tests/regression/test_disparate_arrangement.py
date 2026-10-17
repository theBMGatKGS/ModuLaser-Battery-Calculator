"""02.01.000 (Brent 10-16 9:02 PM): a sheet with 2+ clusters (third-party supply: AUX per entry point unknown) shows the 'Disparate clusters must not share power pathways' warning AND the
Recommended Power Supply Arrangement card (not withheld). Run: python3 tests/regression/test_disparate_arrangement.py (APP=<file url> for the Toolbox)"""
import asyncio, os, sys
from playwright.async_api import async_playwright
APP = os.environ.get('APP', 'file://' + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'modulaser_battery_calculator.html')))
JS = r'''async ()=>{ const W=ms=>new Promise(r=>setTimeout(r,ms)); clearEntireDocument({clearHeaders:false}); const pre=[...document.querySelectorAll('.location')]; addLocation();
  const l=[...document.querySelectorAll('.location')].pop(), loc=l.dataset.loc; pre.forEach(e=>e.remove()); l.querySelector('.ps-name').value='PS-1';
  const set=(el,v)=>{ el.value=v; el.dispatchEvent(new Event('change',{bubbles:true})); };
  addModuleRow(loc,'Standard Display'); addModuleRow(loc,'Standard Display'); addModuleRow(loc,'Detector'); addModuleRow(loc,'Detector'); recalcLocationInner(loc);
  const R=()=>[...l.querySelectorAll('[data-role=module]')]; const Ds=()=>R().filter(r=>r.querySelector('.type-select').value!=='Detector'), Ts=()=>R().filter(r=>r.querySelector('.type-select').value==='Detector');
  Ds().forEach((d,i)=>{ set(d.querySelector('.cluster-select'), String(i+1)); set(d.querySelector('.module-address'), String(i+1)); d.querySelector('.zone-name').value='D'+(i+1); }); recalcLocationInner(loc);
  Ts().forEach((t,i)=>{ set(t.querySelector('.cluster-select'), String(i+1)); }); recalcLocationInner(loc);
  Ts().forEach((t,i)=>{ const d=Ds()[i]; const ps=t.querySelector('.power-select'); const o=[...ps.options].find(o=>o.value==='follow:'+d.id); if(o) set(ps,o.value); set(t.querySelector('.module-address'), String(i+3)); t.querySelector('.zone-name').value='T'+(i+1); set(t.querySelector('.fanspeed-select'),'16'); });
  l.querySelector('.mode-radio[value=thirdparty]').checked=true; const ah=l.querySelector('.tp-battery-ah'); ah.disabled=false; ah.value='40'; const ac=l.querySelector('.aux-circuits-custom'); if(ac){ac.disabled=false; ac.value='4';} recalcLocationInner(loc);
    recalcLocationInner(loc); recalcLocation(loc); await W(300);
  const vm=v2SheetModel(l); const ab=l.querySelector('.arrangement-block');
  const t=ab.hidden?null:ab.querySelector('.arrangement-list').innerText; return {t, flags: vm.flags, btn: !!(ab.querySelector('button')&&!ab.querySelector('button').disabled)}; }'''
R = []
def ok(n, c, i=''): R.append(bool(c)); print('PASS' if c else 'FAIL', n, str(i)[:300])
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(700)
    r = await pg.evaluate(JS); t = r['t'] or ''
    ok('warning shown', any(x.startswith('Disparate clusters must not share power pathways') for x in r['flags']), r['flags'])
    ok('only that warning is present (no other flags)', len(r['flags']) == 1, r['flags'])
    ok('arrangement card shown with 2 arrangements, not withheld', 'Arrangement 1' in t and 'Arrangement 2' in t and 'withheld' not in t, t[:200])
    ok('export button enabled', r['btn'])
    ok('no MiniLaser row without MiniLasers', 'MiniLasers' not in t)
    # QA F8: Edwards A/BPS mode knows each entry point's AUX circuit (unique per entry point; ribbons stay within a cluster) -> clusters can't share a pathway, no flag
    B = await pg.evaluate("""()=>{ const l=[...document.querySelectorAll('.location')].pop(), loc=l.dataset.loc;
      l.querySelector('.mode-radio[value=builtin]').checked=true; recalcLocationInner(loc); recalcLocation(loc);
      const F=()=>[...l.querySelectorAll('.flags-list li')].filter(li=>!li.closest('[hidden]')).map(li=>li.textContent).some(t=>t.startsWith('Disparate clusters'));
      const ent=[...l.querySelectorAll('[data-role=module]')].filter(r=>r.querySelector('.type-select').value!=='Detector').map(r=>r.querySelector('.aux-circuit-num'));
      const auto=ent.map(a=>a.value); const r1=F();
      const set=(el,v)=>{ el.value=v; el.dispatchEvent(new Event('change',{bubbles:true})); };
      set(ent[0],'1'); set(ent[1],'2'); recalcLocationInner(loc); recalcLocation(loc); const r2=F();
      set(ent[1],'1'); recalcLocationInner(loc); recalcLocation(loc); const r3=F(); return [auto, r1, r2, r3, ent.map(a=>a.value)]; }""")
    ok('A/BPS: auto AUX gives each cluster its own circuit -> no disparate-clusters flag', B[0][0] != B[0][1] and B[1] is False, B)
    ok('A/BPS: clusters on separate AUX circuits -> no flag', B[2] is False, B)
    ok('A/BPS: a second cluster cannot take an AUX circuit already used (unique per entry point), so no shared pathway and no flag', B[3] is False and B[4][0] != B[4][1], B)
    ok('no page errors', not errs, errs[:3])
    await b.close()
  print(f"{sum(R)}/{len(R)} passed"); sys.exit(0 if all(R) else 1)
asyncio.run(main())

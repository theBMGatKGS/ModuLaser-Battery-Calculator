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
    r = await pg.evaluate(JS)
    ST = """(loc)=>{ const l=document.getElementById('location-'+loc); const m=v2SheetModel(l); const li=[...l.querySelectorAll('.flags-list li')].filter(x=>!x.closest('[hidden]'));
      const red=l.querySelector('.reduce-supplies-block'); const ab=l.querySelector('.arrangement-block'); const bomT=l.querySelector('.bom-table tbody, .bom-body, [class*=bom] tbody');
      return { flags: li.map(x=>x.textContent), adv: li.map(x=>x.classList.contains('flag-advisory')), withheld: l.classList.contains('recommendations-withheld'), status: m.status, dot: m.dot, bom: !!m.bom,
        reduce: red && !red.hidden ? red.innerText : '', card: ab && !ab.hidden ? ab.querySelector('.arrangement-list').innerText : '', btn: !!(ab && ab.querySelector('button') && !ab.querySelector('button').disabled),
        bomScreen: bomT ? bomT.innerText : '', psRequired: l.querySelector('.ps-required') ? l.querySelector('.ps-required').textContent : '' }; }"""
    loc = r['loc'] if isinstance(r, dict) and 'loc' in r else await pg.evaluate("[...document.querySelectorAll('.location')].pop().dataset.loc")
    A = await pg.evaluate(ST, loc)
    # (1) third-party, 2 clusters, 2 supplies required: the disparate message is an advisory WARNING only
    ok('third-party 2 clusters: disparate warning shown, labelled "Warning:" and marked advisory', len(A['flags']) == 1 and A['flags'][0].startswith('Warning: Disparate clusters must not share power pathways') and A['adv'] == [True], A['flags'])
    ok('advisory only → recommendations not withheld, sheet dot not "error"', not A['withheld'] and A['dot'] != 'error', [A['withheld'], A['dot']])
    ok('no "Recommendation withheld" banner above the card', 'withheld' not in A['reduce'].lower(), A['reduce'][:160])
    ok('arrangement card shown (2 arrangements), export enabled', 'Arrangement 1' in A['card'] and 'Arrangement 2' in A['card'] and 'withheld' not in A['card'] and A['btn'], A['card'][:160])
    ok('BOM shown when the card is shown (model + on-screen table, not withheld)', A['bom'] and 'withheld' not in A['bomScreen'].lower(), A['bomScreen'][:160])
    ok('no MiniLaser row without MiniLasers', 'MiniLasers' not in A['card'])
    # (1b) same sheet with a big enough battery (1 supply): the sheet PASSES with the warning
    P = await pg.evaluate("""(loc)=>{ const l=document.getElementById('location-'+loc); const ah=l.querySelector('.tp-battery-ah'); ah.disabled=false; ah.value='200'; const bs=l.querySelector('.design-basis-select'); bs.value=[...bs.options].map(o=>o.value).find(v=>/NFPA 72 Voice/.test(v))||bs.options[1].value; applyDesignBasis(loc); l.querySelector('.temperature-select').value='77'; l.querySelectorAll('.fanspeed-select').forEach(x=>{ if(x.closest('tr').querySelector('.type-select').value==='Detector'){ x.value='1'; } }); recalcLocationInner(loc); recalcLocation(loc); }""", loc)
    P = await pg.evaluate(ST, loc)
    ok('1 supply + only the disparate warning → status PASS, BOM shown, warning still listed', P['status'] == 'pass' and P['bom'] and not P['withheld'] and any('Disparate clusters' in x for x in P['flags']), {k: P[k] for k in ('status', 'bom', 'withheld', 'psRequired', 'flags')} | {'ah': await pg.evaluate("(loc)=>document.querySelector('#location-'+loc+' .required-ah').textContent", loc)})
    # (2) Edwards A/BPS: AUX is unique per entry point and ribbons stay in their cluster → no disparate warning (dead shared-pathway branch removed)
    B = await pg.evaluate("""(loc)=>{ const l=document.getElementById('location-'+loc);
      l.querySelector('.mode-radio[value=builtin]').checked=true; recalcLocationInner(loc); recalcLocation(loc);
      const F=()=>[...l.querySelectorAll('.flags-list li')].filter(li=>!li.closest('[hidden]')).map(li=>li.textContent).some(t=>t.includes('Disparate clusters'));
      const ent=[...l.querySelectorAll('[data-role=module]')].filter(r=>r.querySelector('.type-select').value!=='Detector').map(r=>r.querySelector('.aux-circuit-num'));
      const set=(el,v)=>{ el.value=v; el.dispatchEvent(new Event('change',{bubbles:true})); };
      const r1=F(), auto=ent.map(a=>a.value); set(ent[1], ent[0].value); recalcLocationInner(loc); recalcLocation(loc); return [r1, auto, F(), ent.map(a=>a.value), [...ent[1].options].filter(o=>o.disabled).map(o=>o.value)]; }""", loc)
    ok('A/BPS 2 clusters: no disparate warning; each cluster gets its own AUX circuit', B[0] is False and B[1][0] != B[1][1], B)
    ok('A/BPS: a circuit already used is disabled for the other entry point, so a shared pathway is impossible', B[2] is False and B[3][0] != B[3][1] and B[3][0] in B[4], B)
    ok('no page errors', not errs, errs[:3])
    await b.close()
  print(f"{sum(R)}/{len(R)} passed"); sys.exit(0 if all(R) else 1)
asyncio.run(main())

"""02.02.000 QA build review (F4, F8): app-level Auto never picks 12V6A5 (C1 #58); a ribbon run can never hold two displays;
a display placed after a detector-started run starts its own run (it never follows); AUX 1–4 are per power supply = per sheet,
and a built-in sheet is always one supply (a load needing >1 supply is a validation failure, never a silent second supply).
Run: python3 tests/regression/test_0202_qa.py (APP=<file url> for the Toolbox)"""
import asyncio, os, sys
from playwright.async_api import async_playwright
APP = os.environ.get('APP', 'file://' + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'modulaser_battery_calculator.html')))
R = []
def ok(n, c, i=''): R.append(bool(c)); print('PASS' if c else 'FAIL', n, str(i)[:300])
SHEET = r'''([types, fresh])=>{ const pre=[...document.querySelectorAll('.location')]; addLocation(); const l=[...document.querySelectorAll('.location')].pop(), loc=l.dataset.loc; if (fresh) pre.forEach(e=>e.remove());
  l.querySelector('.ps-name').value='PS-'+loc; types.forEach(t=>addModuleRow(loc,t)); recalcLocationInner(loc);
  const set=(el,v)=>{ el.value=v; el.dispatchEvent(new Event('change',{bubbles:true})); };
  [...l.querySelectorAll('[data-role=module]')].forEach((r,i)=>{ set(r.querySelector('.cluster-select'),'1'); set(r.querySelector('.module-address'),String(i+1+100*(document.querySelectorAll('.location').length-1)%120)); r.querySelector('.zone-name').value='Z'+(i+1); const f=r.querySelector('.fanspeed-select'); if(f && !f.hidden) set(f,'8'); });
  recalcLocationInner(loc); recalcLocation(loc); return loc; }'''
INFO = r'''(loc)=>{ const l=document.getElementById('location-'+loc); const rows=[...l.querySelectorAll('[data-role=module]')];
  return { types: rows.map(r=>r.querySelector('.type-select').value), power: rows.map(r=>r.querySelector('.power-select').value.replace(/follow:.*/,'f')),
    opts: rows.map(r=>[...r.querySelector('.power-select').options].map(o=>o.value.replace(/follow:.*/,'f'))), aux: rows.map(r=>(r.querySelector('.aux-circuit-num')||{}).value||''),
    flags: [...l.querySelectorAll('.flags-list li')].filter(x=>!x.closest('[hidden]')).map(x=>x.textContent), status: v2SheetModel(l).status,
    batt: l.querySelector('.battery-size-select').value, label: v2SheetModel(l).batteryLabel || '' }; }'''
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(700)
        # F4: Auto never picks 12V6A5, sweep small loads through the app
    picks = []
    for n, sb in [(1, 4), (1, 24), (2, 4), (2, 12), (3, 24), (5, 24), (9, 90)]:
      loc = await pg.evaluate(SHEET, [['Standard Display'] + ['Detector'] * (n - 1), True])
      await pg.evaluate("([loc,sb])=>{const l=document.getElementById('location-'+loc); const h=l.querySelector('.standby-hours'); h.value=String(sb); h.dispatchEvent(new Event('input',{bubbles:true})); recalcLocation(loc); recalcLocation(loc);}", [loc, sb])
      i = await pg.evaluate(INFO, loc); picks.append((n, sb, i['batt'], await pg.evaluate("(loc)=>document.getElementById('location-'+loc).querySelector('.auto-battery-mode').value", loc)))
    ok('F4: Auto (app level) never selects 12V6A5 / 7.2 Ah across small→large loads', all(x[3] == 'auto' and x[2] not in ('7.2', '7') for x in picks) and any(x[2] == '10' for x in picks), picks)
    opts72 = await pg.evaluate("(()=>[...document.querySelector('.battery-size-select').options].map(o=>o.value))()")
    ok('F4: 12V6A5 (7.2 Ah) is still offered for a manual pick', '7.2' in opts72, opts72)
        # F8a: two displays in one run is impossible: a display never offers "follow"
    loc = await pg.evaluate(SHEET, [['Standard Display', 'Detector', 'Standard Display', 'Detector'], True])
    i = await pg.evaluate(INFO, loc)
    di = [k for k, t in enumerate(i['types']) if t != 'Detector']
    ok('F8: two displays → each display is its own run entry (no Ribbon Path option on a display)', len(di) == 2 and all(i['power'][k] == 'own' and 'f' not in i['opts'][k] for k in di), i)
    forced = await pg.evaluate("""(loc)=>{ const l=document.getElementById('location-'+loc); const rows=[...l.querySelectorAll('[data-role=module]')]; const d=rows.filter(r=>r.querySelector('.type-select').value!=='Detector');
      const ps=d[1].querySelector('.power-select'); const o=document.createElement('option'); o.value='follow:'+d[0].id; ps.appendChild(o); ps.value=o.value; ps.dispatchEvent(new Event('change',{bubbles:true})); recalcLocation(loc); return d[1].querySelector('.power-select').value; }""", loc)
    ok('F8: forcing display 2 onto display 1’s run is reverted to its own circuit (enforced)', forced == 'own', forced)
    # F8b: display after a detector-started run
    loc = await pg.evaluate(SHEET, [['Detector', 'Detector', 'Detector', 'Standard Display', 'Detector'], True])
    await pg.evaluate("""(loc)=>{ const l=document.getElementById('location-'+loc); const ram=l.querySelector('.ribbon-assign-mode'); if(ram) ram.value='off'; const rows=[...l.querySelectorAll('[data-role=module]')];
      const set=(el,v)=>{ el.value=v; el.dispatchEvent(new Event('change',{bubbles:true})); }; const T=rows.filter(r=>r.querySelector('.type-select').value==='Detector'), D=rows.find(r=>r.querySelector('.type-select').value!=='Detector');
      set(T[0].querySelector('.power-select'),'own'); recalcLocation(loc); [1,2].forEach(k=>set(T[k].querySelector('.power-select'),'follow:'+T[0].id)); set(T[3].querySelector('.power-select'),'follow:'+D.id); recalcLocation(loc); }""", loc)
    i = await pg.evaluate(INFO, loc)
    d = [k for k, t in enumerate(i['types']) if t != 'Detector'][0]; T = [k for k, t in enumerate(i['types']) if t == 'Detector']
    ok('F8: display added after a detector-started run stays its own run (own circuit, no follow option); detector run = T1 + 2 followers', i['power'][d] == 'own' and 'f' not in i['opts'][d] and [i['power'][k] for k in T] == ['own', 'f', 'f', 'f'], i)
    ok('F8: detector-led run of 3 + separate display run → no ribbon-run error', not [x for x in i['flags'] if x.startswith('Ribbon run exceeds')], i['flags'])
    ok('F8: the run entry detector and the display take different AUX circuits', i['aux'][d] and i['aux'][T[0]] and i['aux'][d] != i['aux'][T[0]], i['aux'])
    # F8c: AUX per supply = per sheet; a built-in sheet is always exactly one supply
    a = await pg.evaluate(SHEET, [['Standard Display'] + ['Detector'] * 4, True])
    b2 = await pg.evaluate(SHEET, [['Standard Display'] + ['Detector'] * 4, False])
    for L in (a, b2):
      await pg.evaluate("""(loc)=>{ const l=document.getElementById('location-'+loc); const ram=l.querySelector('.ribbon-assign-mode'); if(ram) ram.value='off'; l.querySelectorAll('[data-role=module] .power-select').forEach(s=>{ s.value='own'; s.dispatchEvent(new Event('change',{bubbles:true})); }); recalcLocation(loc); }""", L)
    ia, ib = await pg.evaluate(INFO, a), await pg.evaluate(INFO, b2)
    ok('F8: each sheet (supply) has its own AUX 1–4; 5th entry on a sheet gets none', sorted(x for x in ia['aux'] if x) == ['1', '2', '3', '4'] and ia['aux'].count('') == 1 and sorted(x for x in ib['aux'] if x) == ['1', '2', '3', '4'], [ia['aux'], ib['aux']])
    big = await pg.evaluate(SHEET, [['Standard Display'] + ['Detector'] * 8, True])
    await pg.evaluate("(loc)=>{const l=document.getElementById('location-'+loc); const h=l.querySelector('.standby-hours'); h.value='90'; h.dispatchEvent(new Event('input',{bubbles:true})); recalcLocation(loc); recalcLocation(loc);}", big)
    ib = await pg.evaluate(INFO, big)
    ok('F8: a built-in sheet needing more than one supply FAILS (never silently becomes 2 supplies sharing AUX 1–4)', ib['status'] == 'fail' and ib['label'] != '' , [ib['status'], ib['label']])
    ok('no page errors', not errs, errs[:3])
    await b.close()
  print(f"{sum(R)}/{len(R)} passed"); sys.exit(0 if all(R) else 1)
asyncio.run(main())
